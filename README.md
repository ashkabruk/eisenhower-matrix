# Eisenhower Matrix Email Classifier

Ordnet eine Liste von E-Mails mit Claude den vier Eisenhower-Quadranten zu (Listenrepräsentation is am übersichtlichsten) und erzeugt einen farbcodierten HTML-Prioritätsreport.

## Setup

```bash
pip install -r requirements.txt
```

Anthropic API-Key setzen:

```bash
# bash
export ANTHROPIC_API_KEY="sk-ant-..."

# PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-...
```

## Ausführen

```bash
python classify.py                          # liest emails.json, schreibt output.html
python classify.py my_emails.json out.html  # eigene Pfade
python classify.py --lang de                # Sprache des Reports (de/en)
```

`output.html` danach im Browser oder E-Mail-Client öffnen.

## Beispiel

**Input** (`emails.json` — drei realistische E-Mails für eine Zürcher Immobilien-Investmentfirma):

| # | Absender | Betreff |
|---|----------|---------|
| 1 | `markus.baum@totalreno.ch` | Bestätigung HEUTE nötig — Übergabe Seestrasse 12 gefährdet |
| 2 | `anna.mueller@alpenpartners.ch` | JV Term Sheet — überarbeiteter Equity Waterfall für Montag |
| 3 | `digest@swissrealestatenews.ch` | Swiss Real Estate Digest — Woche 24, 2026 |

**Output** (`output.html`):

- 🔴 **Sofort erledigen** — Freigabe an Bauunternehmer mit 18'000 € Konventionalstrafe (dringend + wichtig)
- 🔵 **Einplanen** — JV Term Sheet vor dem Montagstermin prüfen (nicht dringend + wichtig)
- ⚫ **Eliminieren** — wöchentlicher Marktnewsletter (keine Aktion nötig)

## Von 70% auf 95% Trefferquote

Gelabeltes Testset (~50 E-Mails) mit den schwierigen Fällen aufbauen: gemischte Dringlichkeit, Multi-Thema-Threads, "klingt dringend, ist aber unwichtig". Classifier drüberlaufen lassen, jede Fehlklassifikation von Hand prüfen, vage Prompt-Definitionen nachschärfen und gezielte Few-Shot-Beispiele ergänzen. Zwei bis drei Durchläufe schliessen den grössten Teil der Lücke; das Parsen ist dank JSON-Output schon zuverlässig.

## Nächste Schritte

- **Batching**: Mehrere E-Mails pro API-Call → tiefere Kosten und Latenz.
- **Konfidenz**: Grenzfälle mit Konfidenzwert markieren.
- **Filter**: Report auf einzelne Quadranten beschränkbar.
- **Sprache**: Z.B. `--lang de` oder `--lang en`
