

from runway_config_schematic import ModuleDefinition, DeploymentDefinition

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
