"""Use the hash of a module folder to decide if there are changes to be deployed."""

import logging

from .staticsite.util import get_hash_of_files

LOGGER = logging.getLogger(__name__)


class SourceHashTracking(object):
    """Store the results of hashing a folder."""

    def __init__(self, ssm_client, namespace, environment_name, path):
        """Create an instance."""
        self._ssm_client = ssm_client
        self._path = path
        self._ssm_key = "%s-%s-hash" % (namespace, environment_name)

    def have_the_files_changed(self, source_hashing_directories):
        """Check if anything has changed."""
        hash_string = get_hash_of_files(
            root_path=self._path,
            directories=source_hashing_directories
        )

        result = True

        # Now determine if the current module has already been deployed
        try:
            previous_hash_string = self.ssm_client.get_parameter(Name=self._ssm_key)['Parameter']['Value']
            if previous_hash_string != hash_string:
                LOGGER.debug("previous deployment found in SSM: %s", previous_hash_string)
                LOGGER.info("these files have changed since the deployment. proceeding.")
            else:
                LOGGER.info("skipping build; these files have already deployed")
                result = False
        except self.ssm_client.exceptions.ParameterNotFound:
            LOGGER.info("no previous deployment found in SSM")

        # if previous_hash_string:
        #     context_dict['old_archive_filename'] = \
        #         artifact_key_prefix + previous_hash_string + '.zip'

        return result, hash_string

    def store_hash_of_deployed_files(self, hash_string):
        """Record a hash in SSM for next time."""
        LOGGER.info("updating deployment in SSM: %s", hash_string)

        self._ssm_client.put_parameter(
            Name=self._ssm_key,
            Description='Hash of currently deployed static website source',
            Value=hash_string,
            Type='String',
            Overwrite=True
        )

    def cleanup(self):
        try:
            self._ssm_client.delete_parameter(Name=self._ssm_key)
            LOGGER.info("deployment removed from SSM")
        except self._ssm_client.exceptions.ParameterNotFound:
            LOGGER.info("deployment seems to have already been deleted from SSM")
