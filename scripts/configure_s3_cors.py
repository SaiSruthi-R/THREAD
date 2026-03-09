import boto3
import json

s3_client = boto3.client('s3', region_name='us-east-1')

bucket_name = 'memory-mapping-documents-140023380330'

cors_configuration = {
    'CORSRules': [
        {
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag'],
            'MaxAgeSeconds': 3000
        }
    ]
}

try:
    s3_client.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration=cors_configuration
    )
    print(f"✅ CORS configuration applied to bucket: {bucket_name}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
