"""
mailer.py — Send Q&A notification emails via Resend HTTP API.

Railway blocks outbound SMTP, so we use Resend (HTTP-based) instead.
Set RESEND_API_KEY in Railway Variables.
"""

import os
import threading
from datetime import datetime

_RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
_NOTIFY_TO = os.environ.get("NOTIFY_TO", "jay.ziang.zhang@gmail.com")


def _send(question: str, answer: str, sources: list) -> None:
    if not _RESEND_API_KEY:
        print("[Mailer] RESEND_API_KEY not set — skipping email.")
        return

    import resend
    resend.api_key = _RESEND_API_KEY

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sources_text = ", ".join(sources) if sources else "—"
    subject = f"[RAG] {question[:60]}{'…' if len(question) > 60 else ''}"

    html = f"""
    <html><body style="font-family:sans-serif;max-width:640px;margin:auto;padding:24px">
      <h2 style="color:#1a1a2e">💬 New RAG Question</h2>
      <p style="color:#888;font-size:13px">{timestamp}</p>
      <table style="width:100%;border-collapse:collapse">
        <tr>
          <td style="padding:12px;background:#f0f4ff;border-radius:8px;vertical-align:top;width:30px">
            <strong>Q</strong>
          </td>
          <td style="padding:12px;background:#f0f4ff;border-radius:8px">
            {question}
          </td>
        </tr>
        <tr><td colspan="2" style="padding:6px"></td></tr>
        <tr>
          <td style="padding:12px;background:#f6fff0;border-radius:8px;vertical-align:top;width:30px">
            <strong>A</strong>
          </td>
          <td style="padding:12px;background:#f6fff0;border-radius:8px;white-space:pre-wrap">
            {answer}
          </td>
        </tr>
      </table>
      <p style="margin-top:16px;color:#888;font-size:12px">Sources: {sources_text}</p>
    </body></html>
    """

    try:
        resend.Emails.send({
            "from": "RAG Notifier <onboarding@resend.dev>",
            "to": [_NOTIFY_TO],
            "subject": subject,
            "html": html,
        })
        print(f"[Mailer] Email sent for: {question[:50]}")
    except Exception as e:
        print(f"[Mailer] Failed to send email: {e}")


def notify_async(question: str, answer: str, sources: list) -> None:
    """Fire-and-forget: send email in a background thread."""
    threading.Thread(target=_send, args=(question, answer, sources), daemon=True).start()
