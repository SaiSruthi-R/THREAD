from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_lambda_event_sources as lambda_events,
    Duration,
)
from constructs import Construct

class IngestionStack(Stack):
    def __init__(self, scope: Construct, id: str, storage_stack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SQS Queue for ingestion events
        self.ingestion_queue = sqs.Queue(
            self, "IngestionQueue",
            queue_name="memory-ingestion-queue",
            visibility_timeout=Duration.seconds(300),
            retention_period=Duration.days(14)
        )

        # S3 Bucket for raw documents
        self.documents_bucket = s3.Bucket(
            self, "DocumentsBucket",
            bucket_name=f"memory-mapping-documents-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        # Lambda Layer with dependencies
        dependencies_layer = lambda_.LayerVersion(
            self, "DependenciesLayer",
            code=lambda_.Code.from_asset("../../backend/lambda/layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="OpenSearch and AWS dependencies for Lambda functions"
        )

        # Ingestion Lambda
        self.ingestion_handler = lambda_.Function(
            self, "IngestionHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="ingestion_handler.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(300),
            memory_size=512,
            environment={
                "METADATA_TABLE": storage_stack.metadata_table.table_name,
                "OPENSEARCH_ENDPOINT": storage_stack.opensearch_domain.attr_domain_endpoint,
                "GRAPH_UPDATE_QUEUE": self.ingestion_queue.queue_url
            }
        )

        # Grant permissions
        storage_stack.metadata_table.grant_read_write_data(self.ingestion_handler)
        self.ingestion_queue.grant_send_messages(self.ingestion_handler)
        self.documents_bucket.grant_read_write(self.ingestion_handler)

        # Add SQS trigger
        self.ingestion_handler.add_event_source(
            lambda_events.SqsEventSource(self.ingestion_queue, batch_size=10)
        )

        # Graph Update Lambda (processes Neptune updates)
        self.graph_updater = lambda_.Function(
            self, "GraphUpdater",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="graph_updater.lambda_handler",
            code=lambda_.Code.from_asset("../../backend/lambda"),
            timeout=Duration.seconds(60),
            environment={
                "NEPTUNE_ENDPOINT": storage_stack.neptune_cluster.cluster_endpoint.hostname,
                "NEPTUNE_PORT": "8182"
            }
        )
