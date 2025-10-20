#!/bin/bash

echo "Starting FollowUpSync in Local Mode..."
echo

echo "Starting MCP servers..."
python mcp/slack_server.py &
SLACK_PID=$!

python mcp/notion_server.py &
NOTION_PID=$!

python mcp/jira_server.py &
JIRA_PID=$!

echo "Waiting for MCP servers to start..."
sleep 5

echo "Starting Streamlit app..."
streamlit run app/streamlit_app.py

# Cleanup on exit
trap "kill $SLACK_PID $NOTION_PID $JIRA_PID" EXIT