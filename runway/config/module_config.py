
# pylint: disable-all

import re

from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import BooleanType, DictType, ListType, ModelType, StringType


VALID_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2"
]

class RegionType(StringType):
    def validate_region(self, value):
        if not value in VALID_REGIONS:
            raise ValidationError("unrecognized region '%s;" % value)


ModuleEnvironment = DictType(StringType)


class ModuleDefinition(Model):
    path = StringType(required=True)



class DeploymentDefinition(Model):
    env_vars = DictType(ModuleEnvironment, required=False)
    environments = DictType(ModuleEnvironment, required=False)
    modules = ListType(ModelType(ModuleDefinition), required=True, min_size=1)
    regions = ListType(RegionType(), required=True, min_size=1)

    def validate_env_vars(self, data, value):
        _check_environment_names('env_vars', data)
        return value

    def validate_environments(self, data, value):
        _check_environment_names('environments', data)
        return value


ENVIRONMENT_NAME_REGEX = re.compile("^[a-z][a-zA-Z0-9-_]+")


def _check_environment_names(node, data):
    if data.get(node) and isinstance(data.get(node), dict):
        for name in data.get(node).keys():
            if (name != "*" and not bool(ENVIRONMENT_NAME_REGEX.match(name))):
                raise ValidationError("invalid environment name '%s' in '%s'" % (name, node))


class RunwayConfig(Model):
    """Top-level config."""
    deployments = ListType(ModelType(DeploymentDefinition), required=True, min_size=1)
    ignore_git_branch = BooleanType(default=False)



def main():
    """Start here."""
    my_mod = {
        'path': 'foo'

    }

    my_dict = {
        'modules': [
            my_mod
        ],
        'regions': ["us-west-1",
                    "us-west-2"],
        'environments': {
            'dev': {"a": 2},
            'qa': {
                'foo': 3
            }
        },
        'env_vars': {
            'fooBar4345': {},
            '*': {}
        }
    }

    ModuleDefinition(my_mod).validate()

    defn = DeploymentDefinition(my_dict)
    defn.validate()

    print(defn.to_primitive())

    print(defn.regions[1])

if __name__ == "__main__":
    main()
