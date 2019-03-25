"""Use the hash of a module folder to decide if there are changes to be deployed."""

import logging

from .staticsite.util import get_hash_of_files

LOGGER = logging.getLogger(__name__)

# only between these two functions
# 'hash'
# 'hash_tracking_parameter'

# external
# 'artifact_key_prefix'
# 'hash_tracking_disabled'


def have_the_files_changed(session, artifact_key_prefix, path,
                           source_hashing_directories, source_hashing_parameter):
    """Check if anything has changed."""
    context_dict = {}

    context_dict['hash'] = get_hash_of_files(
        root_path=path,
        directories=source_hashing_directories
    )

    # Now determine if the current module has already been deployed
    context_dict['hash_tracking_parameter'] = source_hashing_parameter
    if not source_hashing_parameter:
        context_dict['hash_tracking_parameter'] = "%shash" % artifact_key_prefix

    ssm_client = session.client('ssm')

    try:
        name = context_dict['hash_tracking_parameter']
        old_parameter_value = ssm_client.get_parameter(Name=name)['Parameter']['Value']
        LOGGER.info("previous deployment found in SSM: %s", old_parameter_value)
    except ssm_client.exceptions.ParameterNotFound:
        LOGGER.info("no previous deployment found in SSM")
        old_parameter_value = None

    if old_parameter_value:
        context_dict['old_archive_filename'] = \
            artifact_key_prefix + old_parameter_value + '.zip'

    if old_parameter_value == context_dict['hash']:
        LOGGER.info("staticsite: skipping build; app hash %s already deployed "
                    "in this environment",
                    context_dict['hash'])
        context_dict['deploy_is_current'] = True
        return context_dict
    else:
        LOGGER.info("these files have changed since the deployment. proceeding.")

    return context_dict


def store_hash_of_deployed_files(session, context_dict):
    """Record a hash in SSM for next time."""
    LOGGER.info("staticsite: updating environment SSM parameter %s with hash %s",
                context_dict['hash_tracking_parameter'],  # noqa
                context_dict['hash'])

    ssm_client = session.client('ssm')

    ssm_client.put_parameter(
        Name=context_dict['hash_tracking_parameter'],  # noqa
        Description='Hash of currently deployed static website source',
        Value=context_dict['hash'],
        Type='String',
        Overwrite=True
    )
