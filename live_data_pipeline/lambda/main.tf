

provider "aws" {
  access_key = var.ACCESS_KEY_ID
  secret_key = var.SECRET_ACCESS_KEY
region = "eu-west-2"
}

#ECS task definition
variable "ACCESS_KEY_ID" {
    type = string
}

variable "SECRET_ACCESS_KEY" {
    type = string
}

variable "DATABASE_HOST" {
    type = string
}

variable "DATABASE_PORT" {
    type = string
}

variable "DATABASE_NAME" {
    type = string
}


variable "DATABASE_USERNAME" {
    type = string
}

variable "DATABASE_PASSWORD" {
    type = string
}
variable "DATABASE_SCHEMA" {
    type = string
}


data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

# Task Definition
resource "aws_ecs_task_definition" "c14-gem-lo-task-definition-batch" {
  family                   = "c14-gem-lo-task-definition-batch"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"  
  cpu                      = "256"      
  memory                   = "512"     
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn  
  task_role_arn            = data.aws_iam_role.ecs_task_execution_role.arn   

  container_definitions = jsonencode([
    {
      name      = "c14-gem-lo-truck-ecr-batch"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-gem-lo-truck-ecr-batch:latest" 
      cpu       = 256       
      memory    = 512            
      essential = true      
      portMappings = [
        {
          containerPort = 8080         
          hostPort      = 8080
        }
      ]
      environment = [
        {
          name  = "DATABASE_HOST"
          value = var.DATABASE_HOST
        },
        {
          name  = "DATABASE_USERNAME"
          value = var.DATABASE_USERNAME
        },
        {
          name  = "DATABASE_PASSWORD"
          value = var.DATABASE_PASSWORD
        },
        {
          name  = "DATABASE_PORT"
          value = var.DATABASE_PORT
        },
        {
          name  = "DATABASE_NAME"
          value = var.DATABASE_NAME
        }, 
        {
          name  = "DATABASE_SCHEMA"
          value = var.DATABASE_SCHEMA
        },
        {  
          name  = "ACCESS_KEY_ID"
          value = var.ACCESS_KEY_ID
        }, 
        {
          name  = "SECRET_ACCESS_KEY"
          value = var.SECRET_ACCESS_KEY
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/c14-gem-lo-truck-ecr-batch" 
          "awslogs-region"        = "eu-west-2"       
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group" = "true"
        }
      }
    }
  ])
}



# IAM Role for Lambda to assume
resource "aws_iam_role" "c14-gem-lo-exec-role" {
  name = "c14-gem-lo-exec-role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow"
      }
    ]
  })
}

# IAM Policy Attachment for logging permissions
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.c14-gem-lo-exec-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "c14-gem-lo-lambda_vpc_policy" {
  name = "c14-gem-lo-lambda_vpc_policy"
  role = aws_iam_role.c14-gem-lo-exec-role.name

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ],
        "Resource": "*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "c14-gem-lo-lambda-report2" {
  function_name = "c14-gem-lo-lambda-report2"
  role          = aws_iam_role.c14-gem-lo-exec-role.arn
  package_type  = "Image"

  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c14-gem-lo-live-report@sha256:a96f67594c3eb55679a2dfcf413dbb3315078fa91e437102dc0e6581307912d2" #image


  memory_size   = 512
  timeout       = 15

  environment {
       variables = {
         "DATABASE_HOST" = var.DATABASE_HOST
         "DATABASE_PASSWORD" = var.DATABASE_PASSWORD
         "DATABASE_USERNAME" = var.DATABASE_USERNAME
         "DATABASE_PORT" = var.DATABASE_PORT
         "DATABASE_HOST" = var.DATABASE_HOST
         "DATABASE_NAME" = var.DATABASE_NAME
         "DATABASE_SCHEMA" = var.DATABASE_SCHEMA
         "ACCESS_KEY_ID" = var.ACCESS_KEY_ID
         "SECRET_ACCESS_KEY" = var.SECRET_ACCESS_KEY
       }
  }
  vpc_config {
  subnet_ids         = ["subnet-0497831b67192adc2", "subnet-0acda1bd2efbf3922", "subnet-0465f224c7432a02e"] # IDs of the subnets in your VPC
  security_group_ids = ["sg-059e3edb078b8e82e"] 
  }
  architectures = ["x86_64"]

}

