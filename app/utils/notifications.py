import os
import httpx
from typing import Dict, Any

async def send_slack_lead_notification(
    lead_id: int,
    lead_data: Dict[str, Any],
    workflow_run_id: str
) -> bool:
    """
    Send formatted Slack notification for new lead
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ Slack webhook not configured")
        return False
    
    # Build rich Slack message
    payload = {
        "channel": "#sales-leads",
        "username": "BizLink Lead Bot",
        "icon_emoji": ":rocket:",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 New Lead Captured",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Name:*\n{lead_data.get('name', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{lead_data.get('email', 'N/A')}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Company:*\n{lead_data.get('company') or 'N/A'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Interest:*\n{lead_data.get('area_of_interest') or 'N/A'}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Lead ID: {lead_id} | Workflow: {workflow_run_id}"
                    }
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(webhook_url, json=payload)
            if response.status_code == 200:
                print(f"✅ Slack notification sent for lead {lead_id}")
                return True
            else:
                print(f"❌ Slack API error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Slack notification failed: {e}")
        return False