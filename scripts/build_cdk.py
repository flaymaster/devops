from aws_cdk import (
    App
)
from cdk_app.app import RestApp


def create_cyclarity_hub_app():
    print("Synth RestApp...")
    stage_name = "Devops-RestApp"
    rest_app = App(outdir="../cdk.out")
    RestApp(app=rest_app, stage_name=stage_name)
    rest_app.synth()


if __name__ == "__main__":
    create_cyclarity_hub_app()
