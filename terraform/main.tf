data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["137112412989"]

  filter {
    name   = "image-id"
    values = ["ami-01e082ac2f79f3918"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "ai-cost-detective-vpc"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "ai-cost-detective-public-subnet"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "ai-cost-detective-igw"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "ai-cost-detective-public-rt"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "app" {
  name        = "ai-cost-detective-app-sg"
  description = "Security group for AI Cloud Cost Detective application"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP access"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS access"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "FastAPI application access"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "ai-cost-detective-app-sg"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_iam_role" "cost_detector" {
  name = "ai-cost-detective-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "ai-cost-detective-ec2-role"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_iam_role_policy" "cost_explorer_read_only" {
  name = "ai-cost-detective-cost-explorer-read-only"
  role = aws_iam_role.cost_detector.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
          "ce:GetDimensionValues"
        ]

        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_managed_instance_core" {
  role       = aws_iam_role.cost_detector.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "cost_detector" {
  name = "ai-cost-detective-ec2-profile"
  role = aws_iam_role.cost_detector.name

  tags = {
    Name        = "ai-cost-detective-ec2-profile"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.cost_detector.name

  user_data = <<-EOF
  #!/bin/bash
  systemctl enable amazon-ssm-agent
  systemctl start amazon-ssm-agent
  EOF

  associate_public_ip_address = true

  root_block_device {
    volume_size = 8
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name        = "ai-cost-detective-app"
    Environment = "shared"
    Project     = "ai-cloud-cost-detective"
  }

}