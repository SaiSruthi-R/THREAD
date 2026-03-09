from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_neptune_alpha as neptune,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_sqs as sqs,
    Duration,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct

class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC for Neptune and OpenSearch
        self.vpc = ec2.Vpc(
            self, "MemoryMappingVPC",
            max_azs=2,
            nat_gateways=1
        )

        # DynamoDB Tables
        # Metadata Table
        self.metadata_table = dynamodb.Table(
            self, "MetadataTable",
            table_name="memory-metadata",
            partition_key=dynamodb.Attribute(
                name="entityId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Projects Table
        self.projects_table = dynamodb.Table(
            self, "ProjectsTable",
            table_name="memory-projects",
            partition_key=dynamodb.Attribute(
                name="projectId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Decisions Table
        self.decisions_table = dynamodb.Table(
            self, "DecisionsTable",
            table_name="memory-decisions",
            partition_key=dynamodb.Attribute(
                name="decisionId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Add GSI for project queries
        self.decisions_table.add_global_secondary_index(
            index_name="ProjectIndex",
            partition_key=dynamodb.Attribute(
                name="projectId",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Neptune Cluster (Knowledge Graph)
        neptune_subnet_group = neptune.SubnetGroup(
            self, "NeptuneSubnetGroup",
            vpc=self.vpc,
            description="Subnet group for Neptune cluster",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        self.neptune_cluster = neptune.DatabaseCluster(
            self, "NeptuneCluster",
            vpc=self.vpc,
            instance_type=neptune.InstanceType.T3_MEDIUM,
            removal_policy=RemovalPolicy.DESTROY,
            subnet_group=neptune_subnet_group
        )

        # OpenSearch Domain (Vector DB) - Using CfnDomain for more control
        self.opensearch_domain = opensearch.CfnDomain(
            self, "OpenSearchDomain",
            domain_name="memory-mapping-domain",
            engine_version="OpenSearch_2.11",
            cluster_config=opensearch.CfnDomain.ClusterConfigProperty(
                instance_type="t3.small.search",
                instance_count=1,
                dedicated_master_enabled=False,
                zone_awareness_enabled=False
            ),
            ebs_options=opensearch.CfnDomain.EBSOptionsProperty(
                ebs_enabled=True,
                volume_size=10,
                volume_type="gp3"
            ),
            advanced_security_options=opensearch.CfnDomain.AdvancedSecurityOptionsInputProperty(
                enabled=True,
                internal_user_database_enabled=True,
                master_user_options=opensearch.CfnDomain.MasterUserOptionsProperty(
                    master_user_name="admin",
                    master_user_password="Admin123!"
                )
            ),
            domain_endpoint_options=opensearch.CfnDomain.DomainEndpointOptionsProperty(
                enforce_https=True
            ),
            node_to_node_encryption_options=opensearch.CfnDomain.NodeToNodeEncryptionOptionsProperty(
                enabled=True
            ),
            encryption_at_rest_options=opensearch.CfnDomain.EncryptionAtRestOptionsProperty(
                enabled=True
            ),
            access_policies={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "*"
                        },
                        "Action": "es:*",
                        "Resource": f"arn:aws:es:{self.region}:{self.account}:domain/memory-mapping-domain/*"
                    }
                ]
            }
        )

        # Outputs
        CfnOutput(self, "MetadataTableName", value=self.metadata_table.table_name)
        CfnOutput(self, "ProjectsTableName", value=self.projects_table.table_name)
        CfnOutput(self, "DecisionsTableName", value=self.decisions_table.table_name)
        CfnOutput(self, "NeptuneEndpoint", value=self.neptune_cluster.cluster_endpoint.hostname)
        CfnOutput(self, "OpenSearchEndpoint", value=self.opensearch_domain.attr_domain_endpoint)

        # S3 Bucket for document storage
        self.documents_bucket = s3.Bucket.from_bucket_name(
            self, "DocumentsBucket",
            bucket_name=f"memory-mapping-documents-{self.account}"
        )

        # SQS Queue for graph updates
        self.graph_update_queue = sqs.Queue(
            self, "GraphUpdateQueue",
            queue_name="memory-graph-updates",
            visibility_timeout=Duration.seconds(300),
            retention_period=Duration.days(14)
        )

        CfnOutput(self, "DocumentsBucketName", value=self.documents_bucket.bucket_name)
        CfnOutput(self, "GraphUpdateQueueUrl", value=self.graph_update_queue.queue_url)
