#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from aws_cdk import core

from ittest.ittest_stack import IttestStack


app = core.App()
IttestStack(app, "IttestStack", env = {"region" : "us-east-2"})

app.synth()
