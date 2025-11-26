# Feature Development Plan - Post-Meeting Customizations

## Overview
This document outlines the implementation plan for the customizations requested after the successful meeting with Mike.

## Features to Implement

### 1. Cloud Storage Functionality
**Goal:** Enable multi-device access (phone/laptop) with cloud storage for call logs and PDFs

**Implementation Approach:**
- Use Google Drive API for cloud storage (works well with Streamlit Cloud)
- Alternative: AWS S3 (more complex setup)
- Store call logs CSV and generated PDFs in a shared Google Drive folder
- Auto-sync after each call log save
- Display sync status in UI

**Files to Modify:**
- `qualitative_capture_app.py` - Add cloud sync functions
- `requirements.txt` - Add `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`

**User Flow:**
1. User saves call log → Auto-uploads to Google Drive
2. Other staff members can access via shared folder
3. App checks for updates on load

---

### 2. Player Visuals Page
**Goal:** Create interactive visualizations page for players (addressing SAP's lack of visuals)

**Implementation Approach:**
- New page: "Player Visuals"
- Select player from dropdown
- Display same visuals as player overview PDF:
  - Radar charts (intensity & accuracy metrics)
  - Scatterplots (player vs similar players)
  - Performance comparison tables
- Use existing `generate_player_charts.py` functions
- Make charts interactive with Streamlit's chart components

**Files to Modify:**
- `qualitative_capture_app.py` - Add new page
- Reuse `generate_player_charts.py` functions

**Visuals to Include:**
- Radar chart: Player vs Conference Avg vs Power Five Avg
- Scatterplot: Player position on key metrics
- Comparison table: Top 5 similar players

---

### 3. Video Analysis Tracker
**Goal:** Track Mike's video/film analysis of players

**Implementation Approach:**
- New page: "Video Analysis Tracker"
- Fields:
  - Player selection
  - Video source/URL
  - Date watched
  - Video type (game film, highlights, training, etc.)
  - Key observations
  - Strengths identified
  - Weaknesses identified
  - Overall rating (1-10)
  - Notes/analysis
- Store in CSV: `video_analysis.csv`
- View history with filters

**Files to Modify:**
- `qualitative_capture_app.py` - Add new page and data structure

**Data Structure:**
```python
{
    'player_name': str,
    'video_source': str,
    'video_url': str (optional),
    'date_watched': date,
    'video_type': str,
    'key_observations': str,
    'strengths': str,
    'weaknesses': str,
    'overall_rating': int (1-10),
    'notes': str,
    'timestamp': datetime
}
```

---

### 4. Calendar Integration
**Goal:** Sync next call dates with Google Calendar and Outlook

**Implementation Approach:**
- Add calendar sync option in "Next Steps" section
- Use Google Calendar API for Gmail
- Use Microsoft Graph API for Outlook
- Store calendar credentials securely (Streamlit secrets)
- Create calendar event with:
  - Title: "Call with [Player Name]"
  - Date/Time: From "Next Call Date"
  - Description: Next steps notes
  - Reminder: 1 day before

**Files to Modify:**
- `qualitative_capture_app.py` - Add calendar sync functions
- `requirements.txt` - Add `google-api-python-client`, `msal` (for Outlook)

**User Flow:**
1. User fills "Next Steps" with date and notes
2. Checkbox: "Add to Calendar"
3. Select calendar: Google or Outlook
4. Authenticate (first time only)
5. Event created automatically

---

### 5. Additional Feature Ideas

#### A. Player Comparison Dashboard
- Side-by-side comparison of multiple players
- Visual comparison charts
- Export comparison report

#### B. Call Analytics Dashboard
- Total calls per player
- Average call duration trends
- Most discussed topics/keywords
- Agent performance metrics

#### C. Automated Follow-up Reminders
- Email/notification system for upcoming calls
- Dashboard showing players needing follow-up

#### D. Integration with Player Overview Generation
- Auto-trigger player overview PDF generation after X calls
- Link call logs directly in player overview PDFs

#### E. Team Collaboration Features
- Comments/notes on players visible to all staff
- Assignment system (who's responsible for which player)
- Activity feed showing recent updates

#### F. Mobile-Optimized Views
- Simplified mobile interface
- Quick call logging from phone
- Push notifications

---

## Implementation Priority

1. **Week 1 Priority:**
   - Player Visuals Page (addresses SAP gap immediately)
   - Video Analysis Tracker (high value for Mike's workflow)

2. **Week 2 Priority:**
   - Cloud Storage (enables team collaboration)
   - Calendar Integration (improves workflow efficiency)

3. **Future Enhancements:**
   - Additional feature ideas from section 5

---

## Technical Considerations

### Authentication & Security
- Use Streamlit secrets for API keys
- OAuth2 for Google/Microsoft authentication
- Secure credential storage

### Data Storage
- Maintain local CSV files (backup)
- Sync to cloud storage
- Version control for data integrity

### Performance
- Cache chart generation
- Lazy load cloud data
- Optimize for mobile devices

---

## Testing Plan

1. **Cloud Storage:**
   - Test upload/download from multiple devices
   - Verify data consistency
   - Test concurrent access

2. **Visuals Page:**
   - Verify all chart types render correctly
   - Test with various players
   - Check mobile responsiveness

3. **Video Tracker:**
   - Test data entry and retrieval
   - Verify filtering/search functionality

4. **Calendar Integration:**
   - Test with both Google and Outlook
   - Verify event creation
   - Test authentication flow

