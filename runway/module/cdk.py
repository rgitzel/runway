"""CDK module."""

import logging
import os
import subprocess
import sys

import boto3
import six

from . import (
    RunwayModule, format_npm_command_for_logging, generate_node_command,
    run_module_command, run_npm_install
)
from ..util import change_dir, run_commands, which

LOGGER = logging.getLogger('runway')


def cdk_module_matches_env(env_name, env_config, env_vars):
    """Return bool on whether cdk command should continue in current env."""
    if env_config.get(env_name):
        current_env_config = env_config[env_name]
        if isinstance(current_env_config, type(True)) and current_env_config:
            return True
        if isinstance(current_env_config, six.string_types):
            (account_id, region) = current_env_config.split('/')
            if region == env_vars['AWS_DEFAULT_REGION']:
                boto_args = {}
                for i in ['aws_access_key_id', 'aws_secret_access_key',
                          'aws_session_token']:
                    if env_vars.get(i.upper()):
                        boto_args[i] = env_vars[i.upper()]
                sts_client = boto3.client(
                    'sts',
                    region_name=env_vars['AWS_DEFAULT_REGION'],
                    **boto_args
                )
                if sts_client.get_caller_identity()['Account'] == account_id:
                    return True
    return False


def get_cdk_stacks(module_path, env_vars):
    """Return list of CDK stacks."""
    LOGGER.debug('Listing stacks in the CDK app prior to '
                 'diff')
    return subprocess.check_output(
        generate_node_command(
            command='cdk',
            command_opts=['list'],
            path=module_path),
        env=env_vars
    ).strip().split('\n')


class CloudDevelopmentKit(RunwayModule):
    """CDK Runway Module."""

    def run_cdk(self, command='deploy'):
        """Run CDK."""
        response = {'skipped_configs': False}
        cdk_opts = [command]

        if not which('npm'):
            LOGGER.error('"npm" not found in path or is not executable; '
                         'please ensure it is installed correctly.')
            sys.exit(1)

        if 'DEBUG' in self.context.env_vars:
            cdk_opts.append('-v')  # Increase logging if requested

        if cdk_module_matches_env(self.context.env_name,
                                  self.options.get('environments', {}),
                                  self.context.env_vars):
            if self.folder.isfile('package.json'):
                with change_dir(self.path):
                    run_npm_install(self.path, self.options, self.context)
                    if self.options.get('options', {}).get('build_steps',
                                                           []):
                        LOGGER.info("Running build steps for %s...",
                                    os.path.basename(self.path))
                        run_commands(
                            commands=self.options.get('options',
                                                      {}).get('build_steps',
                                                              []),
                            directory=self.path,
                            env=self.context.env_vars
                        )
                    if command == 'diff':
                        LOGGER.info("Running cdk %s on each stack in %s",
                                    command,
                                    os.path.basename(self.path))
                        for i in get_cdk_stacks(self.path,
                                                self.context.env_vars):
                            subprocess.call(
                                generate_node_command(
                                    'cdk',
                                    cdk_opts + [i],  # 'diff <stack>'
                                    self.path
                                ),
                                env=self.context.env_vars
                            )
                    else:
                        if command == 'deploy':
                            bootstrap_command = generate_node_command(
                                'cdk',
                                ['bootstrap'],
                                self.path
                            )
                            LOGGER.info('Running cdk bootstrap...')
                            run_module_command(cmd_list=bootstrap_command,
                                               env_vars=self.context.env_vars)
                        elif command == 'destroy' and 'CI' in self.context.env_vars:  # noqa
                            cdk_opts.append('-f')  # Don't prompt
                        cdk_command = generate_node_command(
                            'cdk',
                            cdk_opts,
                            self.path
                        )
                        LOGGER.info("Running cdk %s on %s (\"%s\")",
                                    command,
                                    os.path.basename(self.path),
                                    format_npm_command_for_logging(cdk_command))  # noqa
                        run_module_command(cmd_list=cdk_command,
                                           env_vars=self.context.env_vars)
            else:
                LOGGER.info(
                    "Skipping cdk %s of %s; no \"package.json\" "
                    "file was found (need a package file specifying "
                    "aws-cdk in devDependencies)",
                    command,
                    os.path.basename(self.path))
        else:
            LOGGER.info(
                "Skipping cdk %s of %s; no config for "
                "this environment found or current account/region does not "
                "match configured environment",
                command,
                os.path.basename(self.path))
            response['skipped_configs'] = True
        return response

    def plan(self):
        """Run cdk diff."""
        self.run_cdk(command='diff')

    def deploy(self):
        """Run cdk deploy."""
        self.run_cdk(command='deploy')

    def destroy(self):
        """Run cdk destroy."""
        self.run_cdk(command='destroy')
