from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    Duration,
    RemovalPolicy,
)
from constructs import Construct

class AIStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamoDB Table for AI Recommendations
        self.recommendations_table = dynamodb.Table(
            self, "RecommendationsTable",
            table_name="ai-recommendations",
            partition_key=dynamodb.Attribute(
                name="recommendationId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Add GSI for project queries
        self.recommendations_table.add_global_secondary_index(
            index_name="ProjectIndex",
            partition_key=dynamodb.Attribute(
                name="projectId",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Bedrock permissions policy
        bedrock_policy = iam.PolicyStatement(
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            resources=[
                f"arn:aws:bedrock:*::foundation-model/*",
                f"arn:aws:bedrock:*:{self.account}:inference-profile/*"
            ]
        )
        
        # AWS Marketplace permissions for Anthropic models
        marketplace_policy = iam.PolicyStatement(
            actions=[
                "aws-marketplace:ViewSubscriptions",
                "aws-marketplace:Subscribe"
            ],
            resources=["*"]
        )

        # Comprehend permissions
        comprehend_policy = iam.PolicyStatement(
            actions=[
                "comprehend:DetectEntities",
                "comprehend:DetectKeyPhrases",
                "comprehend:DetectSentiment"
            ],
            resources=["*"]
        )

        # Lambda Layer with dependencies
        dependencies_layer = lambda_.LayerVersion(
            self, "DependenciesLayer",
            code=lambda_.Code.from_asset("../../backend/lambda/layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="OpenSearch and AWS dependencies for Lambda functions"
        )

        # RAG Handler Lambda
        self.rag_handler = lambda_.Function(
            self, "RAGHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="rag_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(120),  # Increased to 120 seconds
            memory_size=1024,
            environment={
                "OPENSEARCH_ENDPOINT": storage_stack.opensearch_domain.attr_domain_endpoint,
                "NEPTUNE_ENDPOINT": storage_stack.neptune_cluster.cluster_endpoint.hostname
            }
        )

        self.rag_handler.add_to_role_policy(bedrock_policy)
        self.rag_handler.add_to_role_policy(marketplace_policy)
        self.rag_handler.add_to_role_policy(comprehend_policy)

        # Grant OpenSearch access
        self.rag_handler.add_to_role_policy(
            iam.PolicyStatement(
                actions=["es:ESHttpGet", "es:ESHttpPost"],
                resources=[f"{storage_stack.opensearch_domain.attr_arn}/*"]
            )
        )

        # AI Assistant Handler Lambda
        self.ai_assistant_handler = lambda_.Function(
            self, "AIAssistantHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="ai_assistant_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            timeout=Duration.seconds(120),
            memory_size=1024,
            environment={
                "PROJECTS_TABLE": storage_stack.projects_table.table_name,
                "RECOMMENDATIONS_TABLE": self.recommendations_table.table_name
            }
        )

        self.ai_assistant_handler.add_to_role_policy(bedrock_policy)
        self.ai_assistant_handler.add_to_role_policy(marketplace_policy)
        self.ai_assistant_handler.add_to_role_policy(comprehend_policy)
        
        # Grant DynamoDB access
        storage_stack.projects_table.grant_read_data(self.ai_assistant_handler)
        self.recommendations_table.grant_read_write_data(self.ai_assistant_handler)
