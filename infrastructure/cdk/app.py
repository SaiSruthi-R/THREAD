#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.storage_stack import StorageStack
from stacks.ingestion_stack import IngestionStack
from stacks.ai_stack import AIStack
from stacks.api_stack import APIStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1"
)

# Storage Layer
storage_stack = StorageStack(app, "MemoryMappingStorageStack", env=env)

# Ingestion Layer
ingestion_stack = IngestionStack(
    app, "MemoryMappingIngestionStack",
    storage_stack=storage_stack,
    env=env
)

# AI/RAG Layer
ai_stack = AIStack(
    app, "MemoryMappingAIStack",
    storage_stack=storage_stack,
    env=env
)

# API Layer
api_stack = APIStack(
    app, "MemoryMappingAPIStack",
    storage_stack=storage_stack,
    ai_stack=ai_stack,
    ingestion_stack=ingestion_stack,
    env=env
)

# Frontend Layer
frontend_stack = FrontendStack(
    app, "MemoryMappingFrontendStack",
    env=env
)

app.synth()
