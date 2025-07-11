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
from aws_cdk import Aws


class ExecutionRunnerStack(Stack):  # Fixed typo in class name
    def __init__(self,
                 scope: Construct,
                 _id: str,
                 ** kwargs) -> None:
        super().__init__(scope, _id, **kwargs)
        self.subnet_configuration = [
            ec2.SubnetConfiguration(
                name="public",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=24,
            ),
            ec2.SubnetConfiguration(
                name="private",
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=24,
            ),
        ]
        self.vpc = self.create_vpc(
            cidr_block="10.90.0.0/16")

        self.create_rest_load_balancer()
        self.create_execution_runner()

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
        task_role = iam.Role(self, f'{name}-task-role', assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
                             inline_policies={"dynamodb_access": iam.PolicyDocument(statements=[
                                 iam.PolicyStatement(
                                     actions=[
                                         "dynamodb:PutItem",
                                         "dynamodb:UpdateItem",
                                         "dynamodb:GetItem",
                                         "dynamodb:Query",
                                         "dynamodb:Scan"
                                     ],
                                     resources=[
                                         f"arn:aws:dynamodb:{Aws.REGION}:{Aws.ACCOUNT_ID}:table/test-executions-outputs",
                                         f"arn:aws:dynamodb:{Aws.REGION}:{Aws.ACCOUNT_ID}:table/execution-engine-state-db"
                                     ]
                                 )
                             ])})
        runner_task_definition = ecs.FargateTaskDefinition(
            self, f'{name}-task-definition', cpu=1024, memory_limit_mib=3072, family=f'{name}', task_role=task_role,

            runtime_platform=ecs.RuntimePlatform(operating_system_family=ecs.OperatingSystemFamily.LINUX))

        runner_task_definition.add_container(
            f'{name}-container',
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr.Repository.from_repository_arn(
                    self,
                    f'{name}-repo',
                    f'arn:aws:ecr:us-east-1:620318890162:repository/{name}'
                )
            ),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix='execution-runner',
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                log_retention=logs.RetentionDays.ONE_MONTH

            )  # 24 hours timeout for a task definitions
        )

    def create_vpc(self, cidr_block, max_azs=2, nat_gateways=2):
        # Create VPC with proper subnet configuration
        self.vpc = ec2.Vpc(
            self, "MYVPC",
            ip_addresses=ec2.IpAddresses.cidr(cidr_block),
            max_azs=max_azs,
            subnet_configuration=self.subnet_configuration,
            nat_gateways=nat_gateways,
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        self.default_security_group = ec2.SecurityGroup(
            self,
            "Runner_Security_Group",
            vpc=self.vpc,
            allow_all_outbound=True,  # replaces the egress rule for 0.0.0.0/0
            description="Management traffic from env",
            security_group_name="Runner-sg-" + self.vpc.vpc_id
        )
        return self.vpc
