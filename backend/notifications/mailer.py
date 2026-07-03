"""
mailer.py — Send Q&A notification emails via Gmail SMTP.

Called asynchronously after each /query so it never delays the API response.
Credentials are loaded from environment variables (set in Railway).
"""

import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

_GMAIL_USER = os.environ.get("GMAIL_USER", "jay.ziang.zhang@gmail.com")
_GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
_NOTIFY_TO = os.environ.get("NOTIFY_TO", "jay.ziang.zhang@gmail.com")


def _send(question: str, answer: str, sources: list) -> None:
    if not _GMAIL_APP_PASSWORD:
        print("[Mailer] GMAIL_APP_PASSWORD not set — skipping email.")
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sources_text = ", ".join(sources) if sources else "—"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[RAG] New question: {question[:60]}{'…' if len(question) > 60 else ''}"
    msg["From"] = _GMAIL_USER
    msg["To"] = _NOTIFY_TO

    plain = (
        f"Time:     {timestamp}\n"
        f"Question: {question}\n\n"
        f"Answer:\n{answer}\n\n"
        f"Sources: {sources_text}"
    )

    html = f"""
    <html><body style="font-family:sans-serif;max-width:640px;margin:auto;padding:24px">
      <h2 style="color:#1a1a2e">💬 New RAG Question</h2>
      <p style="color:#888;font-size:13px">{timestamp}</p>
      <table style="width:100%;border-collapse:collapse">
        <tr>
          <td style="padding:12px;background:#f0f4ff;border-radius:8px;vertical-align:top;width:80px">
            <strong>Q</strong>
          </td>
          <td style="padding:12px;background:#f0f4ff;border-radius:8px">
            {question}
          </td>
        </tr>
        <tr><td colspan="2" style="padding:6px"></td></tr>
        <tr>
          <td style="padding:12px;background:#f6fff0;border-radius:8px;vertical-align:top;width:80px">
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

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(_GMAIL_USER, _GMAIL_APP_PASSWORD)
            server.sendmail(_GMAIL_USER, _NOTIFY_TO, msg.as_string())
        print(f"[Mailer] Email sent for question: {question[:50]}")
    except Exception as e:
        print(f"[Mailer] Failed to send email: {e}")


def notify_async(question: str, answer: str, sources: list) -> None:
    """Fire-and-forget: send email in a background thread."""
    threading.Thread(target=_send, args=(question, answer, sources), daemon=True).start()
