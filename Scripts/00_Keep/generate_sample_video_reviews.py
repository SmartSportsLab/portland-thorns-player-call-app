#!/usr/bin/env python3
"""
Generate sample video review data for 20 players
This simulates filling out the video review form for testing purposes
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

# Define paths (matching the main app)
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'Qualitative_Data'
video_reviews_file = DATA_DIR / 'video_reviews.csv'
videos_dir = DATA_DIR / 'video_uploads'
videos_dir.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Find player database file (matching the main app logic)
PLAYER_DB_FILE = None

# First, check for uploaded files in DATA_DIR (persistent storage)
if DATA_DIR.exists():
    for uploaded_file in DATA_DIR.glob('*.xlsx'):
        if uploaded_file.exists():
            PLAYER_DB_FILE = uploaded_file
            break
    # Also check for .xls files
    if PLAYER_DB_FILE is None:
        for uploaded_file in DATA_DIR.glob('*.xls'):
            if uploaded_file.exists():
                PLAYER_DB_FILE = uploaded_file
                break

# If no uploaded file, check shortlist files
POSSIBLE_SHORTLIST_FILES = [
    BASE_DIR / 'Portland Thorns 2025 Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Long Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Short Shortlist.xlsx',
    BASE_DIR / 'AI Shortlist.xlsx',
]

if PLAYER_DB_FILE is None:
    for file_path in POSSIBLE_SHORTLIST_FILES:
        if file_path.exists():
            PLAYER_DB_FILE = file_path
            break

# If no shortlist file found, try loading from conference reports
if PLAYER_DB_FILE is None:
    CONFERENCE_REPORTS = [
        BASE_DIR / 'Portland Thorns 2025 ACC Scouting Report.xlsx',
        BASE_DIR / 'Portland Thorns 2025 SEC Scouting Report.xlsx',
        BASE_DIR / 'Portland Thorns 2025 BIG10 Scouting Report.xlsx',
        BASE_DIR / 'Portland Thorns 2025 BIG12 Scouting Report.xlsx',
        BASE_DIR / 'Portland Thorns 2025 IVY Scouting Report.xlsx',
    ]
    # Use first available conference report as fallback
    for report in CONFERENCE_REPORTS:
        if report.exists():
            PLAYER_DB_FILE = report
            break

# Sample data
video_types = ["Game Film", "Highlights", "Training Footage", "Match Replay", "Other"]
video_sources = ["Wyscout", "Hudl", "YouTube", "Team Website", "ESPN+", "NCAA"]
statuses = ["Not Started", "In Progress", "Complete"]
quantitative_matches = ["Strong Match", "Mostly Match", "Some Discrepancies", "Significant Discrepancies"]
recommendations = ["Strong Yes", "Yes", "Maybe", "No", "Strong No"]

# Sample observations
sample_observations = [
    "Excellent first touch and ball control. Shows composure under pressure.",
    "Strong defensive positioning. Reads the game well and anticipates play.",
    "Impressive work rate. Covers a lot of ground and tracks back consistently.",
    "Good passing range. Can switch play effectively and find teammates in space.",
    "Needs improvement in decision-making. Sometimes holds onto the ball too long.",
    "Strong physical presence. Wins aerial duels and physical battles.",
    "Creative in attack. Makes intelligent runs and creates scoring opportunities.",
    "Solid technical foundation. Clean passing and good first touch.",
    "Shows leadership qualities. Communicates well and organizes teammates.",
    "Versatile player. Can play multiple positions effectively."
]

sample_strengths = [
    "Excellent technical ability, strong passing accuracy, good vision",
    "Physical presence, aerial ability, strong in duels",
    "Work rate, stamina, covers ground effectively",
    "Tactical awareness, positioning, game intelligence",
    "Creativity, dribbling ability, 1v1 skills"
]

sample_weaknesses = [
    "Decision-making under pressure needs improvement",
    "Pace could be better for this level",
    "Sometimes loses concentration in defensive transitions",
    "Left foot needs development",
    "Aerial duels could be stronger"
]

sample_red_flags = [
    "Minor concern about injury history - monitor closely",
    "Some attitude questions from previous coaches",
    "None observed",
    "Potential fitness concerns - needs conditioning work",
    ""
]

# Load player database to get real player names (matching the main app logic)
available_players = []
if PLAYER_DB_FILE and PLAYER_DB_FILE.exists():
    try:
        # Try different header rows (some files use header=2 for merged headers)
        for header_row in [2, 1, 0]:
            try:
                df = pd.read_excel(PLAYER_DB_FILE, sheet_name=None, header=header_row)
                found_players = False
                
                for sheet_name, sheet_df in df.items():
                    # Skip non-data sheets
                    if sheet_name.startswith('Sheet') or 'Summary' in sheet_name:
                        continue
                    if 'Player' in sheet_df.columns:
                        found_players = True
                        for _, row in sheet_df.iterrows():
                            player_name = row.get('Player')
                            if pd.notna(player_name) and str(player_name).strip():
                                player_name_str = str(player_name).strip()
                                if player_name_str not in available_players:
                                    available_players.append(player_name_str)
                
                # If we found players, break (success)
                if found_players and available_players:
                    break
            except Exception as inner_e:
                # Try next header row if this one fails
                continue
        
        if not available_players:
            print(f"⚠️ No players found in {PLAYER_DB_FILE}")
            available_players = [f"Player {i+1}" for i in range(20)]
        else:
            print(f"✅ Loaded {len(available_players)} players from database")
    except Exception as e:
        print(f"⚠️ Error loading player database: {e}")
        available_players = [f"Player {i+1}" for i in range(20)]
else:
    print(f"⚠️ Player database file not found. Using placeholder names.")
    available_players = [f"Player {i+1}" for i in range(20)]

# Select 20 random players (or use all if less than 20)
if len(available_players) >= 20:
    selected_players = random.sample(available_players, 20)
else:
    selected_players = available_players + [f"Player {i+1}" for i in range(20 - len(available_players))]

# Generate reviews
reviews = []
base_date = datetime.now() - timedelta(days=30)

for i, player_name in enumerate(selected_players):
    # Vary the review dates
    review_date = base_date + timedelta(days=random.randint(0, 30))
    
    # Create video file path (simulated)
    safe_player_name = player_name.replace('/', '_').replace('\\', '_')
    timestamp = review_date.strftime('%Y%m%d_%H%M%S')
    video_filename = f"{safe_player_name}_{timestamp}.mp4"
    video_file_path = str(videos_dir / video_filename)
    
    # Assign status with some logic (earlier reviews more likely to be complete)
    days_ago = (datetime.now() - review_date).days
    if days_ago > 20:
        status = random.choice(["Complete", "Complete", "Complete", "In Progress"])
    elif days_ago > 10:
        status = random.choice(["Complete", "In Progress", "In Progress", "Not Started"])
    else:
        status = random.choice(["In Progress", "Not Started", "Not Started", "Complete"])
    
    # Video score correlates with recommendation
    if status == "Complete":
        video_score = random.randint(6, 10)
        if video_score >= 8:
            recommendation = random.choice(["Strong Yes", "Yes"])
        elif video_score >= 6:
            recommendation = random.choice(["Yes", "Maybe"])
        else:
            recommendation = random.choice(["Maybe", "No"])
    else:
        video_score = random.randint(1, 10)
        recommendation = random.choice(recommendations)
    
    review = {
        'Player Name': player_name,
        'Review Date': review_date.strftime('%Y-%m-%d'),
        'Video Type': random.choice(video_types),
        'Video Source': random.choice(video_sources),
        'Video URL': f"https://example.com/video/{i+1}" if random.random() > 0.5 else '',
        'Video File Path': video_file_path if random.random() > 0.7 else '',  # 30% have video files
        'Games Reviewed': random.choice([
            "vs Duke, vs UNC",
            "vs Stanford, vs UCLA",
            "vs Virginia, vs Clemson",
            "vs Michigan, vs Ohio State",
            "vs Alabama, vs Georgia",
            ""
        ]),
        'Video Score': video_score,
        'Status': status,
        'Quantitative Match': random.choice(quantitative_matches),
        'Key Observations': random.choice(sample_observations),
        'Strengths Identified': random.choice(sample_strengths),
        'Weaknesses Identified': random.choice(sample_weaknesses),
        'Red Flags': random.choice(sample_red_flags),
        'Recommendation': recommendation,
        'Notes': f"Additional notes for {player_name}. Review completed on {review_date.strftime('%Y-%m-%d')}.",
        'Created At': review_date.strftime('%Y-%m-%d %H:%M:%S')
    }
    reviews.append(review)

# Create DataFrame and save
df = pd.DataFrame(reviews)
df.to_csv(video_reviews_file, index=False)

print(f"✅ Generated {len(reviews)} sample video reviews")
print(f"📁 Saved to: {video_reviews_file}")
print(f"\n📊 Summary:")
print(f"   - Total Reviews: {len(df)}")
print(f"   - Complete: {len(df[df['Status'] == 'Complete'])}")
print(f"   - In Progress: {len(df[df['Status'] == 'In Progress'])}")
print(f"   - Not Started: {len(df[df['Status'] == 'Not Started'])}")
print(f"   - Average Score: {df['Video Score'].mean():.1f}/10")
print(f"\n🎬 Sample players:")
for i, player in enumerate(selected_players[:5]):
    player_review = df[df['Player Name'] == player].iloc[0]
    print(f"   {i+1}. {player} - {player_review['Status']} - Score: {player_review['Video Score']}/10")

