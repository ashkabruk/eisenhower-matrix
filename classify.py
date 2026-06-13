#!/usr/bin/env python3
"""Classify emails by Eisenhower Matrix quadrant and render an HTML priority report."""

import json
import sys
from datetime import date
from pathlib import Path

import anthropic

# --------------------------------------------------------------------------- #
# Quadrant metadata — order matters for display (most to least critical)       #
# --------------------------------------------------------------------------- #

QUADRANTS = {
    "DO_FIRST": {
        "label": "Urgent + Important — Do First",
        "color": "#b91c1c",
        "bg": "#fef2f2",
    },
    "SCHEDULE": {
        "label": "Not Urgent + Important — Schedule",
        "color": "#1d4ed8",
        "bg": "#eff6ff",
    },
    "DELEGATE": {
        "label": "Urgent + Not Important — Delegate",
        "color": "#b45309",
        "bg": "#fffbeb",
    },
    "ELIMINATE": {
        "label": "Not Urgent + Not Important — Eliminate",
        "color": "#4b5563",
        "bg": "#f9fafb",
    },
}

# --------------------------------------------------------------------------- #
# Prompt                                                                        #
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT = """\
You are an executive assistant for a real estate investment firm in Zurich. \
Classify each email using the Eisenhower Matrix.

Definitions
-----------
URGENT    – Requires action within 24–48 hours, has an imminent hard deadline, \
or immediately blocks others. Examples: closing deadline today, contractor \
waiting for written approval, legal notice with a response window.

IMPORTANT – Directly affects business outcomes, financial performance, legal \
standing, or key relationships. Examples: investment decisions, partnership \
agreements, regulatory compliance, strategic portfolio reviews.

Quadrants
---------
DO_FIRST  – Urgent AND Important      → Act immediately.
SCHEDULE  – Not Urgent AND Important  → Block time on the calendar.
DELEGATE  – Urgent AND NOT Important  → Route to someone else quickly.
ELIMINATE – NOT Urgent AND NOT Important → Archive or ignore.

Few-shot examples
-----------------
Email: {"sender": "contractor@vortex.ch", "subject": "Approval needed TODAY or €15k penalty", \
"body": "Sign-off required by 5 pm to avoid the late-delivery clause in section 8."}
→ {"quadrant": "DO_FIRST", "justification": "Hard 5 pm deadline with a direct financial \
penalty makes this both urgent and important."}

Email: {"sender": "digest@swissrealty.ch", "subject": "Weekly Market Roundup — Week 24", \
"body": "Top stories: Zurich office vacancy falls, Basel logistics rents rise…"}
→ {"quadrant": "ELIMINATE", "justification": "Generic newsletter with no action or \
decision required."}

Output format
-------------
Return ONLY valid JSON — no markdown fences, no commentary:
{
  "classifications": [
    {
      "id": "<email id>",
      "quadrant": "DO_FIRST|SCHEDULE|DELEGATE|ELIMINATE",
      "justification": "<one concise sentence>"
    }
  ]
}"""


# --------------------------------------------------------------------------- #
# Classification                                                                #
# --------------------------------------------------------------------------- #

def classify(emails: list[dict]) -> list[dict]:
    """Call Claude and return a list of classification objects."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    user_msg = "Classify these emails:\n\n" + json.dumps(emails, indent=2)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
    except anthropic.APIError as e:
        sys.exit(f"API error: {e}")

    raw = response.content[0].text
    try:
        data = json.loads(raw)
        return data["classifications"]
    except (json.JSONDecodeError, KeyError) as e:
        sys.exit(f"Model returned unexpected output ({e}):\n{raw}")


# --------------------------------------------------------------------------- #
# HTML rendering                                                                #
# --------------------------------------------------------------------------- #

def render_html(emails: list[dict], classifications: list[dict]) -> str:
    """Group classified emails by quadrant and return a self-contained HTML string."""
    by_id = {e["id"]: e for e in emails}

    grouped: dict[str, list] = {q: [] for q in QUADRANTS}
    for c in classifications:
        q = c.get("quadrant", "ELIMINATE")
        if q not in grouped:
            q = "ELIMINATE"  # fallback for unexpected values
        email = by_id.get(c["id"], {})
        grouped[q].append({**email, "justification": c.get("justification", "")})

    sections = ""
    for q, meta in QUADRANTS.items():
        items = grouped[q]
        if not items:
            continue
        rows = "".join(
            f"""<tr>
              <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;width:42%;
                         vertical-align:top">
                <div style="font-weight:600;font-size:13px;color:#111827">
                  {_esc(item.get("sender", ""))}
                </div>
                <div style="font-size:13px;color:#374151;margin-top:2px">
                  {_esc(item.get("subject", ""))}
                </div>
              </td>
              <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;
                         font-size:13px;color:#6b7280;vertical-align:top">
                {_esc(item.get("justification", ""))}
              </td>
            </tr>"""
            for item in items
        )
        sections += f"""
        <div style="margin-bottom:28px">
          <div style="background:{meta['color']};color:#fff;padding:10px 14px;
                      border-radius:6px 6px 0 0;font-size:14px;font-weight:600">
            {meta['label']}&ensp;<span style="font-weight:400;opacity:.85">
              ({len(items)} email{'s' if len(items) != 1 else ''})
            </span>
          </div>
          <table width="100%" cellpadding="0" cellspacing="0"
                 style="border-collapse:collapse;background:{meta['bg']};
                        border:1px solid #e5e7eb;border-top:none;
                        border-radius:0 0 6px 6px">
            <thead>
              <tr style="background:#f3f4f6">
                <th style="padding:7px 14px;text-align:left;font-size:11px;
                           color:#9ca3af;letter-spacing:.05em">SENDER / SUBJECT</th>
                <th style="padding:7px 14px;text-align:left;font-size:11px;
                           color:#9ca3af;letter-spacing:.05em">JUSTIFICATION</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    total = sum(len(v) for v in grouped.values())
    today = date.today().strftime("%B %d, %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Email Priority Report — Eisenhower Matrix</title>
</head>
<body style="margin:0;padding:32px 24px;background:#f3f4f6;
             font-family:Arial,Helvetica,sans-serif">
  <div style="max-width:680px;margin:0 auto">
    <h1 style="font-size:18px;font-weight:700;color:#111827;margin:0 0 4px">
      Email Priority Report
    </h1>
    <p style="margin:0 0 28px;font-size:13px;color:#9ca3af">
      Eisenhower Matrix &middot; {total} emails &middot; {today}
    </p>
    {sections}
  </div>
</body>
</html>"""


def _esc(s: str) -> str:
    """Minimal HTML escaping to prevent XSS in sender/subject/justification fields."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------- #
# Entry point                                                                   #
# --------------------------------------------------------------------------- #

def main() -> None:
    emails_path = sys.argv[1] if len(sys.argv) > 1 else "emails.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.html"

    try:
        emails = json.loads(Path(emails_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Input file not found: {emails_path}")
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON in {emails_path}: {e}")

    print(f"Classifying {len(emails)} email(s)...")
    classifications = classify(emails)
    html = render_html(emails, classifications)
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
