import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.pipeline import Pipeline
from core.config import Config
from core.schema import ExtractionResult

st.set_page_config(page_title="FollowUpSync", page_icon="✅", layout="wide")
st.title("FollowUpSync — meeting → action")
st.caption("Convert meeting transcripts into actionable execution plans")

# Initialize session state
if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None
if 'artifacts_saved' not in st.session_state:
    st.session_state.artifacts_saved = False

# Mode selection
mode = st.radio("Mode", ["Local", "AWS"], index=0)
Config.MODE = "local" if mode == "Local" else "aws"

# Initialize pipeline
pipeline = Pipeline()

# Section 1: Input
st.subheader("1️⃣ Input")
tab1, tab2 = st.tabs(["Paste text", "Upload file (.txt)"])
text_input = ""
file_bytes = None

with tab1:
    text_input = st.text_area("Paste transcript text", height=200)

with tab2:
    uploaded = st.file_uploader("Upload a .txt transcript", type=["txt"])
    if uploaded:
        file_bytes = uploaded.read().decode("utf-8")

if st.button("🔄 Process", type="primary"):
    content = text_input if text_input else (file_bytes or "")
    if not content.strip():
        st.warning("Please paste text or upload a .txt file.")
    else:
        with st.spinner("Processing transcript..."):
            try:
                result = pipeline.process_transcript(content)
                st.session_state.extraction_result = result
                st.session_state.artifacts_saved = False
                st.success(f"✅ Processed! Run ID: {result.run_id}")
            except Exception as e:
                st.error(f"Error processing transcript: {str(e)}")

# Section 2: Review & Edit
if st.session_state.extraction_result:
    st.subheader("2️⃣ Review & Edit")
    result = st.session_state.extraction_result
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Decisions**")
        if result.decisions:
            decisions_data = []
            for i, decision in enumerate(result.decisions):
                decisions_data.append({
                    "Text": decision.text,
                    "Owners": ", ".join(decision.owners) if decision.owners else "",
                    "Rationale": decision.rationale or ""
                })
            st.dataframe(pd.DataFrame(decisions_data), use_container_width=True)
        else:
            st.info("No decisions found")
    
    with col2:
        st.write("**Action Items**")
        if result.action_items:
            actions_data = []
            for i, item in enumerate(result.action_items):
                actions_data.append({
                    "Title": item.title,
                    "Owner": item.owner or "Unassigned",
                    "Due Date": str(item.due_date) if item.due_date else "",
                    "Priority": item.priority or "Medium"
                })
            st.dataframe(pd.DataFrame(actions_data), use_container_width=True)
        else:
            st.info("No action items found")
    
    with col3:
        st.write("**Risks & Blockers**")
        if result.risks:
            risks_data = []
            for i, risk in enumerate(result.risks):
                risks_data.append({
                    "Text": risk.text,
                    "Severity": risk.severity or "Medium",
                    "Mitigation": risk.mitigation or ""
                })
            st.dataframe(pd.DataFrame(risks_data), use_container_width=True)
        else:
            st.info("No risks found")
    
    # Section 3: Deliver
    st.subheader("3️⃣ Deliver")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Integrations**")
        
        # Slack integration
        send_slack = st.checkbox("Send to Slack", disabled=not Config.has_slack_config())
        if send_slack:
            slack_channel = st.text_input("Slack Channel", value=Config.SLACK_DEFAULT_CHANNEL)
        
        # Notion integration
        send_notion = st.checkbox("Create Notion tasks", disabled=not Config.has_notion_config())
        
        # Jira integration
        send_jira = st.checkbox("Create Jira issues", disabled=not Config.has_jira_config())
        
        if st.button("📤 Send", type="primary"):
            integrations = {}
            if send_slack:
                integrations['slack'] = {'channel': slack_channel}
            if send_notion:
                integrations['notion'] = True
            if send_jira:
                integrations['jira'] = True
            
            if integrations:
                with st.spinner("Sending to integrations..."):
                    try:
                        delivery_results = pipeline.deliver_to_integrations(result, integrations)
                        st.success("✅ Sent to integrations!")
                        
                        # Show results
                        for service, service_result in delivery_results.items():
                            if isinstance(service_result, dict) and service_result.get('ok'):
                                st.success(f"✅ {service.title()}: Success")
                            elif isinstance(service_result, list):
                                success_count = sum(1 for r in service_result if not r.get('error'))
                                st.success(f"✅ {service.title()}: {success_count}/{len(service_result)} items created")
                            else:
                                st.error(f"❌ {service.title()}: {service_result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error sending to integrations: {str(e)}")
            else:
                st.warning("Please select at least one integration")
    
    with col2:
        st.write("**Artifacts**")
        
        if st.button("💾 Generate Artifacts"):
            with st.spinner("Generating artifacts..."):
                try:
                    artifacts = pipeline.save_artifacts(result)
                    st.session_state.artifacts_saved = True
                    st.success("✅ Artifacts generated!")
                    
                    # Show download links
                    st.download_button(
                        "📄 Download Summary.md",
                        data=Path(artifacts['summary_md']).read_text() if not Config.is_aws_mode() else "Check S3",
                        file_name=f"Summary_{result.run_id}.md",
                        mime="text/markdown"
                    )
                    
                    st.download_button(
                        "📋 Download ActionItems.json",
                        data=Path(artifacts['action_items_json']).read_text() if not Config.is_aws_mode() else "Check S3",
                        file_name=f"ActionItems_{result.run_id}.json",
                        mime="application/json"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating artifacts: {str(e)}")
    
    # Section 4: Configuration Status
    with st.expander("🔧 Configuration Status"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Slack**")
            if Config.has_slack_config():
                st.success("✅ Configured")
            else:
                st.error("❌ Missing SLACK_BOT_TOKEN")
        
        with col2:
            st.write("**Notion**")
            if Config.has_notion_config():
                st.success("✅ Configured")
            else:
                st.error("❌ Missing NOTION_TOKEN or NOTION_DATABASE_ID")
        
        with col3:
            st.write("**Jira**")
            if Config.has_jira_config():
                st.success("✅ Configured")
            else:
                st.error("❌ Missing Jira configuration")

# Sidebar with sample data
with st.sidebar:
    st.subheader("📝 Sample Transcript")
    if st.button("Load Sample"):
        sample_text = """Meeting Notes - Project Kickoff
        
Decisions made:
- We decided to use React for the frontend development
- Database will be PostgreSQL
- Deploy on AWS infrastructure

Action items:
- John will set up the development environment by Friday
- Sarah needs to create the database schema by next Tuesday
- Mike will research deployment options this week

Risks identified:
- Timeline might be tight for the MVP release
- Need to ensure API compatibility with mobile app
- Budget constraints for AWS services"""
        
        st.text_area("Sample content (copy this):", value=sample_text, height=300)
    
    st.subheader("🚀 Quick Start")
    st.markdown("""
    1. **Paste or upload** a meeting transcript
    2. **Process** to extract structured data
    3. **Review** and edit the results
    4. **Configure** integrations in .env file
    5. **Send** to Slack/Notion/Jira
    6. **Download** artifacts
    """)