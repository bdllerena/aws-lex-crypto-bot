from constructs import Construct
import os
import subprocess
from typing import List
from aws_cdk import (
    Duration,
    Stack,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_lambda as _lambda,
)


class CbotStack(Stack):
    def create_dependencies_layer(
        self, requirements_path: str, output_dir: str
    ) -> _lambda.LayerVersion:
        if not os.environ.get("SKIP_PIP"):
            subprocess.check_call(
                f"pip install -r {requirements_path} -t {output_dir}/python".split()
            )
        return _lambda.LayerVersion(
            self, "HandlerDependencies", code=_lambda.Code.from_asset(output_dir)
        )

    def create_handler(
        self,
        layers: List[_lambda.LayerVersion],
    ):

        crypto_search_lambda = _lambda.Function(
            self,
            "CryptoSearchHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="cbot_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=layers,
            function_name="cb-search-crypto-dev",
        )

        coinmarket_api_param = ssm.StringParameter.from_string_parameter_attributes(
            self, "Parameter", parameter_name="/dev/crypto-bot/COIN_MARKETCAP_API_KEY"
        )
        coinmarket_api_param.grant_read(crypto_search_lambda)

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        requirements_path: str = "./requirements.txt",
        layer_dir: str = "./.layer",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dependenciesLayer = self.create_dependencies_layer(
            requirements_path=requirements_path, output_dir=layer_dir
        )

        self.create_handler(
            layers=[dependenciesLayer],
        )
