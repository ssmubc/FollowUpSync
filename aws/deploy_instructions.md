# AWS Deployment Instructions

This guide covers deploying FollowUpSync MCP servers to AWS Lambda for production use.

## Prerequisites

- AWS CLI configured with appropriate permissions
- AWS account with access to Lambda, S3, and Bedrock
- Python 3.9+ and pip

## Required AWS Services

### 1. S3 Bucket Setup

```bash
# Create S3 bucket for artifacts
aws s3 mb s3://followupsync-artifacts-demo --region us-east-1

# Enable versioning (optional)
aws s3api put-bucket-versioning \
  --bucket followupsync-artifacts-demo \
  --versioning-configuration Status=Enabled
```

### 2. Bedrock Model Access

1. Go to AWS Console → Bedrock → Model access
2. Ensure access to: `amazon.nova-micro-v1:0` (available by default)
3. No approval needed - Nova models are immediately accessible

### 3. IAM Role for Lambda

Create IAM role with these policies:
- `AWSLambdaBasicExecutionRole`
- Custom policy for S3 and Bedrock:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::followupsync-artifacts-demo/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
    }
  ]
}
```

## Lambda Deployment

### Option 1: Manual Deployment

1. **Package Slack MCP Lambda**:
```bash
mkdir lambda_package
cp mcp/slack_server.py lambda_package/
cd lambda_package
pip install fastapi uvicorn mangum -t .
zip -r ../slack_mcp.zip .
cd ..
```

2. **Create Lambda Function**:
```bash
aws lambda create-function \
  --function-name followupsync-slack-mcp \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR-ACCOUNT:role/followupsync-lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://slack_mcp.zip \
  --timeout 30 \
  --memory-size 256
```

3. **Create Function URL**:
```bash
aws lambda create-function-url-config \
  --function-name followupsync-slack-mcp \
  --auth-type NONE \
  --cors '{
    "AllowCredentials": false,
    "AllowHeaders": ["content-type"],
    "AllowMethods": ["POST", "GET"],
    "AllowOrigins": ["*"],
    "MaxAge": 86400
  }'
```

4. **Repeat for Notion and Jira MCPs**

### Option 2: AWS SAM Deployment

Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  S3Bucket:
    Type: String
    Default: followupsync-artifacts-demo

Resources:
  SlackMCPFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: mcp/
      Handler: slack_server.lambda_handler
      Runtime: python3.9
      Timeout: 30
      MemorySize: 256
      Environment:
        Variables:
          MCP_AUTH_TOKEN: !Ref MCPAuthToken
      FunctionUrlConfig:
        AuthType: NONE
        Cors:
          AllowOrigins: ["*"]
          AllowMethods: ["POST", "GET"]
          AllowHeaders: ["content-type"]

  NotionMCPFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: mcp/
      Handler: notion_server.lambda_handler
      Runtime: python3.9
      Timeout: 30
      MemorySize: 256
      FunctionUrlConfig:
        AuthType: NONE

  MCPAuthToken:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /followupsync/mcp-auth-token
```

Deploy with:
```bash
sam build
sam deploy --guided
```

## Lambda Handler Modifications

For each MCP server, create a Lambda handler wrapper:

**lambda_function.py** (add to each MCP server):
```python
from mangum import Mangum
from slack_server import app  # or notion_server, jira_server

lambda_handler = Mangum(app)
```

## Environment Variables

Set these in Lambda console or via CLI:

```bash
# For each Lambda function
aws lambda update-function-configuration \
  --function-name followupsync-slack-mcp \
  --environment Variables='{
    "SLACK_BOT_TOKEN": "xoxb-your-token",
    "MCP_AUTH_TOKEN": "your-secure-token"
  }'
```

## Update Local Configuration

Update your `.env` file for AWS mode:

```bash
MODE=aws
S3_BUCKET=followupsync-artifacts-demo

# Update MCP URLs to Lambda Function URLs
SLACK_MCP_URL=https://abc123.lambda-url.us-east-1.on.aws/
NOTION_MCP_URL=https://def456.lambda-url.us-east-1.on.aws/
JIRA_MCP_URL=https://ghi789.lambda-url.us-east-1.on.aws/
```

## Security Considerations

### 1. Authentication
- Use API Gateway with API keys instead of Function URLs for production
- Implement proper authentication in MCP servers
- Use AWS Secrets Manager for sensitive tokens

### 2. Network Security
- Deploy Lambda in VPC if needed
- Use security groups to restrict access
- Enable CloudTrail for audit logging

### 3. Cost Optimization
- Set appropriate memory and timeout limits
- Use provisioned concurrency only if needed
- Monitor costs with CloudWatch

## Monitoring and Logging

### CloudWatch Setup
```bash
# Create log group
aws logs create-log-group --log-group-name /aws/lambda/followupsync-slack-mcp

# Set retention policy
aws logs put-retention-policy \
  --log-group-name /aws/lambda/followupsync-slack-mcp \
  --retention-in-days 7
```

### Metrics to Monitor
- Lambda invocations and errors
- Duration and memory usage
- S3 API calls and storage costs
- Bedrock API calls and costs

## Testing AWS Deployment

1. **Test Lambda Functions**:
```bash
# Test Slack MCP
curl -X POST https://your-lambda-url/slack_post_message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-mcp-token" \
  -d '{"channel": "#test", "text": "Hello from AWS Lambda!"}'
```

2. **Test Full Pipeline**:
- Set MODE=aws in .env
- Run Streamlit app
- Process a transcript
- Verify artifacts appear in S3

## Troubleshooting

### Common Issues

**Lambda timeout errors**:
- Increase timeout in function configuration
- Optimize code for faster execution

**Permission denied errors**:
- Check IAM role has required permissions
- Verify resource ARNs are correct

**Cold start latency**:
- Consider provisioned concurrency for production
- Optimize package size and imports

**S3 access errors**:
- Verify bucket exists and is accessible
- Check bucket policy and CORS settings

### Debugging Tips

1. Check CloudWatch logs for detailed error messages
2. Use AWS X-Ray for distributed tracing
3. Test individual components separately
4. Verify environment variables are set correctly

## Cost Estimation

For moderate usage (100 transcripts/month):
- Lambda: ~$1-5/month
- S3: ~$1-2/month  
- Bedrock: ~$5-15/month
- **Total: ~$7-22/month**

Monitor actual usage and adjust resources accordingly.

## Cleanup

To remove all AWS resources:

```bash
# Delete Lambda functions
aws lambda delete-function --function-name followupsync-slack-mcp
aws lambda delete-function --function-name followupsync-notion-mcp
aws lambda delete-function --function-name followupsync-jira-mcp

# Empty and delete S3 bucket
aws s3 rm s3://followupsync-artifacts-demo --recursive
aws s3 rb s3://followupsync-artifacts-demo

# Delete IAM role (via console or CLI)
```