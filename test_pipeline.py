#!/usr/bin/env python3
"""
Test script for FollowUpSync pipeline
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.pipeline import Pipeline
from core.config import Config

def test_extraction():
    """Test the extraction pipeline with sample data"""
    print("🧪 Testing FollowUpSync Pipeline...")
    
    # Load sample transcript
    sample_path = Path("data/input/sample.txt")
    if not sample_path.exists():
        print("❌ Sample file not found. Please ensure data/input/sample.txt exists.")
        return False
    
    transcript = sample_path.read_text(encoding='utf-8')
    print(f"📄 Loaded transcript ({len(transcript)} characters)")
    
    # Initialize pipeline
    pipeline = Pipeline()
    
    try:
        # Process transcript
        print("🔄 Processing transcript...")
        result = pipeline.process_transcript(transcript)
        
        # Display results
        print(f"✅ Extraction complete! Run ID: {result.run_id}")
        print(f"📋 Found:")
        print(f"   - {len(result.decisions)} decisions")
        print(f"   - {len(result.action_items)} action items")
        print(f"   - {len(result.risks)} risks")
        
        # Show details
        if result.decisions:
            print("\n📝 Decisions:")
            for i, decision in enumerate(result.decisions, 1):
                print(f"   {i}. {decision.text}")
        
        if result.action_items:
            print("\n🎯 Action Items:")
            for i, item in enumerate(result.action_items, 1):
                owner = f" ({item.owner})" if item.owner else ""
                due = f" - Due: {item.due_date}" if item.due_date else ""
                print(f"   {i}. {item.title}{owner}{due}")
        
        if result.risks:
            print("\n⚠️ Risks:")
            for i, risk in enumerate(result.risks, 1):
                severity = f" [{risk.severity}]" if risk.severity else ""
                print(f"   {i}. {risk.text}{severity}")
        
        # Test artifact generation
        print("\n💾 Generating artifacts...")
        artifacts = pipeline.save_artifacts(result)
        print(f"✅ Artifacts saved:")
        print(f"   - Summary: {artifacts['summary_md']}")
        print(f"   - JSON: {artifacts['action_items_json']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return False

def test_config():
    """Test configuration status"""
    print("\n🔧 Configuration Status:")
    
    print(f"   Mode: {Config.MODE}")
    print(f"   Slack: {'✅' if Config.has_slack_config() else '❌'}")
    print(f"   Notion: {'✅' if Config.has_notion_config() else '❌'}")
    print(f"   Jira: {'✅' if Config.has_jira_config() else '❌'}")
    
    if not any([Config.has_slack_config(), Config.has_notion_config(), Config.has_jira_config()]):
        print("\n💡 To test integrations, configure API tokens in .env file")

def main():
    """Run all tests"""
    print("=" * 50)
    print("FollowUpSync Test Suite")
    print("=" * 50)
    
    # Test configuration
    test_config()
    
    # Test extraction
    success = test_extraction()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! FollowUpSync is ready to use.")
        print("\nNext steps:")
        print("1. Configure integrations in .env file")
        print("2. Start MCP servers: python mcp/slack_server.py (etc.)")
        print("3. Run app: streamlit run app/streamlit_app.py")
    else:
        print("❌ Tests failed. Please check the error messages above.")
    print("=" * 50)

if __name__ == "__main__":
    main()