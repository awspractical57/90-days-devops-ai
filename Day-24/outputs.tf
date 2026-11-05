# outputs.tf values shown after terraform apply
# like return values from function
output "bucket_name"{
    description = "name of the s3 bucket created"
    # reference: resource_type.local_name.attribute
    value       = aws_s3_bucket.devops_bucket.id
}
output "bucket_arn"{
    description = "arn of the s3 bucket"
    value       = aws_s3_bucket.devops_bucket.arn
}

output "bucket_region"{
    description = "region of the s3 bucket"
    value       = aws_s3_bucket.devops_bucket.region
}