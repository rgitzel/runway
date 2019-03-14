"""Runway context module."""

import os


ENV_VAR_NAMES = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN'
]


class Context(object):
    """Runway execution context."""

    def __init__(self, env_name,  # pylint: disable=too-many-arguments
                 env_region, env_root, env_vars=None, project_name=None):
        """Initialize base class."""
        self.env_name = env_name
        self.env_region = env_region
        self.env_root = env_root
        self.project_name = project_name

        if env_vars is None:
            self.env_vars = os.environ.copy()
        else:
            self.env_vars = env_vars

    def save_existing_iam_env_vars(self):
        """Backup IAM environment variables for later restoration."""
        for i in ENV_VAR_NAMES:
            if i in self.env_vars:
                self.env_vars['OLD_' + i] = self.env_vars[i]

    def restore_existing_iam_env_vars(self):
        """Restore backed up IAM environment variables."""
        for i in ENV_VAR_NAMES:
            if 'OLD_' + i in self.env_vars:
                self.env_vars[i] = self.env_vars['OLD_' + i]
            elif i in self.env_vars:
                self.env_vars.pop(i)
