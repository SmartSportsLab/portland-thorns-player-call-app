#!/usr/bin/env python3
"""
Generate sample call log and video review data
Ensures 80% of players have both at least one phone call AND at least one video review
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

# Define paths (matching the main app)
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'Qualitative_Data'
call_log_file = DATA_DIR / 'call_log.csv'
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

# Load player database to get real player names
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
            available_players = [f"Player {i+1}" for i in range(50)]
        else:
            print(f"✅ Loaded {len(available_players)} players from database")
    except Exception as e:
        print(f"⚠️ Error loading player database: {e}")
        available_players = [f"Player {i+1}" for i in range(50)]
else:
    print(f"⚠️ Player database file not found. Using placeholder names.")
    available_players = [f"Player {i+1}" for i in range(50)]

# Select players for sample data (use at least 30, or all if less)
num_players = max(30, min(len(available_players), 50))
if len(available_players) >= num_players:
    selected_players = random.sample(available_players, num_players)
else:
    selected_players = available_players + [f"Player {i+1}" for i in range(num_players - len(available_players))]

# Calculate how many players should have both (80%)
num_with_both = int(len(selected_players) * 0.8)
players_with_both = random.sample(selected_players, num_with_both)
players_without_both = [p for p in selected_players if p not in players_with_both]

print(f"\n📊 Sample Data Strategy:")
print(f"   - Total Players: {len(selected_players)}")
print(f"   - Players with BOTH call log AND video review: {len(players_with_both)} ({len(players_with_both)/len(selected_players)*100:.1f}%)")
print(f"   - Players with only one or neither: {len(players_without_both)} ({len(players_without_both)/len(selected_players)*100:.1f}%)")

# Sample data options
call_types = ["Initial Contact", "Follow-up", "Agent Call", "Player Call", "Team Meeting"]
recommendations = ["Strong Yes", "Yes", "Maybe", "No", "Strong No"]
interest_levels = ["Very High", "High", "Medium", "Low", "Very Low"]
video_types = ["Game Film", "Highlights", "Training Footage", "Match Replay", "Other"]
video_sources = ["Wyscout", "Hudl", "YouTube", "Team Website", "ESPN+", "NCAA"]
statuses = ["Not Started", "In Progress", "Complete"]
quantitative_matches = ["Strong Match", "Mostly Match", "Some Discrepancies", "Significant Discrepancies"]

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

# Generate call logs
print(f"\n📞 Generating call logs...")
call_logs = []
base_date = datetime.now() - timedelta(days=60)

# For players with both, ensure they have at least one call
for i, player_name in enumerate(players_with_both):
    num_calls = random.randint(1, 3)  # 1-3 calls per player
    for call_num in range(num_calls):
        call_date = base_date + timedelta(days=random.randint(0, 60))
        
        # Calculate assessment grade based on ratings
        communication = random.randint(6, 10)
        maturity = random.randint(6, 10)
        coachability = random.randint(6, 10)
        leadership = random.randint(5, 10)
        work_ethic = random.randint(6, 10)
        confidence = random.randint(5, 10)
        tactical_knowledge = random.randint(6, 10)
        team_fit = random.randint(6, 10)
        overall_rating = random.randint(6, 10)
        
        total_score = (communication + maturity + coachability + leadership + 
                      work_ethic + confidence + tactical_knowledge + team_fit + overall_rating)
        percentage = (total_score / 90) * 100
        
        if percentage >= 90:
            grade = 'A'
        elif percentage >= 80:
            grade = 'B'
        elif percentage >= 70:
            grade = 'C'
        elif percentage >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        if overall_rating >= 8:
            recommendation = random.choice(["Strong Yes", "Yes"])
        elif overall_rating >= 6:
            recommendation = random.choice(["Yes", "Maybe"])
        else:
            recommendation = random.choice(["Maybe", "No", "Strong No"])
        
        call_log = {
            'Call Number': len(call_logs) + 1,
            'Player Name': player_name,
            'Call Date': call_date.strftime('%Y-%m-%d'),
            'Call Type': random.choice(call_types),
            'Agent Name': f"Agent {random.randint(1, 20)}",
            'Team': random.choice(["Duke", "UNC", "Stanford", "UCLA", "Virginia", "Clemson"]),
            'Conference': random.choice(["ACC", "SEC", "BIG10", "BIG12", "PAC12"]),
            'Position Profile': random.choice(["Forward", "Midfielder", "Defender", "Goalkeeper"]),
            'Communication': communication,
            'Maturity': maturity,
            'Coachability': coachability,
            'Leadership': leadership,
            'Work Ethic': work_ethic,
            'Confidence': confidence,
            'Tactical Knowledge': tactical_knowledge,
            'Team Fit': team_fit,
            'Overall Rating': overall_rating,
            'Assessment Grade': grade,
            'Recommendation': recommendation,
            'Interest Level': random.choice(interest_levels),
            'Call Notes': f"Productive conversation with {player_name}. Discussed opportunities and fit.",
            'Created At': call_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        call_logs.append(call_log)

# For players without both, randomly assign some to have only calls
for i, player_name in enumerate(players_without_both):
    if random.random() < 0.5:  # 50% chance of having a call
        call_date = base_date + timedelta(days=random.randint(0, 60))
        
        communication = random.randint(5, 10)
        maturity = random.randint(5, 10)
        coachability = random.randint(5, 10)
        leadership = random.randint(4, 10)
        work_ethic = random.randint(5, 10)
        confidence = random.randint(4, 10)
        tactical_knowledge = random.randint(5, 10)
        team_fit = random.randint(5, 10)
        overall_rating = random.randint(5, 10)
        
        total_score = (communication + maturity + coachability + leadership + 
                      work_ethic + confidence + tactical_knowledge + team_fit + overall_rating)
        percentage = (total_score / 90) * 100
        
        if percentage >= 90:
            grade = 'A'
        elif percentage >= 80:
            grade = 'B'
        elif percentage >= 70:
            grade = 'C'
        elif percentage >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        if overall_rating >= 8:
            recommendation = random.choice(["Strong Yes", "Yes"])
        elif overall_rating >= 6:
            recommendation = random.choice(["Yes", "Maybe"])
        else:
            recommendation = random.choice(["Maybe", "No", "Strong No"])
        
        call_log = {
            'Call Number': len(call_logs) + 1,
            'Player Name': player_name,
            'Call Date': call_date.strftime('%Y-%m-%d'),
            'Call Type': random.choice(call_types),
            'Agent Name': f"Agent {random.randint(1, 20)}",
            'Team': random.choice(["Duke", "UNC", "Stanford", "UCLA", "Virginia", "Clemson"]),
            'Conference': random.choice(["ACC", "SEC", "BIG10", "BIG12", "PAC12"]),
            'Position Profile': random.choice(["Forward", "Midfielder", "Defender", "Goalkeeper"]),
            'Communication': communication,
            'Maturity': maturity,
            'Coachability': coachability,
            'Leadership': leadership,
            'Work Ethic': work_ethic,
            'Confidence': confidence,
            'Tactical Knowledge': tactical_knowledge,
            'Team Fit': team_fit,
            'Overall Rating': overall_rating,
            'Assessment Grade': grade,
            'Recommendation': recommendation,
            'Interest Level': random.choice(interest_levels),
            'Call Notes': f"Initial contact with {player_name}.",
            'Created At': call_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        call_logs.append(call_log)

# Generate video reviews
print(f"🎥 Generating video reviews...")
video_reviews = []
base_date = datetime.now() - timedelta(days=30)

# For players with both, ensure they have at least one video review
for i, player_name in enumerate(players_with_both):
    num_reviews = random.randint(1, 2)  # 1-2 reviews per player
    for review_num in range(num_reviews):
        review_date = base_date + timedelta(days=random.randint(0, 30))
        
        # Create video file path (simulated)
        safe_player_name = player_name.replace('/', '_').replace('\\', '_')
        timestamp = review_date.strftime('%Y%m%d_%H%M%S')
        video_filename = f"{safe_player_name}_{timestamp}.mp4"
        video_file_path = str(videos_dir / video_filename)
        
        # Assign status with some logic
        days_ago = (datetime.now() - review_date).days
        if days_ago > 20:
            status = random.choice(["Complete", "Complete", "Complete", "In Progress"])
        elif days_ago > 10:
            status = random.choice(["Complete", "In Progress", "In Progress", "Not Started"])
        else:
            status = random.choice(["In Progress", "Not Started", "Not Started", "Complete"])
        
        # Performance metrics
        technical_ability = random.randint(6, 10)
        tactical_awareness = random.randint(6, 10)
        decision_making = random.randint(6, 10)
        physical_attributes = random.randint(6, 10)
        work_rate = random.randint(6, 10)
        communication = random.randint(6, 10)
        leadership = random.randint(5, 10)
        composure = random.randint(6, 10)
        overall_video_rating = random.randint(6, 10)
        
        total_video_score = (technical_ability + tactical_awareness + decision_making +
                            physical_attributes + work_rate + communication +
                            leadership + composure + overall_video_rating)
        max_possible = 9 * 10
        video_percentage = (total_video_score / max_possible) * 100
        
        if video_percentage >= 90:
            video_grade = 'A'
        elif video_percentage >= 80:
            video_grade = 'B'
        elif video_percentage >= 70:
            video_grade = 'C'
        elif video_percentage >= 60:
            video_grade = 'D'
        else:
            video_grade = 'F'
        
        video_score = random.randint(6, 10)
        if video_score >= 8:
            recommendation = random.choice(["Strong Yes", "Yes"])
        elif video_score >= 6:
            recommendation = random.choice(["Yes", "Maybe"])
        else:
            recommendation = random.choice(["Maybe", "No"])
        
        review = {
            'Player Name': player_name,
            'Review Date': review_date.strftime('%Y-%m-%d'),
            'Video Type': random.choice(video_types),
            'Video Source': random.choice(video_sources),
            'Video URL': f"https://example.com/video/{i+1}" if random.random() > 0.5 else '',
            'Video File Path': video_file_path if random.random() > 0.7 else '',
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
            'Technical Ability': technical_ability,
            'Tactical Awareness': tactical_awareness,
            'Decision Making': decision_making,
            'Physical Attributes': physical_attributes,
            'Work Rate': work_rate,
            'Communication': communication,
            'Leadership': leadership,
            'Composure': composure,
            'Overall Video Rating': overall_video_rating,
            'Total Video Score': total_video_score,
            'Video Percentage': round(video_percentage, 1),
            'Video Grade': video_grade,
            'Key Observations': random.choice(sample_observations),
            'Strengths Identified': random.choice(sample_strengths),
            'Weaknesses Identified': random.choice(sample_weaknesses),
            'Red Flags': random.choice(sample_red_flags),
            'Recommendation': recommendation,
            'Additional Notes': f"Additional notes for {player_name}. Review completed on {review_date.strftime('%Y-%m-%d')}.",
            'Created At': review_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        video_reviews.append(review)

# For players without both, randomly assign some to have only video reviews
for i, player_name in enumerate(players_without_both):
    if random.random() < 0.3:  # 30% chance of having only a video review
        review_date = base_date + timedelta(days=random.randint(0, 30))
        
        safe_player_name = player_name.replace('/', '_').replace('\\', '_')
        timestamp = review_date.strftime('%Y%m%d_%H%M%S')
        video_filename = f"{safe_player_name}_{timestamp}.mp4"
        video_file_path = str(videos_dir / video_filename)
        
        days_ago = (datetime.now() - review_date).days
        if days_ago > 20:
            status = random.choice(["Complete", "Complete", "In Progress"])
        else:
            status = random.choice(["In Progress", "Not Started", "Complete"])
        
        technical_ability = random.randint(5, 10)
        tactical_awareness = random.randint(5, 10)
        decision_making = random.randint(5, 10)
        physical_attributes = random.randint(5, 10)
        work_rate = random.randint(5, 10)
        communication = random.randint(5, 10)
        leadership = random.randint(4, 10)
        composure = random.randint(5, 10)
        overall_video_rating = random.randint(5, 10)
        
        total_video_score = (technical_ability + tactical_awareness + decision_making +
                            physical_attributes + work_rate + communication +
                            leadership + composure + overall_video_rating)
        max_possible = 9 * 10
        video_percentage = (total_video_score / max_possible) * 100
        
        if video_percentage >= 90:
            video_grade = 'A'
        elif video_percentage >= 80:
            video_grade = 'B'
        elif video_percentage >= 70:
            video_grade = 'C'
        elif video_percentage >= 60:
            video_grade = 'D'
        else:
            video_grade = 'F'
        
        video_score = random.randint(5, 10)
        if video_score >= 8:
            recommendation = random.choice(["Strong Yes", "Yes"])
        elif video_score >= 6:
            recommendation = random.choice(["Yes", "Maybe"])
        else:
            recommendation = random.choice(["Maybe", "No"])
        
        review = {
            'Player Name': player_name,
            'Review Date': review_date.strftime('%Y-%m-%d'),
            'Video Type': random.choice(video_types),
            'Video Source': random.choice(video_sources),
            'Video URL': f"https://example.com/video/{i+1}" if random.random() > 0.5 else '',
            'Video File Path': video_file_path if random.random() > 0.7 else '',
            'Games Reviewed': random.choice([
                "vs Duke, vs UNC",
                "vs Stanford, vs UCLA",
                ""
            ]),
            'Video Score': video_score,
            'Status': status,
            'Quantitative Match': random.choice(quantitative_matches),
            'Technical Ability': technical_ability,
            'Tactical Awareness': tactical_awareness,
            'Decision Making': decision_making,
            'Physical Attributes': physical_attributes,
            'Work Rate': work_rate,
            'Communication': communication,
            'Leadership': leadership,
            'Composure': composure,
            'Overall Video Rating': overall_video_rating,
            'Total Video Score': total_video_score,
            'Video Percentage': round(video_percentage, 1),
            'Video Grade': video_grade,
            'Key Observations': random.choice(sample_observations),
            'Strengths Identified': random.choice(sample_strengths),
            'Weaknesses Identified': random.choice(sample_weaknesses),
            'Red Flags': random.choice(sample_red_flags),
            'Recommendation': recommendation,
            'Additional Notes': f"Additional notes for {player_name}.",
            'Created At': review_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        video_reviews.append(review)

# Save call logs
call_logs_df = pd.DataFrame(call_logs)
call_logs_df.to_csv(call_log_file, index=False)

# Save video reviews
video_reviews_df = pd.DataFrame(video_reviews)
video_reviews_df.to_csv(video_reviews_file, index=False)

# Calculate statistics
call_log_players = set(call_logs_df['Player Name'].unique())
video_review_players = set(video_reviews_df['Player Name'].unique())
players_with_both_actual = call_log_players & video_review_players
players_with_only_calls = call_log_players - video_review_players
players_with_only_videos = video_review_players - call_log_players

print(f"\n✅ Generated sample data!")
print(f"📁 Call logs saved to: {call_log_file}")
print(f"📁 Video reviews saved to: {video_reviews_file}")
print(f"\n📊 Final Statistics:")
print(f"   - Total Call Logs: {len(call_logs_df)}")
print(f"   - Total Video Reviews: {len(video_reviews_df)}")
print(f"   - Players with Call Logs: {len(call_log_players)}")
print(f"   - Players with Video Reviews: {len(video_review_players)}")
print(f"   - Players with BOTH: {len(players_with_both_actual)} ({len(players_with_both_actual)/len(selected_players)*100:.1f}%)")
print(f"   - Players with only Calls: {len(players_with_only_calls)}")
print(f"   - Players with only Videos: {len(players_with_only_videos)}")
print(f"\n🎯 Sample players with both:")
for i, player in enumerate(list(players_with_both_actual)[:5]):
    player_calls = len(call_logs_df[call_logs_df['Player Name'] == player])
    player_videos = len(video_reviews_df[video_reviews_df['Player Name'] == player])
    print(f"   {i+1}. {player} - {player_calls} call(s), {player_videos} review(s)")






