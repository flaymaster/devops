# create sqs here
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_sqs as sqs
from aws_cdk import Duration


class WebStack(Stack):
    def __init__(self, scope: Construct, _id: str, ** kwargs) -> None:
        super().__init__(scope, _id, cross_region_references=True, **kwargs)
        self.create_sqs()

    def create_sqs(self):
        self.pdf_report_queue = sqs.Queue(
            self,
            "bucket-queue",
            queue_name="bucket-queue",
            encryption=sqs.QueueEncryption.KMS_MANAGED,
            retention_period=Duration.seconds(120),
            visibility_timeout=Duration.seconds(900)
        )
