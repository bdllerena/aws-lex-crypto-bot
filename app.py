#!/usr/bin/env python3

import aws_cdk as cdk

from cbot.cbot_stack import CbotStack


app = cdk.App()
CbotStack(app, "cbot")

app.synth()
