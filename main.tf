provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "us-east-1"
  s3_use_path_style         = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  endpoints {
    s3        = "http://localhost:4566"
    dynamodb  = "http://localhost:4566"
    lambda    = "http://localhost:4566"
    iam       = "http://localhost:4566"
    logs      = "http://localhost:4566"
  }
}

resource "aws_s3_bucket" "ulyft_s3_bucket" {
  bucket = "ulyft-csv-bucket"
}

resource "aws_dynamodb_table" "ulyft_dynamodb_table" {
  name         = "ulyft_metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "H"

  attribute {
    name = "H"
    type = "S"
  }
}

resource "aws_iam_role" "ulyft_lambda_role" {
  name = "ulyft_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ulyft_lambda_policy" {
  name   = "ulyft_lambda_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["logs:PutLogEvents", "logs:CreateLogGroup", "logs:CreateLogStream"],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem", "dynamodb:Scan", "dynamodb:Query"],
        Resource = "arn:aws:dynamodb:us-east-1:000000000000:table/ulyft_metadata"
      },
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject"],
        Resource = "arn:aws:s3:::ulyft-csv-bucket/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ulyft_attach_policy" {
  role       = aws_iam_role.ulyft_lambda_role.name
  policy_arn = aws_iam_policy.ulyft_lambda_policy.arn
}

resource "aws_lambda_function" "ulyft_csv_lambda" {
  function_name    = "ulyft_csv_processor"
  role            = aws_iam_role.ulyft_lambda_role.arn
  runtime         = "python3.9"
  handler         = "lambda_function.lambda_handler"
  filename        = "python.zip"
  source_code_hash = filebase64sha256("python.zip")

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.ulyft_dynamodb_table.name
    }
  }
}

resource "aws_s3_bucket_notification" "ulyft_s3_event_trigger" {
  bucket = aws_s3_bucket.ulyft_s3_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ulyft_csv_lambda.arn
    events             = ["s3:ObjectCreated:*"]
  }
}

resource "aws_lambda_permission" "ulyft_allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ulyft_csv_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.ulyft_s3_bucket.arn
}
