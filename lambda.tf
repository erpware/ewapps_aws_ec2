data "archive_file" "lambda_ew_app_ec2" {
  type        = "zip"
  source_file = "lambda_function.py"
  output_path = "function.zip"
}

resource "aws_lambda_function" "ew_app_ec2" {
  function_name                  = "ew_app_ec2"
  description                    = "Backend Lambda for erpware EC2 Starter"
  handler                        = "lambda_function.lambda_handler"
  layers                         = []
  memory_size                    = 128
  reserved_concurrent_executions = -1
  role                           = aws_iam_role.iam_role_ew_app_ec2.arn
  runtime                        = "python3.8"
  filename                       = data.archive_file.lambda_ew_app_ec2.output_path
  source_code_hash               = data.archive_file.lambda_ew_app_ec2.output_base64sha256
  timeout = 10

  timeouts {}

  tracing_config {
    mode = "PassThrough"
  }

  environment {
    variables = {
      SECURESTRING = var.securestring
    }
  }
}

resource "aws_iam_role" "iam_role_ew_app_ec2" {
  name = "ew_app_ec2_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_permission" "lambda_permission_ew_app_ec2" {
  statement_id  = "AllowInvokeOfEwAppEc2"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ew_app_ec2.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:eu-central-1:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.ew_app_ec2.id}/*/${aws_api_gateway_method.api_ew_app_ec2_method.http_method}/*"
}

resource "aws_iam_role_policy_attachment" "role_policy_ew_app_ec2" {
  policy_arn = aws_iam_policy.iam_policy_ew_app_ec2.arn
  role       = aws_iam_role.iam_role_ew_app_ec2.id
}

resource "aws_iam_policy" "iam_policy_ew_app_ec2" {
  name = "ew_app_ec2_policy"
  path = "/service-role/"
  policy = jsonencode(
  {
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = join("", ["arn:aws:logs:eu-central-1:", data.aws_caller_identity.current.account_id, ":log-group:/aws/lambda/", aws_lambda_function.ew_app_ec2.function_name, ":*"])
        Sid      = "EwAppEC2Logs"
      },
      {
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:DescribeInstances",
        ]
        Effect = "Allow"
        Resource = "*"
        Sid = "EwAppEC2Instances"
      },
    ]
    Version = "2012-10-17"
  }
  )
}
