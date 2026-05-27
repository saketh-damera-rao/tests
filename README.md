# AI Opportunity Prioritiser

A lightweight synthesis tool built for discovery workshop outputs.
Pre-loaded with use cases from an Australian health insurer AI opportunity session.

## What it does

Takes AI use cases surfaced from a stakeholder workshop and scores them across
four dimensions: client priority, strategic impact, build ease, and data readiness.
Produces a ranked recommendation, an interactive priority matrix, and an auto-generated
insight that flags structural dependencies (e.g. high-impact use cases blocked by
fragmented data) before the team commits to a build sequence.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Live demo

[Deploy to Streamlit Community Cloud — see deployment instructions below]

## Inputs

Each use case is scored 1 to 5 on four dimensions:

| Dimension | What it measures |
|---|---|
| Client priority | How urgently stakeholders named this as a pain point |
| Strategic impact | Value delivered if successfully deployed |
| Build ease | 5 = straightforward, 1 = complex infrastructure required |
| Data readiness | Availability and quality of data needed to power the tool |

Dimension weights are adjustable in real time via sidebar sliders and
auto-normalise so they do not need to sum to a fixed total.

## What it produces

- A ranked list of use cases with weighted composite scores
- An interactive effort-impact scatter plot sized by data readiness
- An auto-generated strategic insight that detects when high-impact use cases
  depend on data that is not yet ready, and surfaces this as a sequencing risk
- CSV export of the full ranked output

## Where it works well

- Synthesising 4 to 10 use cases from a discovery workshop
- Making prioritisation transparent and adjustable for a client debrief
- Communicating the data readiness risk without requiring a separate slide
- Letting the client or team adjust weights live and watch rankings shift

## Where it falls short

- Scores are qualitative judgments, not quantitative measurements. The tool
  makes those judgments comparable and consistent, it does not make them
  objective. The quality of the output depends entirely on the quality of
  the scoring conversation in the room.
- Currently single-session only. Scores are not persisted between sessions.
  A production version would connect to a database or shared spreadsheet.
- Does not currently handle dependencies between use cases (e.g. Use Case B
  cannot be built until Use Case A is live). A dependency graph would be the
  next meaningful addition.

## How I would develop it further

1. Add a dependency mapping layer so the tool can sequence use cases that
   are technically or structurally linked, not just rank them independently.
2. Connect to a persistent store (Supabase or Google Sheets) so multiple
   facilitators can score simultaneously during the workshop and results
   aggregate in real time.
3. Add a confidence rating alongside each score so the tool can flag use cases
   where the team had low certainty, not just low scores.
4. Generate a one-page client-ready PDF summary directly from the tool output.

## Deploying to Streamlit Community Cloud

1. Push app.py and requirements.txt to a public GitHub repository
2. Go to share.streamlit.io
3. Connect your GitHub account
4. Select the repository and set the main file path to app.py
5. Deploy. You will receive a public URL within 60 seconds.
