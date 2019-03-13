.. _module-configurations:

Module Configurations
=====================
CloudFormation
^^^^^^^^^^^^^^
CloudFormation modules are managed by 2 files: 

- a key/value environment file 
- a yaml file defining the stacks/templates/params.

Environment - name these files in the form of ``ENV-REGION.env`` (e.g. ``dev-us-east-1.env``) or ``ENV.env`` (e.g. ``dev.env``) and
place them in the module root or in its ``env`` folder::

    # Namespace is used as each stack's prefix
    # We recommend an (org/customer)/environment delineation
    namespace: contoso-dev
    environment: dev
    customer: contoso
    region: us-west-2
    # The stacker bucket is the S3 bucket (automatically created) where templates
    # are uploaded for deployment (a CloudFormation requirement for large templates)
    stacker_bucket_name: stacker-contoso-us-west-2

Stack config - these can have any name ending in .yaml (they will be evaluated in alphabetical order)::

    # Note namespace/stacker_bucket_name being substituted from the environment
    namespace: ${namespace}
    stacker_bucket: ${stacker_bucket_name}

    stacks:
      myvpcstack:  # will be deployed as contoso-dev-myvpcstack
        template_path: templates/vpc.yaml
        # The enabled option is optional and defaults to true. You can use it to
        # enable/disable stacks per-environment (i.e. like the namespace
        # substitution above, but with the value of either true or false for the
        # enabled option here)
        enabled: true
      myvpcendpoint:
        template_path: templates/vpcendpoint.yaml
        # variables map directly to CFN parameters; here used to supply the
        # VpcId output from the myvpcstack to the VpcId parameter of this stack
        variables:
          VpcId: ${output myvpcstack::VpcId}

The config yaml supports many more features; see the full Stacker documentation for more detail 
(e.g. stack configuration options, additional lookups in addition to output (e.g. SSM, DynamoDB))

| **Environment Values Via Runway Deployment/Module Options**
| In addition or in place of the environment file(s), environment values can be provided via deployment and module options.

**Top-level Runway Config**
::

    ---

    deployments:
      - modules:
          - path: mycfnstacks
            environments:
              dev:
                namespace: contoso-dev
                foo: bar

and/or

::

    ---

    deployments:
      - environments:
          dev:
            namespace: contoso-dev
            foo: bar
        modules:
          - mycfnstacks

**In Module Directory**
::

    ---
    environments:
      dev:
        namespace: contoso-dev
        foo: bar

(in ``runway.module.yaml``)

Terraform
^^^^^^^^^
Standard Terraform rules apply, with the following recommendations/caveats:

- Each environment requires its own tfvars file, in the form of ENV-REGION.tfvars (e.g. dev-contoso.tfvars).
- We recommend (but do not require) having a backend configuration separate from the terraform module code:

main.tf:
::

    terraform {
      backend "s3" {
        key = "some_unique_identifier_for_my_module" # e.g. contosovpc
      }
    }
    # continue with code here...


backend-REGION.tfvars, or backend-ENV-REGION.tfvars, or backend-ENV.tfvars (e.g. backend-us-east-1.tfvars):
::

    bucket = "SOMEBUCKNAME"
    region = "SOMEREGION"
    dynamodb_table = "SOMETABLENAME"

| **tfenv**
| If a ``.terraform-version`` file is placed in the module (this is recommended), tfenv_ will be invoked to ensure the appropriate version is installed prior to module deployment.

| **Environment Values Via Runway Deployment/Module Options**
| In addition or in place of the variable file(s), variable values can be provided via deployment and module options.

**Top-level Runway Config**
::

    ---

    deployments:
      - modules:
          - path: mytfmodule
            environments:
              dev:
                foo: bar

and/or
::

    ---

    deployments:
      - environments:
          dev:
            foo: bar
        modules:
          - mytfmodule

**In Module Directory**
::

    ---
    environments:
      dev:
        namespace: contoso-dev
        foo: bar

(in ``runway.module.yaml``)

| **Backend Values Via Runway Deployment/Module Options**
| Terraform backend options can be specified in the runway config yaml via deployment and module options.

**Top-level Runway Config**
::

    ---

    deployments:
      - modules:
          - path: mytfmodule
            options:
              terraform_backend_config:
                bucket: mybucket
                region: us-east-1
                dynamodb_table: mytable

and/or
::

    ---

    deployments:
      - modules:
          - path: mytfmodule
          - path: anothermytfmodule
        module_options:  # shared between all modules in deployment
          terraform_backend_config:
            bucket: mybucket
            region: us-east-1
            dynamodb_table: mytable

**In Module Directory**
::

    ---
    options:
      terraform_backend_config:
        bucket: mybucket
        region: us-east-1
        dynamodb_table: mytable

(in ``runway.module.yaml``)

.. _tfenv: https://github.com/kamatama41/tfenv

Serverless
^^^^^^^^^^
Standard `Serverless
<https://serverless.com/framework/>`_ rules apply, with the following
recommendations/caveats:

- The Cloudformation stack will be named
- By default the Runway deploy environment is used as the Serverless stage name.
-- You can override this in the environment config, below. This is useful when
   you want to give the Runway module a more descriptive name, perhaps to distinguish
   between AWS accounts.
- A ``package.json`` file is required, specifying the serverless dependency, e.g.:

::

    {
      "name": "mymodulename",
      "version": "1.0.0",
      "description": "My serverless module",
      "main": "handler.py",
      "devDependencies": {
        "serverless": "^1.25.0"
      },
      "author": "Serverless Devs",
      "license": "ISC"
    }

- We strongly recommend you commit the package-lock.json that is generated
  after running `npm install`

Environment - name these (possibly empty) files in the form of ``ENV-REGION.yml`` (e.g. ``dev-us-east-1.yml``) or ``ENV.yml`` (e.g. ``dev.yml``) and
place them in the module root or in its ``env`` folder::

    # this is optional
    stage: dev


| **Enabling Environments Via Runway Deployment/Module Options**
| Environments can be specified via deployment and module options in lieu of
| variable files.

**Top-level Runway Config**
::

    ---

    deployments:
      - modules:
          - path: myslsmodule
            environments:
              dev-sandbox:
                stage: dev
              prod:

and/or
::

    ---

    deployments:
      - environments:
          dev:
          prod:
        modules:
          - myslsmodule

**In Module Directory**
::

    ---
    environments:
      dev:
      prod:

(in ``runway.module.yaml``)

CDK
^^^
Standard `AWS CDK
<https://awslabs.github.io/aws-cdk/>`_ rules apply, with the following recommendations/caveats:

A ``package.json`` file is required, specifying the aws-cdk dependency. E.g.::

    {
      "name": "mymodulename",
      "version": "1.0.0",
      "description": "My CDK module",
      "main": "index.js",
      "dependencies": {
        "@aws-cdk/cdk": "^0.9.2",
        "@types/node": "^10.10.1"
      },
      "devDependencies": {
        "aws-cdk": "^0.9.2",
        "typescript": "^3.0.3"
      }
      "author": "My Org",
      "license": "Apache-2.0"
    }

We strongly recommend you commit the package-lock.json that is generated after running ``npm install``

**Build Steps**
Build steps (e.g. for compiling TypeScript) can be specified in the module options. These steps will be run before each diff, deploy, or destroy.
::

    deployments:
      - modules:
          - path: mycdkmodule
            environments:
              dev: true
            options:
              build_steps:
                - npx tsc

**Environment Configs**
Environments can be specified via deployment and/or module options. Each example below shows the explicit CDK ``ACCOUNT/REGION`` environment mapping; 
these can be alternately be specified with a simple boolean (e.g. ``dev: true``).

**Top-level Runway Config**
::

    ---

    deployments:
      - modules:
          - path: mycdkmodule
            environments:
              dev: 987654321098/us-west-2
              prod: 123456789012/us-west-2

and/or:
::

    ---

    deployments:
      - environments:
          dev: 987654321098/us-west-2
          prod: 123456789012/us-west-2
        modules:
          - mycdkmodule

**In Module Directory**
::

    ---
    environments:
      dev: 987654321098/us-west-2
      prod: 123456789012/us-west-2

(in ``runway.module.yaml``)

Static Site
^^^^^^^^^^^

This module type performs idempotent deployments of static websites. It
combines CloudFormation stacks (for S3 buckets & CloudFront Distribution) with
additional logic to build & sync the sites.

It can be used with a configuration like the following::

    deployments:
      - modules:
          - path: web
            class_path: runway.module.staticsite.StaticSite
            environments:
              dev:
                namespace: contoso-dev
                staticsite_aliases: web.example.com,foo.web.example.com
                staticsite_acmcert_arn: arn:aws:acm:us-east-1:123456789012:certificate/...
            options:
              build_steps:
                - npm ci
                - npm run build
              build_output: dist
        regions:
          - us-west-2

This will build the website in ``web`` via the specified build_steps and then upload the contents of ``web/dist``
to a S3 bucket created in the CloudFormation stack ``web-dev-conduit``. On subsequent deploys, the website will
be built and synced only if the (non-git-ignored) files in ``web`` change.

The site domain name is available via the ``CFDistributionDomainName`` output of the ``<namespace>-<path>`` stack
(e.g. ``contoso-dev-web`` above) and will be displayed on stack creation/updates.

A number of `additional options are available <staticsite_config.html>`_. A start-to-finish example walkthrough
is available `in the Conduit quickstart <quickstart.html#conduit-serverless-cloudfront>`_.
