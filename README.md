# Portland Thorns Player Call App

A Streamlit scouting workspace for tracking recruitment calls, video reviews, follow-ups, and player summaries.

This public portfolio version uses fictional showcase data so the app can be reviewed without exposing private player, agent, or club information.

## Features

- Pipeline-level Insights dashboard for calls, recommendations, follow-ups, and agent quality
- Phone Calls workflow for recording qualitative player conversations
- Video Analysis workflow with review scores, notes, and recommendations
- Player Summary page with Conference > Team > Player filtering and downloadable PDF summaries
- Showcase Mode with 1,000 fictional call records and 393 fictional video reviews across 300 prospects

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run Scripts/00_Keep/qualitative_capture_app.py
```

## Showcase Data

The included data is synthetic:

- `Qualitative_Data/sample_call_log.csv`
- `Qualitative_Data/sample_video_reviews.csv`

Names, agents, agencies, notes, scores, and recommendations are fictional. Team and conference labels are public NCAA structures used to make the demo realistic.

Real call logs, uploaded databases, recordings, exports, Excel files, and private qualitative data are ignored by `.gitignore`.

## Streamlit Cloud

Use this app entry point:

```text
Scripts/00_Keep/qualitative_capture_app.py
```

