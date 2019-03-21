"""Configuration taken from the runway.yml file."""

# pylint: disable = too-many-instance-attributes


class ModuleConfig(object):
    """Configuration taken from the runway.yml file."""

    # this is called from ModulesCommand.run()
    def __init__(self, environment_name, deployment_environments, module_environments,  # noqa pylint: disable=too-many-arguments
                 skip_npm_ci, build_steps, namespace, class_path):
        """Initialize from runway.yml contents."""
        self._environment_name = environment_name

        self._environment_from_deployment, self._shared_environment_from_deployment = \
            _extract(environment_name, deployment_environments)

        self._environment_from_module, self._shared_environment_from_module = \
            _extract(environment_name, module_environments)

        self.skip_npm_ci = skip_npm_ci

        self.class_path = class_path

        # the rest of these should be in sub-classes... but loading is an issue

        # CDK and staticsite
        self.build_steps = build_steps

        # Terraform
        self.terraform_backend_config = None

        # static site and CFN
        self.namespace = namespace

        # static site
        self.source_hashing = {}  # ?

    def effective_environment(self):
        """Return the the combination of the various environment configuration values, if any."""
        environment = {}
        if self._shared_environment_from_deployment:
            environment.update(self._shared_environment_from_deployment)
        if self._shared_environment_from_module:
            environment.update(self._shared_environment_from_module)
        if self._environment_from_deployment:
            environment.update(self._environment_from_deployment)
        if self._environment_from_module:
            environment.update(self._environment_from_module)
        return environment

    def environment_specified(self):
        """Return whether or not anything was given for this particular environment."""
        return (self._environment_from_module is not None) or \
               (self._environment_from_deployment is not None)


def _extract(environment_name, environments_node):
    environment = None
    shared = None

    environment = environments_node.get(environment_name)
    if environment:
        # `dev: True` is valid in `runway.yml` but we need it to be a dict
        if environment and isinstance(environment, bool):
            environment = {}

    # we might have some shared values to combine with the values specific to this environment
    shared = environments_node.get("*")

    return (environment, shared)
