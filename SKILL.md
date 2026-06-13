# Skill: Eisenhower Matrix Email Classifier

Reads a JSON list of emails, classifies each into an Eisenhower Matrix quadrant
using Claude (`claude-sonnet-4-6`), and renders a grouped HTML priority report.

## Inputs

`emails.json` — JSON array of email objects:

```json
[
  {
    "id": "unique-string",
    "sender": "name@domain.com",
    "subject": "Email subject line",
    "body": "Full email body text"
  }
]
```

## Outputs

`output.html` — self-contained HTML report, grouped and color-coded by quadrant:
- **Do First** (red) — Urgent + Important
- **Schedule** (blue) — Not Urgent + Important
- **Delegate** (amber) — Urgent + Not Important
- **Eliminate** (gray) — Not Urgent + Not Important

Each entry shows sender, subject, and a one-line justification from the model.

## Invocation

```bash
python classify.py                           # emails.json → output.html (defaults)
python classify.py my_emails.json out.html   # custom paths
```

## Environment

| Variable            | Required | Description                    |
|---------------------|----------|--------------------------------|
| `ANTHROPIC_API_KEY` | Yes      | Anthropic API key              |

## Dependencies

- Python 3.11+
- `anthropic` Python SDK (`pip install -r requirements.txt`)

## Error handling

- Missing or malformed `emails.json` → clear message, non-zero exit
- API failure (network, auth, rate limit) → `anthropic.APIError` message, non-zero exit
- Malformed JSON response from model → raw model output printed, non-zero exit
