from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_cognito as cognito,
    Duration,
    CfnOutput,
)
from constructs import Construct

class APIStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack, ai_stack, ingestion_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Cognito User Pool for authentication
        user_pool = cognito.UserPool(
            self, "MemoryMappingUserPool",
            user_pool_name="memory-mapping-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True
            )
        )

        # Projects Handler
        projects_handler = lambda_.Function(
            self, "ProjectsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="projects_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            timeout=Duration.seconds(30),
            environment={
                "PROJECTS_TABLE": storage_stack.projects_table.table_name
            }
        )
        storage_stack.projects_table.grant_read_write_data(projects_handler)

        # File Upload Handler
        file_upload_handler = lambda_.Function(
            self, "FileUploadHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="file_upload_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "DOCUMENTS_BUCKET": storage_stack.documents_bucket.bucket_name,
                "METADATA_TABLE": storage_stack.metadata_table.table_name
            }
        )
        storage_stack.documents_bucket.grant_read_write(file_upload_handler)
        storage_stack.metadata_table.grant_read_write_data(file_upload_handler)

        # Decisions Handler
        decisions_handler = lambda_.Function(
            self, "DecisionsHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="decisions_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            timeout=Duration.seconds(30),
            environment={
                "DECISIONS_TABLE": storage_stack.decisions_table.table_name
            }
        )
        storage_stack.decisions_table.grant_read_write_data(decisions_handler)

        # Graph Handler
        graph_handler = lambda_.Function(
            self, "GraphHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="graph_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            timeout=Duration.seconds(30),
            environment={
                "NEPTUNE_ENDPOINT": storage_stack.neptune_cluster.cluster_endpoint.hostname,
                "NEPTUNE_PORT": "8182"
            }
        )

        # API Gateway
        api = apigw.RestApi(
            self, "MemoryMappingAPI",
            rest_api_name="Memory Mapping API",
            description="API for Memory Mapping contextual knowledge system",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )

        # API Resources and Methods
        # /query - RAG queries
        query_resource = api.root.add_resource("query")
        query_resource.add_method(
            "POST",
            apigw.LambdaIntegration(ai_stack.rag_handler)
        )

        # /projects
        projects_resource = api.root.add_resource("projects")
        projects_resource.add_method(
            "GET",
            apigw.LambdaIntegration(projects_handler)
        )
        projects_resource.add_method(
            "POST",
            apigw.LambdaIntegration(projects_handler)
        )

        # /projects/{id}
        project_resource = projects_resource.add_resource("{id}")
        project_resource.add_method(
            "GET",
            apigw.LambdaIntegration(projects_handler)
        )
        project_resource.add_method(
            "PUT",
            apigw.LambdaIntegration(projects_handler)
        )
        project_resource.add_method(
            "DELETE",
            apigw.LambdaIntegration(projects_handler)
        )

        # /decisions
        decisions_resource = api.root.add_resource("decisions")
        decisions_resource.add_method(
            "GET",
            apigw.LambdaIntegration(decisions_handler)
        )

        # /graph
        graph_resource = api.root.add_resource("graph")
        graph_resource.add_method(
            "POST",
            apigw.LambdaIntegration(graph_handler)
        )

        # /ingest
        ingest_resource = api.root.add_resource("ingest")
        ingest_resource.add_method(
            "POST",
            apigw.LambdaIntegration(ingestion_stack.ingestion_handler)
        )

        # /ai-assistant
        ai_assistant_resource = api.root.add_resource("ai-assistant")
        ai_assistant_resource.add_method(
            "POST",
            apigw.LambdaIntegration(ai_stack.ai_assistant_handler)
        )

        # /files - File upload and management
        files_resource = api.root.add_resource("files")
        files_resource.add_method(
            "POST",
            apigw.LambdaIntegration(file_upload_handler)
        )
        files_resource.add_method(
            "GET",
            apigw.LambdaIntegration(file_upload_handler)
        )

        # /files/project/{projectId} - List files for a project
        files_project_resource = files_resource.add_resource("project")
        files_project_id_resource = files_project_resource.add_resource("{projectId}")
        files_project_id_resource.add_method(
            "GET",
            apigw.LambdaIntegration(file_upload_handler)
        )

        # /files/{fileId} - Delete file
        file_resource = files_resource.add_resource("{fileId}")
        file_resource.add_method(
            "DELETE",
            apigw.LambdaIntegration(file_upload_handler)
        )

        # Outputs
        CfnOutput(self, "APIEndpoint", value=api.url)
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
