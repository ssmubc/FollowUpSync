import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.pipeline import Pipeline
from core.config import Config
from core.schema import ExtractionResult

st.set_page_config(page_title="FollowUpSync", page_icon="🚀", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    background: linear-gradient(135deg, #4285f4 0%, #1565c0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}
.sub-header {
    text-align: center;
    color: #5f6368;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}
.workflow-visual {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 1.5rem 0;
    padding: 1rem;
    background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
    border-radius: 16px;
    border: 1px solid #e3f2fd;
}
.workflow-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 1rem;
}
.workflow-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}
.workflow-text {
    font-size: 0.9rem;
    color: #1565c0;
    font-weight: 600;
}
.workflow-arrow {
    font-size: 1.5rem;
    color: #4285f4;
    margin: 0 0.5rem;
}
.stButton > button[kind="primary"] {
    background-color: #4285f4 !important;
    border-color: #4285f4 !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #3367d6 !important;
    border-color: #3367d6 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 FollowUpSync</h1>', unsafe_allow_html=True)
st.markdown('''
<div class="workflow-visual">
    <div class="workflow-step">
        <div class="workflow-icon">📝</div>
        <div class="workflow-text">Upload</div>
    </div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step">
        <div class="workflow-icon">🤖</div>
        <div class="workflow-text">AI Extract</div>
    </div>
    <div class="workflow-arrow">→</div>
    <div class="workflow-step">
        <div class="workflow-icon">✅</div>
        <div class="workflow-text">Deliver</div>
    </div>
</div>
''', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Turn meeting notes into action items with smart scheduling</p>', unsafe_allow_html=True)

# Initialize session state
if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None
if 'artifacts_saved' not in st.session_state:
    st.session_state.artifacts_saved = False

# Mode selection
mode = st.radio("Mode", ["AWS", "Local"], index=0)
st.caption("💡 AWS mode: Bedrock Nova AI with smart date parsing | Local mode: Rule-based fallback")
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
    st.subheader("2️⃣ Review Results")
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
                    if Config.is_aws_mode():
                        # Get content from S3 for download
                        summary_content = pipeline.storage.get_file_content(result.run_id, "Summary.md")
                        json_content = pipeline.storage.get_file_content(result.run_id, "ActionItems.json")
                    else:
                        # Get content from local files
                        summary_content = Path(artifacts['summary_md']).read_text()
                        json_content = Path(artifacts['action_items_json']).read_text()
                    
                    st.download_button(
                        "📄 Download Summary.md",
                        data=summary_content,
                        file_name=f"Summary_{result.run_id}.md",
                        mime="text/markdown"
                    )
                    
                    st.download_button(
                        "📋 Download ActionItems.json",
                        data=json_content,
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
        sample_text = """Meeting Notes - Project Kickoff (Oct 21, 2025)
Attendees: John, Sarah, Mike, Anthony
        
Key decisions from today:
- After much debate, tech team went with React (Sarah preferred Vue but majority ruled)
- Database: PostgreSQL - Sarah and Mike both agreed on this one
- AWS for deployment - leadership pushed for this despite cost concerns

TODOs coming out of this:
- John: get dev environment ready by end of week (Friday)
- Sarah: DB schema work, needs to be done by next Tuesday 
- Mike: look into deployment stuff, deadline Oct 30th
- Anthony: crunch the numbers on costs, due Jan 1st

Concerns raised:
- Timeline is super tight for MVP launch. John suggested we add some buffer time and focus on core features first
- Mobile app integration could be tricky - Mike thinks we should document the API properly and test integration early
- Need to optimize our cloud spending. Anthony mentioned we should set up cost monitoring and optimize our resource usage

Next meeting: TBD"""
        
        st.text_area("Sample content (copy this):", value=sample_text, height=300)
    
    st.subheader("⚙️ How It Works")
    st.markdown("""
    1. **Paste or upload** a meeting transcript
    2. **Process with AWS Bedrock Nova** - AI extracts structured data
    3. **Review smart-parsed dates** - "next Tuesday" → 2025-10-28
    4. **See organized results** - decisions, actions, risks with owners
    5. **Generate artifacts** - download Summary.md & ActionItems.json
    """)