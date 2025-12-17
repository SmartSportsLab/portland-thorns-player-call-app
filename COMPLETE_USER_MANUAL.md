# Portland Thorns Scouting System - Complete User Manual

**Version:** 1.0  
**Last Updated:** January 2025  
**For:** Mike Norris and Staff

---

## Table of Contents

1. [Overview](#overview)
2. [Part 1: Data Collection from Wyscout](#part-1-data-collection-from-wyscout)
3. [Part 2: Data Processing and Analysis](#part-2-data-processing-and-analysis)
4. [Part 3: Qualitative Capture App](#part-3-qualitative-capture-app)
5. [Part 4: Deployment and Access](#part-4-deployment-and-access)
6. [Troubleshooting](#troubleshooting)
7. [Quick Reference](#quick-reference)

---

## Overview

This manual documents the complete workflow for the Portland Thorns NCAA Talent Identification System, from initial data collection through Wyscout exports to the final qualitative capture application. This system enables comprehensive tracking of player calls, video reviews, and performance metrics.

### System Components

1. **Wyscout Data Export** - Automated scraping of player statistics
2. **Data Processing Scripts** - Analysis and report generation
3. **Qualitative Capture App** - Streamlit-based call log and video review system
4. **Player Summary Reports** - Comprehensive player analysis dashboards

### Key Features

- 📞 **Phone Call Logging** - Track all player/agent conversations
- 🎥 **Video Analysis** - Log and review player video assessments
- 📊 **Player Summaries** - Comprehensive player dashboards with metrics
- 📈 **Performance Metrics** - Visual analytics and comparisons
- ✅ **To Do List** - Task management for scouting workflow

---

## Part 1: Data Collection from Wyscout

### 1.1 Understanding Wyscout Export

Wyscout is a football data platform that provides detailed player statistics. Our system automates the export of player data from Wyscout for analysis.

### 1.2 Export Process Overview

The Wyscout export system consists of several modules that work together:

1. **Login Module** - Authenticates with Wyscout
2. **Navigation Modules** - Navigate to specific teams/leagues
3. **Player Discovery** - Finds all players on team pages
4. **Data Export** - Exports player statistics to CSV/Excel files

### 1.3 Running Wyscout Exports

#### Option A: Export All Teams

```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"
python wyscout_orchestrator_complete.py
```

This will:
- Log into Wyscout
- Navigate to the selected league (e.g., Liga Mayor)
- Process all teams
- Export player data for each player
- Save files to the exports directory

#### Option B: Export Specific Teams

```python
from wyscout_orchestrator_complete import WyscoutCompleteOrchestrator

orchestrator = WyscoutCompleteOrchestrator()
selected_teams = ["Cibao", "Moca", "Atlético Pantoja"]
success = orchestrator.run_complete_automation(selected_teams)
```

#### Option C: Export Specific Players

```python
orchestrator = WyscoutCompleteOrchestrator()
selected_teams = ["Cibao"]
selected_players = ["Player1", "Player2"]
success = orchestrator.run_complete_automation(selected_teams, selected_players)
```

### 1.4 Export Output

Exported files are saved in the download directory (default: `exports/`):

```
exports/
├── player_data_1.csv
├── player_data_2.csv
├── ...
└── export_results.json
```

Each CSV file contains:
- Player name and basic information
- Position and team details
- Performance statistics (goals, assists, passes, etc.)
- Match data and minutes played
- Advanced metrics (xG, xA, etc.)

### 1.5 Export Configuration

**Download Directory:**
```python
orchestrator = WyscoutCompleteOrchestrator(download_dir="./my_exports")
```

**Logging Level:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # For detailed logging
```

### 1.6 Troubleshooting Wyscout Exports

**Common Issues:**

1. **Login Failed**
   - Check Wyscout credentials
   - Verify internet connection
   - Check for CAPTCHA or 2FA requirements

2. **Team Not Found**
   - Verify team names match exactly
   - Check if team is in the selected league
   - Ensure page has loaded completely

3. **Player Navigation Failed**
   - Check if player names are correct
   - Verify player is on the team page
   - Ensure page has loaded completely

4. **Roma Export Failed**
   - Check if Roma export button is visible
   - Verify download permissions
   - Check available disk space

---

## Part 2: Data Processing and Analysis

### 2.1 Data Processing Overview

After exporting data from Wyscout, several processing scripts analyze and organize the data:

1. **Player Statistics Processing** - Normalizes data to per-90 metrics
2. **Conference Reports** - Generates position-specific scouting reports
3. **Performance Index Calculation** - Calculates team-relative performance
4. **NWSL Readiness Analysis** - Predicts NWSL success probability

### 2.2 Key Processing Scripts

#### Conference Report Generation

Location: `Scripts/00_Keep/update_mike_norris_reports.py`

**Purpose:** Generates comprehensive scouting reports for each conference (ACC, SEC, Big 10, Big 12, Ivy League).

**How to Run:**
```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"
python update_mike_norris_reports.py
```

**Output:** Excel files in `Conference Reports/`:
- `Portland Thorns 2025 ACC Scouting Report.xlsx`
- `Portland Thorns 2025 SEC Scouting Report.xlsx`
- `Portland Thorns 2025 BIG10 Scouting Report.xlsx`
- `Portland Thorns 2025 BIG12 Scouting Report.xlsx`
- `Portland Thorns 2025 IVY Scouting Report.xlsx`

**Report Contents:**
- Player rankings by position profile
- Performance scores (80/20 intent vs accuracy weighting)
- Team average comparisons
- Position-specific metrics
- Percentile rankings

#### Player Overview Generation

Location: `Scripts/00_Keep/generate_player_overviews.py`

**Purpose:** Creates detailed 2-page PDF overviews for individual players.

**How to Run:**
```bash
python generate_player_overviews.py
```

**Output:** PDF files in `Player Overviews/` directory

### 2.3 Data Files Structure

```
Data/Advanced Search/
├── Qualitative_Data/
│   ├── call_log.csv              # Phone call records
│   ├── video_reviews.csv         # Video analysis records
│   ├── agents.csv                # Agent contact information
│   └── column_visibility_presets.json  # Table display preferences
├── Conference Reports/
│   ├── Portland Thorns 2025 ACC Scouting Report.xlsx
│   ├── Portland Thorns 2025 SEC Scouting Report.xlsx
│   └── ...
├── Exports/
│   ├── Players Stats By Position/
│   │   ├── AM Advanced Playmaker ACC 2025.xlsx
│   │   ├── CB Hybrid ACC 2025.xlsx
│   │   └── ...
│   └── Team Stats By Conference/
└── Player Overviews/
    ├── Top 15/
    └── Other/
```

### 2.4 Position Profiles

The system analyzes players across four main position profiles:

1. **Hybrid CB** (Ball-Playing Center Back)
2. **DM Box-To-Box** (Defensive Midfielder)
3. **Advanced Playmaker** (AM/CM)
4. **Touchline Winger** (Wide Attacker)

Each position profile has specific metrics and weightings defined in the configuration files.

---

## Part 3: Qualitative Capture App

### 3.1 App Overview

The Qualitative Capture App is a Streamlit-based web application for logging phone calls, video reviews, and viewing player summaries. It provides a user-friendly interface for tracking qualitative scouting information.

### 3.2 Accessing the App

#### Local Access

1. Open Terminal
2. Navigate to the app directory:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"
   ```
3. Launch the app:
   ```bash
   streamlit run qualitative_capture_app.py
   ```
4. The app will open in your browser at `http://localhost:8501`

#### Cloud Access (Streamlit Cloud)

The app is deployed on Streamlit Cloud and accessible via a public URL (provided separately).

### 3.3 Login

**Credentials:**
- Username: `MikeNorris`
- Password: `1234`

**Note:** After logging in, your session persists even if you refresh the page.

### 3.4 App Pages

The app has five main pages accessible via the sidebar navigation:

1. **Phone Calls** - Log and view player/agent calls
2. **Video Analysis** - Log and view video reviews
3. **Player Summary** - Comprehensive player dashboards
4. **Performance Metrics** - Analytics and visualizations
5. **To Do List** - Task management

---

### 3.5 Phone Calls Page

#### 3.5.1 Overview

The Phone Calls page allows you to log conversations with players and agents, track assessments, and view call history.

#### 3.5.2 Logging a New Call

**Step 1: Select Player**
- Use the dropdown menus to select:
  - **Conference** (ACC, SEC, Big 10, Big 12, Ivy League)
  - **Team** (automatically filtered by conference)
  - **Player** (automatically filtered by team)

**Step 2: Fill Call Details**

**Required Fields:**
- **Player Name** (auto-populated from selection)
- **Call Date**
- **Call Type** (Initial Contact, Follow-up, Agent Call, etc.)

**Optional Fields:**
- **Agent Name** (select from existing agents or add new)
- **Call Duration** (in minutes)
- **Overall Rating** (1-10 scale)
- **Recommendation** (Yes, No, Maybe, Follow-up)
- **Notes** (free text)
- **Follow-up Required** (Yes/No)
- **Follow-up Date** (if follow-up required)

**Step 3: Assessment Ratings**

Rate the player on various attributes (1-10 scale):
- Technical Ability
- Physical Attributes
- Tactical Understanding
- Mental Attributes
- Communication
- Coachability
- Team Fit
- Potential

**Step 4: Save**

Click **"Save Call Log"** at the bottom of the form to save the call.

#### 3.5.3 Call History Tab

View all logged calls with filtering and sorting options:

**Filters:**
- **Date Range** - Last 7 days, Last 30 days, This Month, This Year, Custom Range
- **Player** - Filter by specific players
- **Recommendation** - Filter by recommendation status
- **Conference** - Filter by conference

**View Modes:**
- **Summary** - Compact view with key information
- **Expanded** - Full details for each call

**Features:**
- Sort by any column
- Search within the table
- Export to CSV
- Column visibility presets (save your preferred column layout)

#### 3.5.4 Player Call Rankings Tab

View players ranked by:
- Number of calls
- Average overall rating
- Recommendation status
- Most recent call date

#### 3.5.5 Draft Saving

**Save Draft:**
- Click "Save Draft" in the sidebar to save your progress without submitting
- Draft is automatically restored when you return to the form

**Clear Draft:**
- Click "Clear Draft" to remove saved draft data

**Refresh Form:**
- Click "Refresh Form" to clear all fields and start fresh

---

### 3.6 Video Analysis Page

#### 3.6.1 Overview

The Video Analysis page allows you to log video reviews of players, track analysis metrics, and view review history.

#### 3.6.2 Adding a Video Review

**Step 1: Select Player**
- Use the dropdown to select a player from the database

**Step 2: Video Information**
- **Video Type** (Match Highlights, Full Match, Training Footage, etc.)
- **Video Source** (YouTube, Hudl, Wyscout, etc.)
- **Video URL** (optional)
- **Review Date**

**Step 3: Analysis Ratings**

Rate the player on video-specific metrics (1-10 scale):
- Technical Execution
- Decision Making
- Spatial Awareness
- Physical Performance
- Tactical Discipline
- Overall Video Score

**Step 4: Notes**
- Add detailed notes about what you observed in the video

**Step 5: Save**
- Click **"Save Video Review"** to save the review

#### 3.6.3 Video Review History

View all video reviews with:
- Filtering by player, date range, video type
- Sorting by any column
- Search functionality
- Export to CSV

---

### 3.7 Player Summary Page

#### 3.7.1 Overview

The Player Summary page provides a comprehensive dashboard for each player, combining phone call data and video analysis.

#### 3.7.2 Accessing a Player Summary

1. Select a player from the dropdown at the top of the page
2. The page will display all available information for that player

#### 3.7.3 Phone Call Section

**Summary Metrics:**
- Total Calls
- Average Overall Rating
- Most Recent Call Date
- Recommendation Status

**Average Ratings Chart:**
- Bar chart showing average ratings across all assessment categories

**All Calls Table:**
- Complete list of all calls for the player
- Expandable rows showing detailed call information

**Call Review Details:**
- Expandable sections for each call showing:
  - Full call notes
  - All assessment ratings
  - Agent information
  - Follow-up details

**Radar Chart:**
- Visual comparison of player's call metrics vs. call log average
- Shows strengths and weaknesses relative to other players

#### 3.7.4 Video Analysis Section

**Summary Metrics:**
- Total Reviews
- Average Video Score
- Most Recent Review Date
- Video Types Reviewed

**Average Ratings Chart:**
- Bar chart showing average ratings across video analysis categories

**All Video Reviews Table:**
- Complete list of all video reviews for the player
- Expandable rows showing detailed review information

**Video Review Details:**
- Expandable sections for each review showing:
  - Full review notes
  - All video analysis ratings
  - Video source and URL
  - Review date

**Radar Chart:**
- Visual comparison of player's video metrics vs. video analysis average

#### 3.7.5 Combined Analysis

**Combined Radar Chart:**
- Shows both phone call and video analysis metrics together
- Provides holistic view of player assessment

#### 3.7.6 PDF Download

**Download Player Summary PDF:**
- Click the "Download Player Summary PDF" button at the bottom
- Generates a comprehensive PDF report including:
  - All call logs
  - All video reviews
  - Summary statistics
  - Charts and visualizations

---

### 3.8 Performance Metrics Page

#### 3.8.1 Overview

The Performance Metrics page provides Power BI-style visualizations and analytics for scouting data.

#### 3.8.2 Features

- Interactive charts and graphs
- Filterable metrics
- Comparative analysis
- Trend visualization

---

### 3.9 To Do List Page

#### 3.9.1 Overview

The To Do List page helps manage scouting tasks and follow-ups.

#### 3.9.2 Features

- Create tasks
- Set due dates
- Mark tasks as complete
- Filter by status
- Organize by priority

---

### 3.10 Uploading Player Database

#### 3.10.1 Overview

The app requires a player database (Excel file) to function. This database contains the list of players you can select when logging calls or reviews.

#### 3.10.2 Upload Process

1. Go to the sidebar
2. Under "Upload Player Database", click "Browse files"
3. Select an Excel file (`.xlsx` or `.xls`)
4. The file will be uploaded and saved permanently
5. The app will automatically reload with the new database

#### 3.10.3 Supported File Formats

- Excel files (`.xlsx`, `.xls`)
- Should contain columns: Player Name, Conference, Team

**Recommended Files:**
- Conference scouting reports (e.g., `Portland Thorns 2025 ACC Scouting Report.xlsx`)
- Shortlist files (e.g., `Portland Thorns 2025 Long Shortlist.xlsx`)

---

## Part 4: Deployment and Access

### 4.1 Local Deployment

#### Prerequisites

1. Python 3.8 or higher
2. Required Python packages (see `requirements.txt`)

#### Installation Steps

1. **Install Dependencies:**
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"
   pip install -r requirements.txt
   ```

2. **Run the App:**
   ```bash
   streamlit run qualitative_capture_app.py
   ```

3. **Access the App:**
   - Open your browser
   - Navigate to `http://localhost:8501`

### 4.2 Streamlit Cloud Deployment

#### Overview

The app is deployed on Streamlit Cloud for easy access from anywhere.

#### Access

- URL: (Provided separately)
- Login credentials: Same as local (MikeNorris / 1234)

#### Features

- Automatic updates when code is pushed to GitHub
- No local setup required
- Accessible from any device with internet
- Secure and reliable hosting

#### Deployment Process (for developers)

1. **Prepare Repository:**
   - Ensure all code is committed to Git
   - Ensure `requirements.txt` exists in repository root
   - Push to GitHub

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository
   - Set Main file path: `Scripts/00_Keep/qualitative_capture_app.py`
   - Click "Deploy!"

3. **App Settings:**
   - App automatically installs dependencies from `requirements.txt`
   - Streamlit Cloud provides public URL
   - App auto-redeploys when code is pushed to GitHub

---

## Troubleshooting

### App Won't Start Locally

**Issue:** Streamlit command not found

**Solution:**
```bash
pip install streamlit
```

**Issue:** Port 8501 already in use

**Solution:**
```bash
streamlit run qualitative_capture_app.py --server.port 8502
```

### Login Issues

**Issue:** Can't log in

**Solution:**
- Verify username: `MikeNorris`
- Verify password: `1234`
- Try clearing browser cache
- Try hard refresh (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

### Data Not Loading

**Issue:** Players not appearing in dropdowns

**Solution:**
1. Upload a player database file in the sidebar
2. Ensure the file is in Excel format (`.xlsx` or `.xls`)
3. Ensure the file contains columns: Player Name, Conference, Team
4. Refresh the page after uploading

**Issue:** Call log not showing

**Solution:**
1. Check that `Qualitative_Data/call_log.csv` exists
2. If file doesn't exist, log a test call to create it
3. Ensure you have read/write permissions for the `Qualitative_Data/` directory

### Export Issues

**Issue:** PDF download not working

**Solution:**
- Ensure ReportLab is installed: `pip install reportlab`
- Check browser download settings
- Try a different browser

**Issue:** CSV export not working

**Solution:**
- Check browser download settings
- Ensure pop-up blockers are disabled
- Try a different browser

### Performance Issues

**Issue:** App is slow

**Solution:**
- Close other browser tabs
- Clear browser cache
- Restart the app
- Check internet connection (for cloud version)

---

## Quick Reference

### Keyboard Shortcuts

**Form Editing:**
- **⌘Z** (Mac) / **Ctrl+Z** (Windows) - Undo last change
- **⌘⇧Z** (Mac) / **Ctrl+Shift+Z** (Windows) - Redo
- **⌘R** (Mac) / **Ctrl+R** (Windows) - Refresh page

**Navigation:**
- **⌘K** (Mac) / **Ctrl+K** (Windows) - Focus search
- **Tab** - Next field
- **Shift+Tab** - Previous field
- **Enter** - Submit form

### File Locations

**Data Files:**
- Call Log: `Qualitative_Data/call_log.csv`
- Video Reviews: `Qualitative_Data/video_reviews.csv`
- Agents: `Qualitative_Data/agents.csv`

**Reports:**
- Conference Reports: `Conference Reports/`
- Player Overviews: `Player Overviews/`

**App Files:**
- Main App: `Scripts/00_Keep/qualitative_capture_app.py`
- Requirements: `requirements.txt`

### Common Tasks

**Log a Phone Call:**
1. Go to "Phone Calls" page
2. Select Conference → Team → Player
3. Fill in call details
4. Click "Save Call Log"

**Add Video Review:**
1. Go to "Video Analysis" page
2. Click "Add Review" tab
3. Select player and fill in details
4. Click "Save Video Review"

**View Player Summary:**
1. Go to "Player Summary" page
2. Select player from dropdown
3. View all phone calls and video reviews

**Upload Player Database:**
1. Go to sidebar
2. Under "Upload Player Database", click "Browse files"
3. Select Excel file
4. Wait for upload confirmation

**Export Data:**
- Call Log: Use "Export to CSV" button in Call History tab
- Player Summary: Use "Download Player Summary PDF" button

### Support Contacts

**Technical Support:**
- Email: daniellevitt32@gmail.com
- Created by: Daniel Levitt

**Questions About:**
- Data collection: Refer to Part 1
- Data processing: Refer to Part 2
- App usage: Refer to Part 3
- Deployment: Refer to Part 4

---

## Appendix A: Data Fields Reference

### Phone Call Fields

**Required:**
- Player Name
- Call Date
- Call Type

**Optional:**
- Agent Name
- Call Duration
- Overall Rating (1-10)
- Recommendation (Yes/No/Maybe/Follow-up)
- Notes
- Follow-up Required
- Follow-up Date

**Assessment Ratings (1-10):**
- Technical Ability
- Physical Attributes
- Tactical Understanding
- Mental Attributes
- Communication
- Coachability
- Team Fit
- Potential

### Video Review Fields

**Required:**
- Player Name
- Review Date

**Optional:**
- Video Type
- Video Source
- Video URL
- Notes

**Analysis Ratings (1-10):**
- Technical Execution
- Decision Making
- Spatial Awareness
- Physical Performance
- Tactical Discipline
- Overall Video Score

---

## Appendix B: Position Profiles

### Hybrid CB (Ball-Playing Center Back)

**Key Metrics:**
- Defensive duels won
- Aerial duels won
- Interceptions
- Clearances
- Passes accurate
- Long passes accurate

### DM Box-To-Box (Defensive Midfielder)

**Key Metrics:**
- Passes accurate
- Passes to final third
- Progressive runs
- Duels won
- Interceptions
- Dribbles successful

### Advanced Playmaker (AM/CM)

**Key Metrics:**
- Passes accurate
- Passes to final third
- xA (Expected Assists)
- Received passes
- Progressive passes
- Key passes

### Touchline Winger (Wide Attacker)

**Key Metrics:**
- Dribbles successful
- Crosses accurate
- Passes to penalty area
- Offensive duels won
- Goals
- xG (Expected Goals)

---

## Appendix C: Conference Information

### Supported Conferences

1. **ACC** (Atlantic Coast Conference) - 17 teams
2. **Big Ten** - 18 teams
3. **Big 12** - 16 teams
4. **SEC** (Southeastern Conference) - 16 teams
5. **Ivy League** - 8 teams

**Total Coverage:** 89 teams across 5 conferences

---

## Document History

- **Version 1.0** (January 2025) - Initial comprehensive manual

---

**End of Manual**

