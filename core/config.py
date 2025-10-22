import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MODE = os.getenv("MODE", "local")
    
    # Bedrock
    BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
    
    # Slack
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_DEFAULT_CHANNEL = os.getenv("SLACK_DEFAULT_CHANNEL", "#followupsync-demo")
    
    # Notion
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    
    # Jira
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
    
    # AWS
    S3_BUCKET = os.getenv("S3_BUCKET")
    MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "change-me")
    
    @classmethod
    def is_aws_mode(cls):
        return cls.MODE == "aws"
    
    @classmethod
    def has_slack_config(cls):
        return bool(cls.SLACK_BOT_TOKEN)
    
    @classmethod
    def has_notion_config(cls):
        return bool(cls.NOTION_TOKEN and cls.NOTION_DATABASE_ID)
    
    @classmethod
    def has_jira_config(cls):
        return bool(cls.JIRA_BASE_URL and cls.JIRA_EMAIL and cls.JIRA_API_TOKEN)