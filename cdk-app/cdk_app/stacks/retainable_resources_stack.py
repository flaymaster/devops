# create the s3 bucket here
# create ssm parameter here
# create ecr here

from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_s3 as s3
import json
from aws_cdk import Aws
import os


class RetainableStack(Stack):
    def __init__(
            self,
            scope: Construct,
            _id: str,
            ** kwargs) -> None:
        super().__init__(scope, _id, cross_region_references=True, **kwargs)
        self.check_point_bucket = self.create_s3_bucket()
        self.ssm_param = "/elb/token"
        self.version_parameter: ssm.StringParameter = self.create_ssm()

    def create_s3_bucket(self):
        self.s3_bucket = s3.Bucket(
            self,
            "s3-bucket",
            bucket_name=f"s3-checkpoint-{Aws.ACCOUNT_ID}",
        )
        return self.s3_bucket

    def create_ssm(self):
        versions = {'token': os.getenv('SSM_TOKEN')}
        version_parameter = ssm.StringParameter(self,
                                                id='token-param',
                                                parameter_name=self.ssm_param,
                                                string_value=json.dumps(
                                                    versions)
                                                )
        return version_parameter

    # def create_rest_ecr(self):
    #     self.ecr_repo = ecr.Repository(
    #         self,
    #         "execution-runner",
    #         repository_name="execution-runner",
    #     )

    # def create_lambda_ecr(self):
    #     self.ecr_repo = ecr.Repository(
    #         self,
    #         "docker_lambda",
    #         repository_name="docker-lambda",
    #     )
