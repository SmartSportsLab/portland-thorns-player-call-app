#!/usr/bin/env python3
"""
Enhance existing player overview PDFs with qualitative information from call logs.
Combines quantitative player data with Mike's call notes and assessments.
"""

import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# Data paths
BASE_DIR = Path('/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search')
CALL_LOG_FILE = BASE_DIR / 'Qualitative_Data' / 'call_log.csv'
PLAYER_OVERVIEWS_DIR = BASE_DIR / 'Player Overviews'

def load_call_log_data():
    """Load call log data from CSV."""
    try:
        if CALL_LOG_FILE.exists():
            df = pd.read_csv(CALL_LOG_FILE)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading call log: {e}")
        return pd.DataFrame()

def get_player_call_data(player_name, team=None):
    """Get all call log entries for a specific player."""
    call_log_df = load_call_log_data()
    if call_log_df.empty:
        return []
    
    # Try to match player name (flexible matching)
    player_name_clean = str(player_name).strip().lower()
    
    # Filter by player name (handle NaN values)
    if 'Player Name' not in call_log_df.columns:
        return []
    
    # Convert Player Name to string and handle NaN
    call_log_df = call_log_df.copy()  # Avoid SettingWithCopyWarning
    call_log_df['Player Name'] = call_log_df['Player Name'].astype(str).replace('nan', '')
    matches = call_log_df[
        call_log_df['Player Name'].str.lower().str.strip() == player_name_clean
    ].copy()
    
    # If team provided, also filter by team (but allow empty team values in call log)
    if team and len(matches) > 0:
        team_clean = str(team).strip().lower()
        # Convert Team to string and handle NaN
        matches['Team'] = matches['Team'].astype(str).replace('nan', '')
        # Match if team matches OR if team is empty in call log (flexible matching)
        team_matches = (
            matches['Team'].str.lower().str.strip() == team_clean
        ) | (
            matches['Team'].str.strip() == ''
        )
        matches = matches[team_matches]
    
    # Sort by call date (most recent first)
    if len(matches) > 0 and 'Call Date' in matches.columns:
        matches = matches.sort_values('Call Date', ascending=False)
    
    return matches.to_dict('records')

def format_call_assessment_summary(call_data):
    """Format player assessment scores into a summary."""
    assessments = []
    
    # Get assessment scores
    scores = {
        'Communication': call_data.get('Communication', ''),
        'Maturity': call_data.get('Maturity', ''),
        'Coachability': call_data.get('Coachability', ''),
        'Leadership': call_data.get('Leadership', ''),
        'Work Ethic': call_data.get('Work Ethic', ''),
        'Confidence': call_data.get('Confidence', ''),
        'Tactical Knowledge': call_data.get('Tactical Knowledge', ''),
        'Team Fit': call_data.get('Team Fit', ''),
        'Overall Rating': call_data.get('Overall Rating', '')
    }
    
    # Filter out empty scores
    valid_scores = {k: v for k, v in scores.items() if v and str(v).strip() != '' and str(v) != 'nan'}
    
    if valid_scores:
        score_items = [f"{k}: {v}/10" for k, v in valid_scores.items()]
        assessments.append(f"**Assessment Scores**: {', '.join(score_items)}")
    
    # Add total score if available
    total_score = call_data.get('Assessment Total Score', '')
    percentage = call_data.get('Assessment Percentage', '')
    grade = call_data.get('Assessment Grade', '')
    
    if total_score and str(total_score).strip() != '' and str(total_score) != 'nan':
        score_line = f"**Total Score**: {total_score}/90"
        if percentage and str(percentage).strip() != '' and str(percentage) != 'nan':
            score_line += f" ({percentage}%)"
        if grade and str(grade).strip() != '' and str(grade) != 'nan':
            score_line += f" | **Grade**: {grade}"
        assessments.append(score_line)
    
    return assessments

def format_agent_assessment(call_data):
    """Format agent assessment information."""
    agent_info = []
    
    agent_name = call_data.get('Agent Name', '')
    relationship = call_data.get('Relationship', '')
    
    if agent_name and str(agent_name).strip() != '' and str(agent_name) != 'nan':
        agent_line = f"**Agent**: {agent_name}"
        if relationship and str(relationship).strip() != '' and str(relationship) != 'nan':
            agent_line += f" ({relationship})"
        agent_info.append(agent_line)
    
    # Agent scores
    agent_scores = {
        'Professionalism': call_data.get('Agent Professionalism', ''),
        'Responsiveness': call_data.get('Agent Responsiveness', ''),
        'Expectations': call_data.get('Agent Expectations', ''),
        'Transparency': call_data.get('Agent Transparency', ''),
        'Negotiation Style': call_data.get('Agent Negotiation Style', '')
    }
    
    valid_agent_scores = {k: v for k, v in agent_scores.items() if v and str(v).strip() != '' and str(v) != 'nan'}
    
    if valid_agent_scores:
        score_items = [f"{k}: {v}/10" for k, v in valid_agent_scores.items()]
        agent_info.append(f"**Agent Assessment**: {', '.join(score_items)}")
    
    return agent_info

def generate_call_notes_section(call_entries):
    """Generate markdown section for call notes and assessments."""
    if not call_entries:
        return None
    
    lines = []
    lines.append("## Call Notes & Assessment")
    lines.append("")
    
    # Process each call entry (most recent first)
    for idx, call in enumerate(call_entries, 1):
        call_date = call.get('Call Date', 'Unknown')
        call_type = call.get('Call Type', 'Unknown')
        
        lines.append(f"### Call #{idx} - {call_date}")
        lines.append("")
        
        # Call details
        call_details = []
        if call_type and str(call_type).strip() != '' and str(call_type) != 'nan':
            call_details.append(f"**Type**: {call_type}")
        
        duration = call.get('Duration (min)', '')
        if duration and str(duration).strip() != '' and str(duration) != 'nan':
            call_details.append(f"**Duration**: {duration} min")
        
        participants = call.get('Participants', '')
        if participants and str(participants).strip() != '' and str(participants) != 'nan':
            call_details.append(f"**Participants**: {participants}")
        
        if call_details:
            lines.append(' | '.join(call_details))
            lines.append("")
        
        # Player Assessment
        assessment_summary = format_call_assessment_summary(call)
        if assessment_summary:
            lines.extend(assessment_summary)
            lines.append("")
        
        # Agent Assessment
        agent_assessment = format_agent_assessment(call)
        if agent_assessment:
            lines.extend(agent_assessment)
            lines.append("")
        
        # Key talking points
        key_points = call.get('Key Talking Points', '')
        if key_points and str(key_points).strip() != '' and str(key_points) != 'nan':
            lines.append(f"**Key Talking Points**: {key_points}")
            lines.append("")
        
        # Interest level and timeline
        interest_info = []
        interest_level = call.get('Interest Level', '')
        if interest_level and str(interest_level).strip() != '' and str(interest_level) != 'nan':
            interest_info.append(f"**Interest Level**: {interest_level}")
        
        timeline = call.get('Timeline', '')
        if timeline and str(timeline).strip() != '' and str(timeline) != 'nan':
            interest_info.append(f"**Timeline**: {timeline}")
        
        if interest_info:
            lines.append(' | '.join(interest_info))
            lines.append("")
        
        # Personality insights
        personality_sections = []
        
        how_they_carry = call.get('How They Carry Themselves', '')
        if how_they_carry and str(how_they_carry).strip() != '' and str(how_they_carry) != 'nan':
            personality_sections.append(f"**How they carry themselves**: {how_they_carry}")
        
        how_they_view = call.get('How They View Themselves', '')
        if how_they_view and str(how_they_view).strip() != '' and str(how_they_view) != 'nan':
            personality_sections.append(f"**How they view themselves**: {how_they_view}")
        
        what_important = call.get('What Is Important To Them', '')
        if what_important and str(what_important).strip() != '' and str(what_important) != 'nan':
            personality_sections.append(f"**What's important**: {what_important}")
        
        mindset = call.get('Mindset Towards Growth', '')
        if mindset and str(mindset).strip() != '' and str(mindset) != 'nan':
            personality_sections.append(f"**Growth mindset**: {mindset}")
        
        if personality_sections:
            lines.append("**Personality Insights**:")
            for section in personality_sections:
                lines.append(f"- {section}")
            lines.append("")
        
        # Red flags
        red_flags = call.get('Red Flags', '')
        red_flag_severity = call.get('Red Flag Severity', '')
        if red_flags and str(red_flags).strip() != '' and str(red_flags) != 'nan':
            red_flag_line = f"**Red Flags**: {red_flags}"
            if red_flag_severity and str(red_flag_severity).strip() != '' and str(red_flag_severity) != 'nan' and red_flag_severity != 'None':
                red_flag_line += f" (Severity: {red_flag_severity})"
            lines.append(red_flag_line)
            lines.append("")
        
        # Overall assessment
        recommendation = call.get('Recommendation', '')
        summary_notes = call.get('Summary Notes', '')
        
        if recommendation and str(recommendation).strip() != '' and str(recommendation) != 'nan':
            lines.append(f"**Recommendation**: {recommendation}")
        
        if summary_notes and str(summary_notes).strip() != '' and str(summary_notes) != 'nan':
            lines.append(f"**Summary**: {summary_notes}")
            lines.append("")
        
        # Add separator between calls (except last one)
        if idx < len(call_entries):
            lines.append("---")
            lines.append("")
    
    return '\n'.join(lines)

def enhance_existing_pdf(player_name, team=None, position_profile=None):
    """
    Enhance an existing player overview PDF with call log data.
    Reads the existing PDF, extracts content, adds call notes section, regenerates PDF.
    """
    # For now, we'll need to regenerate from source data
    # This is a placeholder - full implementation would require reading existing PDF
    # or regenerating from the original data source
    
    # Get call data
    call_entries = get_player_call_data(player_name, team)
    
    if not call_entries:
        print(f"No call data found for {player_name}")
        return None
    
    # Generate call notes section
    call_section = generate_call_notes_section(call_entries)
    
    if not call_section:
        return None
    
    return call_section

def main():
    """Main function to enhance player overviews with call data."""
    print("ENHANCING PLAYER OVERVIEWS WITH CALL LOG DATA")
    print("=" * 60)
    
    # Load call log
    call_log_df = load_call_log_data()
    
    if call_log_df.empty:
        print("❌ No call log data found. Please ensure call logs have been saved.")
        return
    
    print(f"✅ Loaded {len(call_log_df)} call log entries")
    
    # Get unique players with calls
    players_with_calls = call_log_df['Player Name'].unique()
    print(f"📋 Found {len(players_with_calls)} players with call data")
    
    # For each player, enhance their overview
    enhanced_count = 0
    
    for player_name in players_with_calls:
        player_calls = get_player_call_data(player_name)
        if player_calls:
            print(f"\n📞 Processing {player_name} ({len(player_calls)} call(s))...")
            call_section = generate_call_notes_section(player_calls)
            if call_section:
                print(f"  ✅ Generated call notes section")
                enhanced_count += 1
    
    print(f"\n✅ Enhanced {enhanced_count} player overviews with call data")
    print("\n💡 Note: To fully integrate this into PDFs, run the player overview generation script")
    print("   with the enhanced call data integration.")

if __name__ == "__main__":
    main()

