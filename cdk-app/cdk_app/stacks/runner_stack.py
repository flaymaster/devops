# create ecs here
# create elb here
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_sqs as sqs
from aws_cdk import Duration
from aws_cdk import Aws
from aws_cdk import aws_lambda
import os
from cdk_app.stacks.retainable_resources_stack import RetainableStack


class ExecutionRunnerStack(Stack):  # Fixed typo in class name
    def __init__(self,
                 scope: Construct,
                 _id: str,
                 retainable_stack: RetainableStack,
                 ** kwargs) -> None:
        super().__init__(scope, _id, **kwargs)
        self.retainable_stack = retainable_stack
        self.vpc = self.create_vpc(
            cidr_block="10.90.0.0/16")
        self.rest_docker_tag = os.environ.get("REST_DOCKER_TAG", "latest")
        self.lambda_docker_tag = os.environ.get("LAMBDA_DOCKER_TAG", "latest")
        self.create_sqs()
        self.create_execution_runner()
        self.create_rest_load_balancer()
        self.create_docker_lambda()

    def create_vpc(self, cidr_block):
        # Create VPC with proper subnet configuration
        self.vpc = ec2.Vpc(
            self, "MYVPC",
            ip_addresses=ec2.IpAddresses.cidr(cidr_block),
        )
        return self.vpc

    def create_rest_load_balancer(self):
        """Create basic ALB called rest-load-balancer"""
        if not self.vpc:
            raise ValueError("VPC must be created before ALB")
        # Create the Application Load Balancer
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "RestLoadBalancer",
            load_balancer_name="rest-load-balancer",
            vpc=self.vpc,
            internet_facing=True,  # This makes it accessible from internet
        )
        listener = self.alb.add_listener(
            "Listener",
            port=80,
            open=True
        )
        listener.add_targets(
            "ECS",
            port=80,
            targets=[self.ecs_service]
        )
        return self.alb

    def create_execution_runner(self):
        name = "execution-runner"
        if not self.vpc:
            raise ValueError("VPC must be created before ECS cluster")

        self.ecs_cluster = ecs.Cluster(
            self,
            f'{name}-cluster',
            cluster_name=f'{name}',
            vpc=self.vpc,
            container_insights=True
        )
        task_role = iam.Role(
            self,
            f'{name}-task-role',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            inline_policies={
                "ssm_and_logs_access": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "ssm:GetParameter"
                            ],
                            resources=[
                                "arn:aws:ssm:us-east-1:472765722896:parameter/elb/token"
                            ]
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:CreateLogGroup"
                            ],
                            resources=[
                                "*"
                            ]
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "sqs:sendmessage"
                            ],
                            resources=[
                                "arn:aws:sqs:us-east-1:472765722896:bucket-queue"
                            ]
                        )
                    ]
                )
            }
        )
        runner_task_definition = ecs.FargateTaskDefinition(
            self,
            f'{name}-task-definition',
            cpu=1024,
            memory_limit_mib=3072,
            family=f'{name}',
            task_role=task_role,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX
            )
        )

        container = runner_task_definition.add_container(
            f'{name}-container',
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr.Repository.from_repository_attributes(
                    self,
                    f'{name}-repo',
                    repository_arn=(
                        f'arn:aws:ecr:{Aws.REGION}:{Aws.ACCOUNT_ID}:'
                        'repository/rest-docker'
                    ),  # noqa
                    repository_name='rest-docker'
                ),
                tag=self.rest_docker_tag,
            ),
            environment={
                'TOKEN_PARAM_NAME': '/elb/token',
                'SQS_QUEUE_URL': self.check_point_queue.queue_url
            },
            logging=ecs.LogDriver.aws_logs(
                stream_prefix='execution-runner-logs',
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                log_retention=logs.RetentionDays.ONE_MONTH
            )
        )
        container.add_port_mappings(
            # or whatever port your app listens on
            ecs.PortMapping(container_port=80)
        )

        self.ecs_service = ecs.FargateService(
            self,
            "MyService",
            cluster=self.ecs_cluster,
            task_definition=runner_task_definition,
            desired_count=1,
            assign_public_ip=True,
        )

    def create_sqs(self):
        self.check_point_queue = sqs.Queue(
            self,
            "bucket-queue",
            queue_name="bucket-queue",
            encryption=sqs.QueueEncryption.KMS_MANAGED,
            retention_period=Duration.seconds(120),
            visibility_timeout=Duration.seconds(900)
        )
        return self.check_point_queue

    def create_docker_lambda(self):
        # specific docker tag from env variable
        self.docker_lambda = aws_lambda.DockerImageFunction(
            self,
            "DockerLambda",
            function_name="docker-lambda",
            code=aws_lambda.DockerImageCode.from_ecr(
                repository=ecr.Repository.from_repository_attributes(
                    self,
                    "docker-lambda-repo",
                    repository_arn=(
                        f"arn:aws:ecr:{Aws.REGION}:{Aws.ACCOUNT_ID}:"
                        "repository/queue-docker"
                    ),
                    repository_name="queue-docker"
                ),
                tag=self.lambda_docker_tag
            ),
            timeout=Duration.seconds(60),
            environment={
                'S3_BUCKET_NAME': self.retainable_stack.check_point_bucket.bucket_name,
            }
        )
        self.docker_lambda.add_event_source_mapping(
            "Pdf_report_trigger_lambda",
            event_source_arn=self.check_point_queue.queue_arn,
            batch_size=1
        )
        # Grant Lambda permissions to consume messages from the SQS queue
        self.check_point_queue.grant_consume_messages(self.docker_lambda)
