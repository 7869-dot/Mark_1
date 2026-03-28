"""
integrations/gmail.py

Gmail integration — three tools:
  - gmail_read_inbox:  fetch recent emails
  - gmail_send_email:  send an email
  - gmail_search:      search emails by query

Auth: OAuth2. On first run, opens a browser for the user to authorize.
Token is saved to GMAIL_TOKEN_PATH and reused on future runs.
"""

from __future__ import annotations

import base64
import json
import os
from email.mime.text import MIMEText
from typing import Any

from config.logging import get_logger
from config.settings import settings
from integrations.base import BaseTool, ToolError

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def _get_gmail_service():
    """Build and return an authenticated Gmail API service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise ToolError("Google API libraries not installed. Run: pip install google-api-python-client google-auth-oauthlib")

    creds = None
    token_path = settings.gmail_token_path

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not settings.has_gmail:
                raise ToolError("Gmail credentials not configured. Set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in .env")

            client_config = {
                "installed": {
                    "client_id": settings.gmail_client_id,
                    "client_secret": settings.gmail_client_secret,
                    "redirect_uris": [settings.gmail_redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token_path) if os.path.dirname(token_path) else ".", exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _extract_body(payload: dict) -> str:
    """Recursively extract plain text body from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        body = _extract_body(part)
        if body:
            return body

    return ""


class GmailReadInbox(BaseTool):
    name = "gmail_read_inbox"
    description = "Read recent emails from Gmail inbox. Returns sender, subject, snippet, and body of recent messages."
    parameters = {
        "type": "object",
        "properties": {
            "max_results": {
                "type": "integer",
                "description": "Number of emails to fetch (1-20, default 5)",
                "default": 5,
            },
            "unread_only": {
                "type": "boolean",
                "description": "If true, only return unread emails",
                "default": False,
            },
        },
        "required": [],
    }

    def is_available(self) -> bool:
        return settings.has_gmail

    async def run(self, max_results: int = 5, unread_only: bool = False, **kwargs) -> str:
        try:
            service = _get_gmail_service()
            query = "is:unread" if unread_only else ""
            results = (
                service.users()
                .messages()
                .list(userId="me", maxResults=min(max_results, 20), q=query)
                .execute()
            )

            messages = results.get("messages", [])
            if not messages:
                return "No emails found."

            emails = []
            for msg_ref in messages:
                msg = service.users().messages().get(userId="me", id=msg_ref["id"], format="full").execute()
                headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
                body = _extract_body(msg["payload"])[:500]  # Truncate long bodies

                emails.append(
                    f"From: {headers.get('From', 'Unknown')}\n"
                    f"Subject: {headers.get('Subject', '(no subject)')}\n"
                    f"Date: {headers.get('Date', 'Unknown')}\n"
                    f"Body: {body}\n"
                    f"---"
                )

            return "\n".join(emails)

        except ToolError:
            raise
        except Exception as e:
            logger.error("gmail_read_error", error=str(e))
            raise ToolError(f"Failed to read Gmail: {e}")


class GmailSendEmail(BaseTool):
    name = "gmail_send_email"
    description = "Send an email via Gmail."
    parameters = {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject line"},
            "body": {"type": "string", "description": "Plain text email body"},
            "cc": {"type": "string", "description": "CC email address (optional)"},
        },
        "required": ["to", "subject", "body"],
    }

    def is_available(self) -> bool:
        return settings.has_gmail

    async def run(self, to: str, subject: str, body: str, cc: str = "", **kwargs) -> str:
        try:
            service = _get_gmail_service()
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            if cc:
                message["cc"] = cc

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId="me", body={"raw": raw}).execute()

            logger.info("gmail_sent", to=to, subject=subject)
            return f"Email sent successfully to {to} with subject '{subject}'"

        except ToolError:
            raise
        except Exception as e:
            logger.error("gmail_send_error", error=str(e))
            raise ToolError(f"Failed to send email: {e}")


class GmailSearch(BaseTool):
    name = "gmail_search"
    description = "Search Gmail for emails matching a query. Supports Gmail search operators like 'from:', 'subject:', 'has:attachment'."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Gmail search query, e.g. 'from:john@example.com subject:invoice'"},
            "max_results": {"type": "integer", "description": "Max emails to return (1-10)", "default": 5},
        },
        "required": ["query"],
    }

    def is_available(self) -> bool:
        return settings.has_gmail

    async def run(self, query: str, max_results: int = 5, **kwargs) -> str:
        try:
            service = _get_gmail_service()
            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=min(max_results, 10))
                .execute()
            )
            messages = results.get("messages", [])
            if not messages:
                return f"No emails found matching: {query}"

            summaries = []
            for msg_ref in messages:
                msg = service.users().messages().get(userId="me", id=msg_ref["id"], format="metadata").execute()
                headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
                summaries.append(
                    f"From: {headers.get('From', '?')} | "
                    f"Subject: {headers.get('Subject', '(no subject)')} | "
                    f"Date: {headers.get('Date', '?')}"
                )

            return f"Found {len(summaries)} emails:\n" + "\n".join(summaries)

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Gmail search failed: {e}")
