# create the s3 bucket here
# create ssm parameter here
# create ecr here

from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ecr as ecr
import json


class RetainableStack(Stack):
    def __init__(
            self,
            scope: Construct,
            _id: str,
            ** kwargs) -> None:
        super().__init__(scope, _id, cross_region_references=True, **kwargs)
        self.create_ecr()
        self.create_s3_bucket()
        self.ssm_param = "/elb/token"
        self.version_parameter: ssm.StringParameter = self.create_ssm()

    def create_s3_bucket(self):
        self.s3_bucket = s3.Bucket(
            self,
            "s3-bucket",
            bucket_name="s3-bucket",
        )

    def create_ssm(self):
        versions = {'token': '@YMRCSdc4hPaj&qY'}
        version_parameter = ssm.StringParameter(self,
                                                id='token-param',
                                                parameter_name=self.ssm_param,
                                                string_value=json.dumps(
                                                    versions)
                                                )
        return version_parameter

    def create_ecr(self):
        self.ecr_repo = ecr.Repository(
            self,
            "docker-repo",
            repository_name="ecr-repo",
        )
