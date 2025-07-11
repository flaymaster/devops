from aws_cdk import App, Stage
import os
from cdk_app.stacks.runner_stack import ExecutionRunnerStack
from cdk_app.stacks.retainable_resources_stack import RetainableStack


class RestApp(Stage):
    def __init__(self,
                 app: App,
                 stage_name: str):

        super().__init__(app, stage_name, env={
            'region': os.getenv('CDK_DEFAULT_REGION')})
        RetainableStack(self, "retainable-stack")
        ExecutionRunnerStack(
            self, "execute-runner-stack")
