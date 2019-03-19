
import sys
import yaml

from module_config import RunwayConfig

def main():
    troy1 = """
deployments:
  - modules:
      - server.sls
    regions:
      - us-east-1
    account-id:
      dev: TBD
      prod: "363639951452"
  - modules:
      - update_public_template.cfn
    regions:
      - us-east-1
    assume-role:
      prod: arn:aws:iam::1234567890123:role/bucket-access-role-Role-XXXXXXXXXX"""

    troy2 = """
deployments:
  - modules:
      - name: web
        path: ./
        class_path: runway.module.staticsite.StaticSite
        environments:
          prod:
            namespace: onica-sso-prod
            staticsite_aliases: sso.onica.com
            staticsite_acmcert_arn: arn:aws:acm:us-east-1:363639951452:certificate/085adb33-5b85-4962-b7f7-df328985792d
        options:
          build_steps:
            - npm install
            - npm run build
          build_output: dist/onica-sso-web
    account-id:
          prod: 363639951452
    regions:
      - us-east-1    
    """

    troy3 = """
deployments:
  - module_options:
      build_steps:
        - npm install
        - npm run build
      build_output: dist/onica-sso-web
    modules:
      - name: web
        path: ./
        class_path: runway.module.staticsite.StaticSite
        environments:
          prod:
            namespace: onica-sso-prod
            staticsite_aliases: sso.onica.com
            staticsite_acmcert_arn: arn:aws:acm:us-east-1:363639951452:certificate/085adb33-5b85-4962-b7f7-df328985792d
    account-id:
      prod: 363639951452
    regions:
      - us-east-1"""


    for y in [troy1, troy2, troy3]:
        try:
            RunwayConfig(yaml.load(y)).validate()
            print("ok!")
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    main()
