"""Serverless module."""
from __future__ import print_function

import logging
import re
import subprocess
import sys

from . import RunwayModule, run_module_command, NpmHelper
from ..util import change_dir, which

LOGGER = logging.getLogger('runway')


def run_sls_remove(sls_cmd, env_vars):
    """Run sls remove command."""
    sls_process = subprocess.Popen(sls_cmd,
                                   stdout=subprocess.PIPE,
                                   env=env_vars)
    stdoutdata, _stderrdata = sls_process.communicate()
    sls_return = sls_process.wait()
    print(stdoutdata)
    if sls_return != 0 and (sls_return == 1 and not (
            re.search(r"Stack '.*' does not exist", stdoutdata))):
        sys.exit(sls_return)


class Serverless(RunwayModule):
    """Serverless Runway Module."""

    def gen_sls_config_files(self):
        """Generate possible SLS config files names."""
        names = []
        for ext in ['yml', 'json']:
            # Give preference to explicit stage-region files
            names.append("config-%s-%s.%s"
                         % (self.context.env_name, self.context.env_region, ext))
            names.append("%s-%s.%s"
                         % (self.context.env_name, self.context.env_region, ext))
            # stage name only
            names.append("config-%s.%s" % (self.context.env_name, ext))
            names.append("%s.%s" % (self.context.env_name, ext))
        return names

    def get_sls_config_file(self):
        """Determine Stacker environment file name."""
        return self.loader.locate_env_file(self.gen_sls_config_files())

    def load_sls_config_file(self, name):
        """Load the contents of the file into a dict."""
        try:
            if name.endswith(".yml"):
                return self.loader.load_yaml_file(name)
            return self.loader.load_json_file(name)
        except Exception as ex:    # pylint: disable=broad-except
            LOGGER.error('failed to load configuration file "%s": %s', name, ex)
            sys.exit(1)

    def run_serverless(self, command='deploy'):
        """Run Serverless."""
        response = {'skipped_configs': False}
        sls_opts = [command]

        if not which('npm'):
            LOGGER.error('"npm" not found in path or is not executable; '
                         'please ensure it is installed correctly.')
            sys.exit(1)

        if 'CI' in self.context.env_vars and command != 'remove':
            sls_opts.append('--conceal')  # Hide secrets from serverless output

        if 'DEBUG' in self.context.env_vars:
            sls_opts.append('-v')  # Increase logging if requested

        sls_opts.extend(['-r', self.context.env_region])
        sls_opts.extend(['--stage', self.context.env_name])

        sls_env_file = self.get_sls_config_file()
        sls_env_file_exists = self.path.isfile(sls_env_file)

        npm = NpmHelper(self.name,
                        self.module_options,
                        self.context.env_vars,
                        self.module_folder_name)

        sls_cmd = npm.generate_node_command(command='sls',
                                            command_opts=sls_opts,
                                            path=self.module_folder_name)

        # for now, an environment file merely need exist, we don't read it
        if self.environment_options or sls_env_file_exists:
            if self.path.isfile('package.json'):
                with change_dir(self.module_folder_name):
                    npm.run_npm_install()
                    LOGGER.info("Running sls %s on %s (\"%s\")",
                                command,
                                self.name,
                                npm.format_npm_command_for_logging(sls_cmd))
                    if command == 'remove':
                        # Need to account for exit code 1 on any removals after
                        # the first
                        run_sls_remove(sls_cmd, self.context.env_vars)
                    else:
                        run_module_command(cmd_list=sls_cmd,
                                           env_vars=self.context.env_vars)
            else:
                LOGGER.warning(
                    "Skipping 'serverless %s' for %s; no \"package.json\" "
                    "file was found (need a package file specifying "
                    "serverless in devDependencies)",
                    command,
                    self.name)
        else:
            response['skipped_configs'] = True
            LOGGER.info(
                "Skipping 'serverless %s' for '%s' in %s; "
                "no configuration found for this stage/region.",
                command,
                self.name,
                self.context.env_region)
            LOGGER.info("Looking for one of the following in root or 'env' folder:")
            for config_file in self.gen_sls_config_files():
                LOGGER.info("\t%s", config_file)

        return response

    def plan(self):
        """Skip sls planning."""
        LOGGER.info('Planning not currently supported for Serverless')

    def deploy(self):
        """Run sls deploy."""
        self.run_serverless(command='deploy')

    def destroy(self):
        """Run serverless remove."""
        self.run_serverless(command='remove')
