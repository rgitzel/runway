
# flake8: noqa
# pylint: disable-all

import re
import six

from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import BooleanType, DictType, ListType, LongType, ModelType, StringType, UnionType


VALID_REGIONS = [
    "ap-south-1",

    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",

    "ap-southeast-1",
    "ap-southeast-2",

    "ca-central-1",

    "cn-north-1",

    "cn-northwest-1",

    "eu-north-1",

    "eu-west-1",
    "eu-west-2",
    "eu-west-3",

    "sa-east-1",

    "us-east-1",
    "us-east-2",

    "us-gov-east-1",

    "us-gov-west-1",

    "us-west-1",
    "us-west-2"
]

class RegionType(StringType):
    def validate_region(self, value):
        if not value in VALID_REGIONS:
            raise ValidationError("unrecognized region '%s;" % value)


ModuleEnvironmentConfigType = DictType(StringType)
ModuleOptionsType = UnionType([StringType, ListType(StringType)])

class ModuleDefinition(Model):
    class_path = StringType(required=False)
    environments = DictType(ModuleEnvironmentConfigType, required=False)
    name = StringType(required=False)
    options = DictType(ModuleOptionsType, required=False)
    path = StringType(required=True)


# each item in a deployment's list of modules can be either a string or a dict,
#  which is difficult (if indeed possible) to define in a model... so instead
#  before validation we turn strings into dicts...
class StringOrModuleModelType(ModelType):
    def convert(self, value, context=None):
        if isinstance(value, six.string_types):
            value = { 'path': value }
        return super(StringOrModuleModelType, self).convert(value, context)


class DeploymentDefinition(Model):
    account_alias = DictType(StringType, required=False)
    account_id = DictType(LongType, required=False, serialized_name='account-id')
    assume_role = DictType(StringType, required=False, serialized_name='assume-role')
    env_vars = DictType(ModuleEnvironmentConfigType, required=False)
    modules = ListType(StringOrModuleModelType(ModuleDefinition), required=True, min_size=1)
    module_options = DictType(ModuleOptionsType, required=False)
    regions = ListType(RegionType(), required=True, min_size=1)
    skip_npm_ci = BooleanType(required=False, default=False, serialized_name='skip-npm-ci')

    def validate_account_alias(self, data, value):
        _check_dict_keys_are_valid_environment_names('account_alias', data, False)
        return value

    def validate_account_id(self, data, value):
        _check_dict_keys_are_valid_environment_names('account_id', data, False)
        return value

    def validate_assume_role(self, data, value):
        _check_dict_keys_are_valid_environment_names('assume_role', data, False)
        return value

    def validate_env_vars(self, data, value):
        _check_dict_keys_are_valid_environment_names('env_vars', data, True)
        return value

    def validate_environments(self, data, value):
        _check_dict_keys_are_valid_environment_names('environments', data, True)
        return value


class RunwayConfig(Model):
    """Top-level config."""
    deployments = ListType(ModelType(DeploymentDefinition), required=True, min_size=1)
    ignore_git_branch = BooleanType(default=False)



ENVIRONMENT_NAME_REGEX = re.compile("^[a-z][a-zA-Z0-9-_]+")

def _check_dict_keys_are_valid_environment_names(node_name, data, allow_star):
    node = data.get(node_name) 
    if node and isinstance(node, dict):
        for name in node.keys():
            if not ((allow_star and name == "*") or bool(ENVIRONMENT_NAME_REGEX.match(name))):
                raise ValidationError("invalid environment name '%s' in '%s'" % (name, node_name))


# -----------------------------------------------------------------------------------------

# this is just for quick local testing, will not be in final PR

def main():
    my_mod = {
        'path': 'foo'

    }

    my_dict = {
        'modules': [
            my_mod,
            "foo2"
        ],
        # 'module_options': {
        #   'opt1': {
        #       'o1': 'v1'
        #   },
        #     'opt2': {
        #         'o2': 'v2'
        #     },
        # },
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
