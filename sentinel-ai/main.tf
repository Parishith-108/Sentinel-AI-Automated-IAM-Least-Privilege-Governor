// Terraform skeleton for Sentinel-AI
// NOTE: This is a minimal example and requires adaptation before use.

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "lambda_s3_bucket" {
  type = string
}

variable "lambda_s3_key" {
  type = string
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = var.lambda_s3_bucket
  acl    = "private"
  tags = {
    Name = "sentinel-ai-lambda-artifacts"
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "sentinel_ai_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

// The Lambda will need permissions to read Access Analyzer findings, read CloudTrail, call Bedrock, and put secrets into SSM/Secrets Manager.
// For a production deployment, craft a least-privilege IAM policy and attach it here.

resource "aws_lambda_function" "sentinel_handler" {
  function_name    = "sentinel_ai_handler"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "iam_logic.lambda_handler"
  runtime          = "python3.10"
  s3_bucket        = aws_s3_bucket.lambda_bucket.id
  s3_key           = var.lambda_s3_key
  environment {
    variables = {
      GITHUB_TOKEN_SSM = "/sentinel_ai/github_token"
      BEDROCK_MODEL_ID = var.bedrock_model_id
    }
  }
}

variable "bedrock_model_id" {
  type    = string
  default = "claude-3.5-sonnet"
}

resource "aws_cloudwatch_event_rule" "access_analyzer_unused_access" {
  name        = "SentinelAI-AccessAnalyzerUnusedAccess"
  description = "Rule to catch IAM Access Analyzer unused-access findings"
  event_pattern = <<PATTERN
{
  "source": ["aws.access-analyzer"],
  "detail-type": ["Access Analyzer Finding"]
}
PATTERN
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.access_analyzer_unused_access.name
  arn       = aws_lambda_function.sentinel_handler.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sentinel_handler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.access_analyzer_unused_access.arn
}

// Outputs
output "lambda_function_name" {
  value = aws_lambda_function.sentinel_handler.function_name
}

// Notes:
// - This main.tf is intentionally minimal. You should package the Lambda code, upload to S3 or use local file in Terraform with care.
// - Secrets (GitHub token, Bedrock keys) should be stored in SSM or Secrets Manager and referenced by the Lambda role.
