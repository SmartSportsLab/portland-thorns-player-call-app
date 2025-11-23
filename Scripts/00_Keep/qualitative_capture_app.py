#!/usr/bin/env python3
"""
Streamlit app for capturing qualitative information from player/agent calls.
Stores data in CSV format for easy export and sharing.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import json
from io import BytesIO
import base64

# ReportLab for PDF generation (works on Streamlit Cloud)
PDF_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Portland Thorns - Call Log",
    page_icon="⚽",
    layout="wide"
)

# Data storage
BASE_DIR = Path('/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search')
DATA_DIR = BASE_DIR / 'Qualitative_Data'
DATA_DIR.mkdir(exist_ok=True)
CALL_LOG_FILE = DATA_DIR / 'call_log.csv'
AGENT_DB_FILE = DATA_DIR / 'agents.csv'
DRAFT_FILE = DATA_DIR / 'call_log_draft.json'

# Try multiple possible shortlist file names
POSSIBLE_SHORTLIST_FILES = [
    BASE_DIR / 'Portland Thorns 2025 Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Long Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Short Shortlist.xlsx',
    BASE_DIR / 'AI Shortlist.xlsx',
]

# Find the first existing shortlist file
PLAYER_DB_FILE = None
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

# Load player database with full info
@st.cache_data
def load_player_database():
    """Load player names from shortlist file."""
    try:
        if PLAYER_DB_FILE and PLAYER_DB_FILE.exists():
            # Try different header rows (some files use header=2 for merged headers)
            players = []
            for header_row in [2, 1, 0]:
                try:
                    df = pd.read_excel(PLAYER_DB_FILE, sheet_name=None, header=header_row)
                    for sheet_name, sheet_df in df.items():
                        # Skip non-data sheets
                        if sheet_name.startswith('Sheet') or 'Summary' in sheet_name:
                            continue
                        if 'Player' in sheet_df.columns:
                            # Get players from this sheet
                            sheet_players = sheet_df['Player'].dropna().unique().tolist()
                            players.extend([str(p) for p in sheet_players if str(p).strip()])
                    
                    # If we found players, break (success)
                    if players:
                        break
                except:
                    continue
            
            return sorted(list(set(players)))
    except Exception as e:
        st.error(f"Error loading player database: {e}")
        import traceback
        st.error(traceback.format_exc())
    return []

@st.cache_data
def load_player_info():
    """Load full player information including team and conference."""
    try:
        if PLAYER_DB_FILE and PLAYER_DB_FILE.exists():
            player_info_dict = {}
            
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
                                if pd.notna(player_name):
                                    team = row.get('Team', '')
                                    conference = row.get('Conference', '')
                                    
                                    # If conference not in columns, try to extract from team name
                                    if not conference or pd.isna(conference) or conference == '':
                                        team_str = str(team).upper()
                                        
                                        # ACC teams
                                        acc_teams = ['DUKE', 'NORTH CAROLINA', 'VIRGINIA', 'CLEMSON', 'FLORIDA STATE', 'VIRGINIA TECH', 'SYRACUSE', 'LOUISVILLE', 'PITTSBURGH', 'BOSTON COLLEGE', 'NC STATE', 'WAKE FOREST', 'MIAMI', 'NOTRE DAME']
                                        # SEC teams
                                        sec_teams = ['ALABAMA', 'GEORGIA', 'FLORIDA', 'LSU', 'TENNESSEE', 'ARKANSAS', 'SOUTH CAROLINA', 'MISSISSIPPI', 'MISSISSIPPI STATE', 'AUBURN', 'KENTUCKY', 'VANDERBILT', 'MISSOURI', 'TEXAS A&M']
                                        # Big Ten teams
                                        big10_teams = ['MICHIGAN', 'OHIO STATE', 'PENN STATE', 'MICHIGAN STATE', 'WISCONSIN', 'IOWA', 'NEBRASKA', 'MINNESOTA', 'INDIANA', 'PURDUE', 'ILLINOIS', 'NORTHWESTERN', 'MARYLAND', 'RUTGERS']
                                        # Big 12 teams
                                        big12_teams = ['TEXAS', 'OKLAHOMA', 'KANSAS', 'BAYLOR', 'TCU', 'OKLAHOMA STATE', 'TEXAS TECH', 'IOWA STATE', 'WEST VIRGINIA', 'KANSAS STATE', 'HOUSTON', 'CINCINNATI', 'UCF', 'BYU']
                                        # Ivy League teams
                                        ivy_teams = ['HARVARD', 'YALE', 'PRINCETON', 'COLUMBIA', 'PENN', 'BROWN', 'DARTMOUTH', 'CORNELL']
                                        
                                        if any(acc_team in team_str for acc_team in acc_teams):
                                            conference = 'ACC'
                                        elif any(sec_team in team_str for sec_team in sec_teams):
                                            conference = 'SEC'
                                        elif any(b10_team in team_str for b10_team in big10_teams):
                                            conference = 'Big Ten'
                                        elif any(b12_team in team_str for b12_team in big12_teams):
                                            conference = 'Big 12'
                                        elif any(ivy_team in team_str for ivy_team in ivy_teams):
                                            conference = 'Ivy League'
                                    
                                    player_info_dict[str(player_name)] = {
                                        'team': str(team) if pd.notna(team) else '',
                                        'conference': str(conference) if conference else '',
                                        'position': sheet_name
                                    }
                    
                    # If we found players, break (success)
                    if found_players and player_info_dict:
                        break
                except Exception as inner_e:
                    # Try next header row if this one fails
                    continue
            
            return player_info_dict
    except Exception as e:
        st.error(f"Error loading player info: {e}")
        import traceback
        st.error(traceback.format_exc())
    return {}

# Load existing call log
def load_call_log():
    """Load existing call log."""
    if CALL_LOG_FILE.exists():
        try:
            return pd.read_csv(CALL_LOG_FILE)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# Save call log
def save_call_log(entry):
    """Save call log entry to CSV."""
    # Load existing call log
    existing_df = load_call_log()
    
    # Convert entry to DataFrame if it's a dict
    if isinstance(entry, dict):
        new_df = pd.DataFrame([entry])
    else:
        new_df = entry
    
    # Append to existing data
    if not existing_df.empty:
        df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        df = new_df
    
    # Save to CSV
    df.to_csv(CALL_LOG_FILE, index=False)

# Load agent database
def load_agent_database():
    """Load agent names from CSV file."""
    if AGENT_DB_FILE.exists():
        try:
            df = pd.read_csv(AGENT_DB_FILE)
            if 'Agent Name' in df.columns:
                return sorted(df['Agent Name'].dropna().unique().tolist())
        except:
            return []
    return []

# Save agent to database
def save_agent_to_database(agent_name):
    """Add agent name to database if not already present."""
    if not agent_name or agent_name.strip() == '':
        return
    
    agent_name = agent_name.strip()
    
    # Load existing agents
    existing_agents = load_agent_database()
    
    # Add if new
    if agent_name not in existing_agents:
        existing_agents.append(agent_name)
        # Save to CSV
        df_agents = pd.DataFrame({'Agent Name': sorted(existing_agents)})
        df_agents.to_csv(AGENT_DB_FILE, index=False)

def save_draft():
    """Save current form data as draft to JSON file."""
    try:
        draft_data = {
            'form1_call_date': str(st.session_state.get('form1_call_date', '')),
            'form1_call_type': st.session_state.get('form1_call_type', ''),
            'form1_duration': st.session_state.get('form1_duration', 30),
            'form1_team': st.session_state.get('form1_team', ''),
            'form1_conference': st.session_state.get('form1_conference', ''),
            'form1_conference_other': st.session_state.get('form1_conference_other', ''),
            'form1_position_profile': st.session_state.get('form1_position_profile', ''),
            'form1_participants': st.session_state.get('form1_participants', ''),
            'form1_call_notes': st.session_state.get('form1_call_notes', ''),
            'form1_agent_name': st.session_state.get('form1_agent_name', ''),
            'form1_agent_selected': st.session_state.get('form1_agent_selected', ''),
            'form1_agent_custom': st.session_state.get('form1_agent_custom', ''),
            'form1_relationship': st.session_state.get('form1_relationship', ''),
            'form1_relationship_other': st.session_state.get('form1_relationship_other', ''),
            'form1_agent_professionalism': st.session_state.get('form1_agent_professionalism', 5),
            'form1_agent_responsiveness': st.session_state.get('form1_agent_responsiveness', 5),
            'form1_agent_expectations': st.session_state.get('form1_agent_expectations', 5),
            'form1_agent_transparency': st.session_state.get('form1_agent_transparency', 5),
            'form1_agent_negotiation_style': st.session_state.get('form1_agent_negotiation_style', 5),
            'form1_agent_notes': st.session_state.get('form1_agent_notes', ''),
            'form2_player_notes': st.session_state.get('form2_player_notes', ''),
            'form2_how_they_carry_themselves': st.session_state.get('form2_how_they_carry_themselves', ''),
            'form2_preparation_level': st.session_state.get('form2_preparation_level', 5),
            'form2_preparation_notes': st.session_state.get('form2_preparation_notes', ''),
            'form2_how_they_view_themselves': st.session_state.get('form2_how_they_view_themselves', ''),
            'form2_what_is_important_to_them': st.session_state.get('form2_what_is_important_to_them', ''),
            'form2_mindset_towards_growth': st.session_state.get('form2_mindset_towards_growth', ''),
            'form2_has_big_injuries': st.session_state.get('form2_has_big_injuries', 'No'),
            'form2_injury_periods': st.session_state.get('form2_injury_periods', ''),
            'form2_personality_traits': st.session_state.get('form2_personality_traits', []),
            'form2_other_traits': st.session_state.get('form2_other_traits', ''),
            'form2_interest_level': st.session_state.get('form2_interest_level', ''),
            'form2_timeline': st.session_state.get('form2_timeline', ''),
            'form2_timeline_selected': st.session_state.get('form2_timeline_selected', ''),
            'form2_timeline_custom': st.session_state.get('form2_timeline_custom', ''),
            'form2_salary_expectations': st.session_state.get('form2_salary_expectations', ''),
            'form2_other_opportunities': st.session_state.get('form2_other_opportunities', ''),
            'form2_key_talking_points': st.session_state.get('form2_key_talking_points', ''),
            'form2_red_flags': st.session_state.get('form2_red_flags', ''),
            'form2_red_flag_severity': st.session_state.get('form2_red_flag_severity', 'None'),
            'form2_recommendation': st.session_state.get('form2_recommendation', ''),
            'form2_summary_notes': st.session_state.get('form2_summary_notes', ''),
            'communication': st.session_state.get('communication', 5),
            'maturity': st.session_state.get('maturity', 5),
            'coachability': st.session_state.get('coachability', 5),
            'leadership': st.session_state.get('leadership', 5),
            'work_ethic': st.session_state.get('work_ethic', 5),
            'confidence': st.session_state.get('confidence', 5),
            'tactical_knowledge': st.session_state.get('tactical_knowledge', 5),
            'team_fit': st.session_state.get('team_fit', 5),
            'overall_rating': st.session_state.get('overall_rating', 5),
            'follow_up_needed': st.session_state.get('follow_up_needed', False),
            'follow_up_date': str(st.session_state.get('follow_up_date', '')) if st.session_state.get('follow_up_date') else '',
            'action_items': st.session_state.get('action_items', ''),
            'use_custom_player': st.session_state.get('use_custom_player', False),
            'custom_player_name': st.session_state.get('custom_player_name', ''),
            'player_select': st.session_state.get('player_select', ''),
            'filter_conference': st.session_state.get('filter_conference', ''),
            'filter_team': st.session_state.get('filter_team', ''),
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(DRAFT_FILE, 'w') as f:
            json.dump(draft_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving draft: {e}")
        return False

def load_draft():
    """Load draft data from JSON file."""
    try:
        if DRAFT_FILE.exists():
            with open(DRAFT_FILE, 'r') as f:
                draft_data = json.load(f)
            return draft_data
        return None
    except Exception as e:
        return None

def clear_draft():
    """Delete draft file."""
    try:
        if DRAFT_FILE.exists():
            DRAFT_FILE.unlink()
    except Exception as e:
        pass

def escape_text(text):
    """Escape special characters for ReportLab Paragraph."""
    if text is None:
        return "N/A"
    text = str(text)
    # Replace common special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def truncate_text(text, max_len):
    """Truncate text to max length."""
    text = str(text) if text is not None else "N/A"
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text

def generate_call_log_pdf(entry):
    """Generate PDF from call log entry using ReportLab."""
    if not PDF_AVAILABLE:
        return None
    
    try:
        # Create PDF in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                              rightMargin=0.4*inch, leftMargin=0.4*inch,
                              topMargin=0.4*inch, bottomMargin=0.4*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.HexColor('#1f77b4'),
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            spaceBefore=8,
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=8,
            spaceAfter=4,
        )
        small_style = ParagraphStyle(
            'CustomSmall',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#666666'),
        )
        
        # Title
        player_name = escape_text(entry.get('Player Name', 'Unknown Player'))
        title = Paragraph(f"Call Log Report - {player_name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.1*inch))
        
        # Call Information
        elements.append(Paragraph("Call Information", heading_style))
        call_data = [
            ['Call Date:', escape_text(entry.get('Call Date', 'N/A')), 
             'Call Type:', escape_text(entry.get('Call Type', 'N/A'))],
            ['Duration:', f"{entry.get('Duration (min)', 0)} min", 
             'Team:', escape_text(entry.get('Team', 'N/A'))],
            ['Conference:', escape_text(entry.get('Conference', 'N/A')), 
             'Position:', escape_text(entry.get('Position Profile', 'N/A'))],
            ['Participants:', escape_text(entry.get('Participants', 'N/A'))],
        ]
        call_table = Table(call_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        call_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(call_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Agent Assessment
        elements.append(Paragraph("Agent Assessment", heading_style))
        agent_name = escape_text(entry.get('Agent Name', 'N/A'))
        relationship = escape_text(entry.get('Relationship', 'N/A'))
        agent_data = [
            ['Agent:', f"{agent_name} ({relationship})"],
            ['Scores:', f"Prof: {entry.get('Agent Professionalism', 'N/A')}/10 | "
                       f"Resp: {entry.get('Agent Responsiveness', 'N/A')}/10 | "
                       f"Exp: {entry.get('Agent Expectations', 'N/A')}/10 | "
                       f"Trans: {entry.get('Agent Transparency', 'N/A')}/10 | "
                       f"Neg: {entry.get('Agent Negotiation Style', 'N/A')}/10"],
            ['Notes:', truncate_text(entry.get('Agent Notes', 'N/A'), 100)],
        ]
        agent_table = Table(agent_data, colWidths=[1.2*inch, 5.8*inch])
        agent_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(agent_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Player Notes
        elements.append(Paragraph("Player Notes", heading_style))
        player_notes = truncate_text(entry.get('Player Notes', 'N/A'), 150)
        notes_para = Paragraph(f"<b>{player_notes}</b>", normal_style)
        elements.append(notes_para)
        elements.append(Spacer(1, 0.15*inch))
        
        # Player Assessment
        elements.append(Paragraph("Player Assessment", heading_style))
        assessment_data = [
            ['Comm:', f"{entry.get('Communication', 'N/A')}/10",
             'Maturity:', f"{entry.get('Maturity', 'N/A')}/10",
             'Coach:', f"{entry.get('Coachability', 'N/A')}/10"],
            ['Leader:', f"{entry.get('Leadership', 'N/A')}/10",
             'Work Ethic:', f"{entry.get('Work Ethic', 'N/A')}/10",
             'Conf:', f"{entry.get('Confidence', 'N/A')}/10"],
            ['Tactical:', f"{entry.get('Tactical Knowledge', 'N/A')}/10",
             'Team Fit:', f"{entry.get('Team Fit', 'N/A')}/10",
             'Overall:', f"{entry.get('Overall Rating', 'N/A')}/10"],
        ]
        assessment_table = Table(assessment_data, colWidths=[1*inch, 0.8*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch])
        assessment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (4, 0), (4, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(assessment_table)
        total_score = entry.get('Assessment Total Score', 'N/A')
        total_pct = entry.get('Assessment Percentage', 'N/A')
        grade = entry.get('Assessment Grade', 'N/A')
        total_text = f"<b>Total:</b> {total_score}/90 ({total_pct}%) | <b>Grade:</b> {grade}"
        elements.append(Paragraph(total_text, normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Personality & Self Awareness
        elements.append(Paragraph("Personality & Self Awareness", heading_style))
        personality_items = [
            ('Carry themselves:', entry.get('How They Carry Themselves', 'N/A'), 80),
            ('View themselves:', entry.get('How They View Themselves', 'N/A'), 80),
            ('Important:', entry.get('What Is Important To Them', 'N/A'), 80),
            ('Growth mindset:', entry.get('Mindset Towards Growth', 'N/A'), 80),
        ]
        for label, value, max_len in personality_items:
            text = truncate_text(value, max_len)
            para = Paragraph(f"<b>{label}</b> {escape_text(text)}", normal_style)
            elements.append(para)
        # Preparation (special format)
        prep_level = entry.get('Preparation Level', 'N/A')
        prep_notes = truncate_text(entry.get('Preparation Notes', 'N/A'), 60)
        prep_text = f"{prep_level}/10 - {prep_notes}"
        elements.append(Paragraph(f"<b>Preparation:</b> {escape_text(prep_text)}", normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Key Talking Points
        elements.append(Paragraph("Key Talking Points", heading_style))
        talking_data = [
            ['Interest:', escape_text(entry.get('Interest Level', 'N/A')), 
             'Timeline:', escape_text(entry.get('Timeline', 'N/A'))],
            ['Salary:', escape_text(entry.get('Salary Expectations', 'N/A'))],
            ['Other Opps:', truncate_text(entry.get('Other Opportunities', 'N/A'), 100)],
            ['Talking Points:', truncate_text(entry.get('Key Talking Points', 'N/A'), 100)],
        ]
        talking_table = Table(talking_data, colWidths=[1*inch, 5*inch])
        talking_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('SPAN', (1, 1), (1, 1)),
            ('SPAN', (1, 2), (1, 2)),
            ('SPAN', (1, 3), (1, 3)),
        ]))
        elements.append(talking_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Red Flags & Assessment
        elements.append(Paragraph("Red Flags & Assessment", heading_style))
        red_flag_severity = escape_text(entry.get('Red Flag Severity', 'N/A'))
        red_flags = truncate_text(entry.get('Red Flags', 'N/A'), 100)
        recommendation = escape_text(entry.get('Recommendation', 'N/A'))
        summary = truncate_text(entry.get('Summary Notes', 'N/A'), 120)
        elements.append(Paragraph(f"<b>Red Flags:</b> {red_flag_severity} - {red_flags}", normal_style))
        elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", normal_style))
        elements.append(Paragraph(f"<b>Summary:</b> {summary}", normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Next Steps
        elements.append(Paragraph("Next Steps", heading_style))
        follow_up = 'Yes' if entry.get('Follow-up Needed') else 'No'
        follow_up_date = entry.get('Follow-up Date', '')
        if follow_up == 'Yes' and follow_up_date:
            follow_up += f" - {follow_up_date}"
        action_items = truncate_text(entry.get('Action Items', 'N/A'), 100)
        elements.append(Paragraph(f"<b>Follow-up:</b> {follow_up}", normal_style))
        elements.append(Paragraph(f"<b>Action Items:</b> {action_items}", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Footer
        call_notes = truncate_text(entry.get('Call Notes', 'N/A'), 80)
        created_at = escape_text(entry.get('Created At', 'N/A'))
        footer_text = f"Call Notes: {call_notes} | Created: {created_at}"
        elements.append(Paragraph(footer_text, small_style))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

# Initialize session state
if 'call_log' not in st.session_state:
    st.session_state.call_log = load_call_log()
if 'selected_player_team' not in st.session_state:
    st.session_state.selected_player_team = ''
if 'selected_player_conference' not in st.session_state:
    st.session_state.selected_player_conference = ''
if 'selected_player_position' not in st.session_state:
    st.session_state.selected_player_position = ''
if 'filter_conference' not in st.session_state:
    st.session_state.filter_conference = ''
if 'filter_team' not in st.session_state:
    st.session_state.filter_team = ''

# Load players and player info
players_list = load_player_database()
player_info_dict = load_player_info()

# Load agent database
agents_list = load_agent_database()

def get_conferences_from_database():
    """Get list of all conferences from player database."""
    conferences = set()
    for player_name, info in player_info_dict.items():
        conf = info.get('conference', '')
        if conf:
            conferences.add(conf)
    return sorted(list(conferences))

def get_teams_by_conference(conference):
    """Get list of teams for a given conference."""
    if not conference:
        return []
    teams = set()
    for player_name, info in player_info_dict.items():
        if info.get('conference', '') == conference:
            team = info.get('team', '')
            if team:
                teams.add(team)
    return sorted(list(teams))

def get_players_by_team(team):
    """Get list of players for a given team."""
    if not team:
        return []
    players = []
    for player_name, info in player_info_dict.items():
        if info.get('team', '') == team:
            players.append(player_name)
    return sorted(players)

# Display loading status in sidebar
if PLAYER_DB_FILE and PLAYER_DB_FILE.exists():
    st.sidebar.success(f"✅ Loaded {len(players_list)} players from:\n`{PLAYER_DB_FILE.name}`")
else:
    st.sidebar.error("⚠️ No player database file found!\n\nPlease ensure one of these files exists:\n- Portland Thorns 2025 Long Shortlist.xlsx\n- Portland Thorns 2025 Short Shortlist.xlsx\n- AI Shortlist.xlsx\n- Conference Reports")

# Main app
st.title("⚽ Portland Thorns - Call Log System")
st.markdown("---")

# Sidebar navigation
# Player Overview PDF Viewer
OVERVIEW_DIR = BASE_DIR / 'Player Overviews'

page = st.sidebar.selectbox(
    "Navigation", 
    [
        "Log New Call", 
        "View Call History", 
        "Player Summary", 
        "Player Database", 
        "Scouting Requests", 
        "Video Review Tracker",
        "View Player Overview",
        "Update Player Overviews",
        "Export to SAP",
        "Export Data"
    ]
)

if page == "Log New Call":
    # Remove hash from URL and scroll to top on page load/refresh
    st.markdown(
        """
        <script>
        (function() {
            // Remove hash from URL if present
            if (window.location.hash) {
                window.history.replaceState(null, null, window.location.pathname + window.location.search);
            }
            // Scroll to top immediately
            window.scrollTo(0, 0);
            // Also handle on load
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    if (window.location.hash) {
                        window.history.replaceState(null, null, window.location.pathname + window.location.search);
                    }
                    window.scrollTo(0, 0);
                });
            }
            // Listen for hash changes and remove them
            window.addEventListener('hashchange', function() {
                if (window.location.hash) {
                    window.history.replaceState(null, null, window.location.pathname + window.location.search);
                    window.scrollTo(0, 0);
                }
            });
        })();
        </script>
        """,
        unsafe_allow_html=True
    )
    
    st.header("📞 Log New Call")
    
    # Player selection OUTSIDE form so it updates reactively
    use_custom_player = st.checkbox("Player not in database", key="use_custom_player")
    
    if use_custom_player:
        # Custom player entry
        player_name = st.text_input("Player Name", key="custom_player_name", placeholder="Enter player name")
        # Clear auto-populated fields and filters for custom players
        st.session_state.selected_player_team = ''
        st.session_state.selected_player_conference = ''
        st.session_state.selected_player_position = ''
        st.session_state.filter_conference = ''
        st.session_state.filter_team = ''
        
        # Show info boxes for custom players
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.info("**Team**: -")
        with col_info2:
            st.info("**Conference**: -")
        with col_info3:
            st.info("**Position**: -")
    else:
        # Conference and Team filtering
        conferences_list = get_conferences_from_database()
        
        col_conf, col_team = st.columns(2)
        
        with col_conf:
            # Conference dropdown
            conference_filter = st.selectbox(
                "Conference",
                [""] + conferences_list,
                key="filter_conference_select",
                index=0 if not st.session_state.get('filter_conference') else (conferences_list.index(st.session_state.filter_conference) + 1 if st.session_state.filter_conference in conferences_list else 0)
            )
            st.session_state.filter_conference = conference_filter
        
        with col_team:
            # Team dropdown (filtered by conference)
            if conference_filter:
                teams_list = get_teams_by_conference(conference_filter)
                # Reset team filter if conference changed and current team not in new list
                current_team = st.session_state.get('filter_team', '')
                if current_team and current_team not in teams_list:
                    st.session_state.filter_team = ''
                    current_team = ''
                
                team_filter = st.selectbox(
                    "Team",
                    [""] + teams_list,
                    key="filter_team_select",
                    index=0 if not current_team else (teams_list.index(current_team) + 1 if current_team in teams_list else 0)
                )
                st.session_state.filter_team = team_filter
            else:
                st.selectbox("Team", [""], key="filter_team_select_disabled", disabled=True)
                st.session_state.filter_team = ''
        
        # Player selection (filtered by team if selected, otherwise by conference, otherwise all)
        if st.session_state.filter_team:
            # Filter by team
            available_players = get_players_by_team(st.session_state.filter_team)
        elif st.session_state.filter_conference:
            # Filter by conference
            available_players = []
            for player_name_check, info in player_info_dict.items():
                if info.get('conference', '') == st.session_state.filter_conference:
                    available_players.append(player_name_check)
            available_players = sorted(available_players)
        else:
            # Show all players
            available_players = players_list
        
        # Search functionality
        col_search, col_select = st.columns([2, 3])
        with col_search:
            player_search = st.text_input("🔍 Search Player", key="player_search")
        with col_select:
            if player_search:
                filtered_players = [p for p in available_players if player_search.lower() in p.lower()]
            else:
                filtered_players = available_players
            
            player_name = st.selectbox("Player Name", [""] + filtered_players[:200], key="player_select")  # Increased limit since we're filtering
    
    # Auto-populate team, conference, and position when player is selected (reactive)
    if player_name and player_name in player_info_dict:
        player_info = player_info_dict[player_name]
        auto_team = player_info.get('team', '')
        auto_conference = player_info.get('conference', '')
        auto_position = player_info.get('position', '')
        
        # Update session state
        st.session_state.selected_player_team = auto_team
        st.session_state.selected_player_conference = auto_conference
        st.session_state.selected_player_position = auto_position
        
        # Show auto-populated info
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.info(f"**Team**: {auto_team}")
        with col_info2:
            st.info(f"**Conference**: {auto_conference}")
        with col_info3:
            st.info(f"**Position**: {auto_position}")
    elif not player_name:
        st.session_state.selected_player_team = ''
        st.session_state.selected_player_conference = ''
        st.session_state.selected_player_position = ''
        # Show info boxes even when no player selected
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.info("**Team**: -")
        with col_info2:
            st.info("**Conference**: -")
        with col_info3:
            st.info("**Position**: -")
    
    st.markdown("---")
    
    # Call details and Agent Assessment - no form wrapper for reactive updates
    col1, col2 = st.columns(2)
    
    with col1:
        call_date = st.date_input("Call Date", value=st.session_state.get('form1_call_date', datetime.now().date()))
        call_type = st.selectbox("Call Type", ["Player Call", "Agent Call", "Both"], index=["Player Call", "Agent Call", "Both"].index(st.session_state.get('form1_call_type', "Player Call")) if st.session_state.get('form1_call_type', "Player Call") in ["Player Call", "Agent Call", "Both"] else 0)
        duration = st.number_input("Duration (minutes)", min_value=0, max_value=300, value=st.session_state.get('form1_duration', 30))
        
        # Use auto-populated values from player selection (no redundant fields)
        team = st.session_state.get('form1_team', st.session_state.selected_player_team)
        conference = st.session_state.get('form1_conference', st.session_state.selected_player_conference)
        conference_other = st.session_state.get('form1_conference_other', '')
        # Position Profile removed - using auto-populated position from player selection
        position_profile = st.session_state.selected_player_position
    
    with col2:
        participants = st.text_area("Participants", value=st.session_state.get('form1_participants', ''), placeholder="List all participants in the call")
        call_notes = st.text_area("Call Notes", value=st.session_state.get('form1_call_notes', ''), placeholder="General notes about the call")
    
    st.markdown("### Agent Assessment")
    # Agent name with dropdown + custom entry
    agent_options = [""] + agents_list
    agent_selected = st.selectbox("Agent Name", agent_options, key="agent_select", index=agent_options.index(st.session_state.get('form1_agent_selected', '')) if st.session_state.get('form1_agent_selected', '') in agent_options else 0)
    agent_custom = st.text_input("Or enter new agent name", value=st.session_state.get('form1_agent_custom', ''), placeholder="Leave empty if using dropdown above", key="agent_custom")
    
    # Use custom if provided, otherwise use selected
    agent_name = agent_custom.strip() if agent_custom.strip() else agent_selected
    relationship = st.selectbox(
        "Relationship",
        ["Professional Agent", "Family Member", "Parent", "Guardian", "Other"],
        index=["Professional Agent", "Family Member", "Parent", "Guardian", "Other"].index(st.session_state.get('form1_relationship', "Professional Agent")) if st.session_state.get('form1_relationship', "Professional Agent") in ["Professional Agent", "Family Member", "Parent", "Guardian", "Other"] else 0,
        help="Select the relationship of the person representing the player"
    )
    relationship_other = st.text_input("Relationship (Other)", value=st.session_state.get('form1_relationship_other', ''), placeholder="Specify if 'Other' selected", disabled=(relationship != "Other"))
    
    col6, col7, col8, col9, col10 = st.columns(5)
    with col6:
        agent_professionalism = st.slider("Agent Professionalism (1-10)", 1, 10, st.session_state.get('form1_agent_professionalism', 5))
    with col7:
        agent_responsiveness = st.slider("Agent Responsiveness (1-10)", 1, 10, st.session_state.get('form1_agent_responsiveness', 5))
    with col8:
        agent_expectations = st.slider("Reasonable Expectations (1-10)", 1, 10, st.session_state.get('form1_agent_expectations', 5))
    with col9:
        agent_transparency = st.slider("Transparency/Honesty (1-10)", 1, 10, st.session_state.get('form1_agent_transparency', 5))
    with col10:
        agent_negotiation_style = st.slider("Negotiation Style (1-10)", 1, 10, st.session_state.get('form1_agent_negotiation_style', 5), help="1 = Aggressive, 10 = Collaborative")
    
    agent_notes = st.text_area("Agent Notes", value=st.session_state.get('form1_agent_notes', ''))
    
    # Store values in session state for form submission
    st.session_state.form1_call_date = call_date
    st.session_state.form1_call_type = call_type
    st.session_state.form1_duration = duration
    st.session_state.form1_team = team
    st.session_state.form1_conference = conference
    st.session_state.form1_conference_other = conference_other
    st.session_state.form1_position_profile = position_profile
    st.session_state.form1_participants = participants
    st.session_state.form1_call_notes = call_notes
    st.session_state.form1_agent_name = agent_name
    st.session_state.form1_agent_selected = agent_selected
    st.session_state.form1_agent_custom = agent_custom
    st.session_state.form1_relationship = relationship
    st.session_state.form1_relationship_other = relationship_other
    st.session_state.form1_agent_professionalism = agent_professionalism
    st.session_state.form1_agent_responsiveness = agent_responsiveness
    st.session_state.form1_agent_expectations = agent_expectations
    st.session_state.form1_agent_transparency = agent_transparency
    st.session_state.form1_agent_negotiation_style = agent_negotiation_style
    st.session_state.form1_agent_notes = agent_notes
    
    # Continue with remaining fields (no form wrapper for reactive updates)
    st.markdown("### Player Notes")
    player_notes = st.text_area("Player Notes", value=st.session_state.get('form2_player_notes', ''), placeholder="General notes about the player")
    st.session_state.form2_player_notes = player_notes
    
    st.markdown("### Personality")
    how_they_carry_themselves = st.text_area(
        "How do they carry themselves?",
        placeholder="Describe their demeanor, presence, communication style"
    )
    preparation_level = st.slider("How prepared are they? (1-10)", 1, 10, 5, help="Knowledge of Portland Thorns and readiness to ask questions")
    preparation_notes = st.text_area(
        "Preparation Notes",
        placeholder="What did they know about Portland? What questions did they ask?"
    )
    
    st.markdown("### Self Awareness / Player Identity")
    how_they_view_themselves = st.text_area(
        "How do they view themselves?",
        placeholder="Their self-perception, strengths they emphasize, role they see themselves in"
    )
    what_is_important_to_them = st.text_area(
        "What is important to them?",
        placeholder="Values, priorities, what matters most to them"
    )
    mindset_towards_growth = st.text_area(
        "What is their mindset towards growth?",
        placeholder="Openness to feedback, learning attitude, development focus"
    )
    
    st.markdown("### Injuries")
    has_big_injuries = st.selectbox(
        "Have they had any big injuries?",
        ["No", "Yes", "Unknown"]
    )
    injury_periods = st.text_area(
        "What were those periods like?",
        placeholder="Describe the injury periods, recovery process, mental/emotional impact",
        disabled=(has_big_injuries != "Yes")
    )
    
    st.markdown("### Additional Personality Traits")
    personality_traits = st.multiselect(
        "Select applicable traits",
        ["Competitive", "Resilient", "Humble", "Driven", "Team-first", "Self-aware", "Confident", "Focused", "Adaptable", "Other"]
    )
    other_traits = st.text_input("Other traits (comma-separated)")
    
    st.markdown("### Key Talking Points")
    interest_level = st.selectbox("Interest Level in Portland", ["Very High", "High", "Medium", "Low", "Very Low", "Unknown"])
    
    # Timeline dropdown with custom option
    timeline_options = ["Immediately", "3 months", "6 months", "1 year", "Other"]
    timeline_selected = st.selectbox("Timeline", timeline_options, index=timeline_options.index(st.session_state.get('form2_timeline_selected', 'Immediately')) if st.session_state.get('form2_timeline_selected', 'Immediately') in timeline_options else 0)
    st.session_state.form2_timeline_selected = timeline_selected
    
    if timeline_selected == "Other":
        timeline_custom = st.text_input("Timeline (Custom)", value=st.session_state.get('form2_timeline_custom', ''), placeholder="Enter custom timeline")
        st.session_state.form2_timeline_custom = timeline_custom
        timeline = timeline_custom
    else:
        timeline = timeline_selected
        st.session_state.form2_timeline_custom = ''
    
    salary_expectations = st.text_input("Salary Expectations", placeholder="If discussed")
    other_opportunities = st.text_area("Other Opportunities", placeholder="Other teams/opportunities mentioned")
    key_talking_points = st.text_area("Key Talking Points", placeholder="Main discussion points")
    
    st.markdown("### Red Flags & Concerns")
    red_flag_severity = st.selectbox("Severity", ["None", "Low", "Medium", "High"])
    red_flags = st.text_area("Red Flags / Concerns", placeholder="Any concerns or red flags")
    
    # Store form2 values in session state (this happens on every rerun)
    st.session_state.form2_how_they_carry_themselves = how_they_carry_themselves
    st.session_state.form2_preparation_level = preparation_level
    st.session_state.form2_preparation_notes = preparation_notes
    st.session_state.form2_how_they_view_themselves = how_they_view_themselves
    st.session_state.form2_what_is_important_to_them = what_is_important_to_them
    st.session_state.form2_mindset_towards_growth = mindset_towards_growth
    st.session_state.form2_has_big_injuries = has_big_injuries
    st.session_state.form2_injury_periods = injury_periods
    st.session_state.form2_personality_traits = personality_traits
    st.session_state.form2_other_traits = other_traits
    st.session_state.form2_interest_level = interest_level
    # Store timeline value (either selected option or custom)
    st.session_state.form2_timeline = timeline
    st.session_state.form2_salary_expectations = salary_expectations
    st.session_state.form2_other_opportunities = other_opportunities
    st.session_state.form2_key_talking_points = key_talking_points
    st.session_state.form2_red_flags = red_flags
    st.session_state.form2_red_flag_severity = red_flag_severity
    
    # Player Assessment section OUTSIDE form for reactive score updates
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        communication = st.slider("Communication Skills (1-10)", 1, 10, st.session_state.get('communication', 5), key="comm_slider")
        maturity = st.slider("Maturity (1-10)", 1, 10, st.session_state.get('maturity', 5), key="maturity_slider")
        coachability = st.slider("Coachability (1-10)", 1, 10, st.session_state.get('coachability', 5), key="coachability_slider")
    
    with col4:
        leadership = st.slider("Leadership Potential (1-10)", 1, 10, st.session_state.get('leadership', 5), key="leadership_slider")
        work_ethic = st.slider("Work Ethic (1-10)", 1, 10, st.session_state.get('work_ethic', 5), key="workethic_slider")
        confidence = st.slider("Confidence Level (1-10)", 1, 10, st.session_state.get('confidence', 5), key="confidence_slider")
    
    with col5:
        tactical_knowledge = st.slider("Tactical Knowledge (1-10)", 1, 10, st.session_state.get('tactical_knowledge', 5), key="tactical_slider")
        team_fit = st.slider("Team Fit (Cultural) (1-10)", 1, 10, st.session_state.get('team_fit', 5), key="teamfit_slider")
        overall_rating = st.slider("Overall Rating (1-10)", 1, 10, st.session_state.get('overall_rating', 5), key="overall_slider")
    
    # Store slider values in session state for form submission
    st.session_state.communication = communication
    st.session_state.maturity = maturity
    st.session_state.coachability = coachability
    st.session_state.leadership = leadership
    st.session_state.work_ethic = work_ethic
    st.session_state.confidence = confidence
    st.session_state.tactical_knowledge = tactical_knowledge
    st.session_state.team_fit = team_fit
    st.session_state.overall_rating = overall_rating
    
    # Calculate total assessment score (reactive - updates immediately as sliders change)
    assessment_total = (
        communication + maturity + coachability + 
        leadership + work_ethic + confidence + 
        tactical_knowledge + team_fit + overall_rating
    )
    max_possible = 9 * 10  # 9 metrics * 10 max score
    assessment_percentage = (assessment_total / max_possible) * 100
    
    # Calculate grade based on assessment percentage (same scale as player metrics)
    # A = 90th percentile or higher, B = 80-89, C = 70-79, D = 60-69, F = below 60
    def assign_grade_from_percentile(pct):
        if pct >= 90:
            return 'A'
        elif pct >= 80:
            return 'B'
        elif pct >= 70:
            return 'C'
        elif pct >= 60:
            return 'D'
        else:
            return 'F'
    
    assessment_grade = assign_grade_from_percentile(assessment_percentage)
    
    # Store assessment totals in session state for form submission
    st.session_state.assessment_total = assessment_total
    st.session_state.assessment_percentage = assessment_percentage
    st.session_state.assessment_grade = assessment_grade
    
    st.markdown("### Assessment Summary")
    col_score1, col_score2, col_score3 = st.columns(3)
    with col_score1:
        st.metric("Total Assessment Score", f"{assessment_total}/{max_possible}")
    with col_score2:
        st.metric("Assessment Percentage", f"{assessment_percentage:.1f}%")
    with col_score3:
        st.metric("Grade", assessment_grade)
    
    st.markdown("### Overall Assessment")
    recommendation = st.selectbox("Recommendation", ["Strong Yes", "Yes", "Maybe", "No", "Strong No"])
    summary_notes = st.text_area("Summary Notes", placeholder="Overall impression and summary")
    
    # Store Overall Assessment values in session state
    st.session_state.form2_recommendation = recommendation
    st.session_state.form2_summary_notes = summary_notes
    
    # Next Steps section - outside form for reactive updates
    st.markdown("### Next Steps")
    follow_up_needed = st.checkbox("Follow-up Needed", value=st.session_state.get('follow_up_needed', False))
    st.session_state.follow_up_needed = follow_up_needed
    
    # Always show date input, but disable it when checkbox is unchecked
    follow_up_date = st.date_input(
        "Follow-up Date", 
        value=st.session_state.get('follow_up_date', datetime.now().date()) if st.session_state.get('follow_up_date') else datetime.now().date(),
        disabled=not follow_up_needed
    )
    if follow_up_needed:
        st.session_state.follow_up_date = follow_up_date
    else:
        st.session_state.follow_up_date = None
    
    action_items = st.text_area("Action Items", value=st.session_state.get('action_items', ''), placeholder="What needs to happen next?")
    st.session_state.action_items = action_items
    
    # Sticky Save Draft button in sidebar (always visible as user scrolls)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💾 Save Progress")
        if st.button("💾 Save Draft", key="save_draft_btn", use_container_width=True, help="Save your progress without submitting. Data will be restored when you return."):
            if save_draft():
                st.success("✅ Draft saved!")
        
        # Show draft status
        draft_exists = DRAFT_FILE.exists()
        if draft_exists:
            draft_data = load_draft()
            if draft_data and 'saved_at' in draft_data:
                st.caption(f"📋 Draft saved: {draft_data['saved_at']}")
            if st.button("🗑️ Clear Draft", key="clear_draft_btn", use_container_width=True):
                clear_draft()
                st.rerun()
    
    # Final form for submission only
    with st.form("call_log_form_final"):
        submitted = st.form_submit_button("💾 Save Call Log", use_container_width=True)
        
        if submitted:
            # Get form values from first form (stored in session state or accessed via form context)
            # Note: We need to access the first form's values
            if not player_name or (isinstance(player_name, str) and player_name.strip() == ''):
                st.error("Please enter or select a player name")
            else:
                # Access first form values from session state
                # Save new agent to database if provided
                agent_name_val = st.session_state.get('form1_agent_name', '')
                if agent_name_val and agent_name_val.strip():
                    save_agent_to_database(agent_name_val)
                # Create new entry - need to get values from first form
                # Since forms are separate, we'll need to store first form data in session state
                final_conference = st.session_state.get('form1_conference_other') if st.session_state.get('form1_conference') == "Other" else st.session_state.get('form1_conference', '')
                final_relationship = st.session_state.get('form1_relationship_other') if st.session_state.get('form1_relationship') == "Other" else st.session_state.get('form1_relationship', '')
                
                new_entry = {
                    'Call Date': (st.session_state.get('form1_call_date') or datetime.now().date()).strftime('%Y-%m-%d') if isinstance(st.session_state.get('form1_call_date', None), date) else datetime.now().date().strftime('%Y-%m-%d'),
                    'Player Name': player_name,
                    'Team': st.session_state.get('form1_team', ''),
                    'Conference': final_conference,
                    'Position Profile': st.session_state.get('form1_position_profile', ''),
                    'Call Type': st.session_state.get('form1_call_type', ''),
                    'Duration (min)': st.session_state.get('form1_duration', 0),
                    'Participants': st.session_state.get('form1_participants', ''),
                    'Call Notes': st.session_state.get('form1_call_notes', ''),
                    'Communication': st.session_state.get('communication', 5),
                    'Maturity': st.session_state.get('maturity', 5),
                    'Coachability': st.session_state.get('coachability', 5),
                    'Leadership': st.session_state.get('leadership', 5),
                    'Work Ethic': st.session_state.get('work_ethic', 5),
                    'Confidence': st.session_state.get('confidence', 5),
                    'Tactical Knowledge': st.session_state.get('tactical_knowledge', 5),
                    'Team Fit': st.session_state.get('team_fit', 5),
                    'Assessment Total Score': st.session_state.get('assessment_total', 45),
                    'Assessment Percentage': round(st.session_state.get('assessment_percentage', 50.0), 1),
                    'Assessment Grade': st.session_state.get('assessment_grade', 'F'),
                    'How They Carry Themselves': st.session_state.get('form2_how_they_carry_themselves', ''),
                    'Preparation Level': st.session_state.get('form2_preparation_level', 5),
                    'Preparation Notes': st.session_state.get('form2_preparation_notes', ''),
                    'How They View Themselves': st.session_state.get('form2_how_they_view_themselves', ''),
                    'What Is Important To Them': st.session_state.get('form2_what_is_important_to_them', ''),
                    'Mindset Towards Growth': st.session_state.get('form2_mindset_towards_growth', ''),
                    'Has Big Injuries': st.session_state.get('form2_has_big_injuries', 'No'),
                    'Injury Periods': st.session_state.get('form2_injury_periods', '') if st.session_state.get('form2_has_big_injuries') == "Yes" else '',
                    'Personality Traits': ', '.join(st.session_state.get('form2_personality_traits', [])),
                    'Other Traits': st.session_state.get('form2_other_traits', ''),
                    'Agent Name': st.session_state.get('form1_agent_name', ''),
                    'Relationship': final_relationship,
                    'Agent Professionalism': st.session_state.get('form1_agent_professionalism', 5),
                    'Agent Responsiveness': st.session_state.get('form1_agent_responsiveness', 5),
                    'Agent Expectations': st.session_state.get('form1_agent_expectations', 5),
                    'Agent Transparency': st.session_state.get('form1_agent_transparency', 5),
                    'Agent Negotiation Style': st.session_state.get('form1_agent_negotiation_style', 5),
                    'Agent Notes': st.session_state.get('form1_agent_notes', ''),
                    'Player Notes': st.session_state.get('form2_player_notes', ''),
                    'Interest Level': st.session_state.get('form2_interest_level', ''),
                    'Timeline': st.session_state.get('form2_timeline', ''),
                    'Salary Expectations': st.session_state.get('form2_salary_expectations', ''),
                    'Other Opportunities': st.session_state.get('form2_other_opportunities', ''),
                    'Key Talking Points': st.session_state.get('form2_key_talking_points', ''),
                    'Red Flags': st.session_state.get('form2_red_flags', ''),
                    'Red Flag Severity': st.session_state.get('form2_red_flag_severity', ''),
                    'Overall Rating': st.session_state.get('overall_rating', 5),
                    'Recommendation': st.session_state.get('form2_recommendation', ''),
                    'Summary Notes': st.session_state.get('form2_summary_notes', ''),
                    'Follow-up Needed': st.session_state.get('follow_up_needed', False),
                    'Follow-up Date': st.session_state.get('follow_up_date').strftime('%Y-%m-%d') if st.session_state.get('follow_up_date') else '',
                    'Action Items': st.session_state.get('action_items', ''),
                    'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save to CSV
                save_call_log(new_entry)
                # Clear draft after successful submission
                clear_draft()
                st.success("✅ Call log saved successfully!")
                
                # Store PDF data in session state for download outside form
                pdf_bytes = generate_call_log_pdf(new_entry)
                if pdf_bytes:
                    player_name_safe = new_entry['Player Name'].replace('/', '_').replace('\\', '_')
                    pdf_filename = f"Call_Log_{player_name_safe}_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.session_state['pdf_download_data'] = pdf_bytes
                    st.session_state['pdf_download_filename'] = pdf_filename
                    st.session_state['show_pdf_download'] = True
                else:
                    st.session_state['show_pdf_download'] = False
                    if not PDF_AVAILABLE:
                        st.info("💡 Install reportlab to enable PDF downloads: `pip install reportlab`")
    
    # PDF download button (outside form)
    if st.session_state.get('show_pdf_download', False):
        pdf_bytes = st.session_state.get('pdf_download_data')
        pdf_filename = st.session_state.get('pdf_download_filename', 'call_log.pdf')
        if pdf_bytes:
            st.download_button(
                "📄 Download PDF",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download_btn"
            )
            # Clear the download state after showing
            st.session_state['show_pdf_download'] = False

elif page == "View Call History":
    st.header("📋 Call History")
    
    if st.session_state.call_log.empty:
        st.info("No call logs yet. Log your first call!")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_player = st.selectbox("Filter by Player", [""] + sorted(st.session_state.call_log['Player Name'].unique().tolist()))
        with col2:
            filter_recommendation = st.selectbox("Filter by Recommendation", [""] + sorted(st.session_state.call_log['Recommendation'].unique().tolist()))
        with col3:
            filter_date_range = st.date_input("Filter by Date Range", value=None)
        
        # Apply filters
        filtered_log = st.session_state.call_log.copy()
        if filter_player:
            filtered_log = filtered_log[filtered_log['Player Name'] == filter_player]
        if filter_recommendation:
            filtered_log = filtered_log[filtered_log['Recommendation'] == filter_recommendation]
        
        st.dataframe(filtered_log, use_container_width=True, height=400)
        
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            filtered_log.to_csv(index=False),
            file_name=f"call_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

elif page == "Player Summary":
    st.header("👤 Player Summary")
    
    if st.session_state.call_log.empty:
        st.info("No call logs yet.")
    else:
        selected_player = st.selectbox("Select Player", sorted(st.session_state.call_log['Player Name'].unique().tolist()))
        
        if selected_player:
            player_calls = st.session_state.call_log[st.session_state.call_log['Player Name'] == selected_player]
            
            st.subheader(f"Summary for {selected_player}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Calls", len(player_calls))
            with col2:
                avg_rating = player_calls['Overall Rating'].mean()
                st.metric("Avg Overall Rating", f"{avg_rating:.1f}/10")
            with col3:
                latest_recommendation = player_calls.iloc[-1]['Recommendation']
                st.metric("Latest Recommendation", latest_recommendation)
            with col4:
                latest_date = player_calls.iloc[-1]['Call Date']
                st.metric("Last Call", latest_date)
            
            st.markdown("### Average Ratings")
            rating_cols = ['Communication', 'Maturity', 'Coachability', 'Leadership', 'Work Ethic', 'Confidence', 'Tactical Knowledge', 'Team Fit']
            # Filter to only include columns that exist in the dataframe
            rating_cols = [col for col in rating_cols if col in player_calls.columns]
            if rating_cols:
                avg_ratings = player_calls[rating_cols].mean()
                st.bar_chart(avg_ratings)
            
            st.markdown("### All Calls")
            st.dataframe(player_calls, use_container_width=True)

elif page == "Player Database":
    st.header("👥 Player Database")
    st.markdown("Browse and search all players in the shortlist database.")
    
    if not players_list:
        st.info("No players loaded. Please check that the shortlist file exists.")
    else:
        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Search Player", "")
        with col2:
            filter_conference = st.selectbox("Filter by Conference", [""] + ["ACC", "SEC", "Big Ten", "Big 12", "Ivy League"])
        with col3:
            filter_position = st.selectbox("Filter by Position", [""] + ["Hybrid CB", "DM Box-To-Box", "AM Advanced Playmaker", "Right Touchline Winger"])
        
        # Filter players
        filtered_players = players_list
        if search_term:
            filtered_players = [p for p in filtered_players if search_term.lower() in p.lower()]
        
        # Display player cards
        if filtered_players:
            st.write(f"**Found {len(filtered_players)} players**")
            
            # Show in grid
            cols_per_row = 3
            for i in range(0, len(filtered_players), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, player in enumerate(filtered_players[i:i+cols_per_row]):
                    with cols[j]:
                        player_info = player_info_dict.get(player, {})
                        with st.container():
                            st.markdown(f"### {player}")
                            if player_info:
                                st.write(f"**Team**: {player_info.get('team', 'N/A')}")
                                st.write(f"**Conference**: {player_info.get('conference', 'N/A')}")
                                st.write(f"**Position**: {player_info.get('position', 'N/A')}")
                            
                            # Check if player has call logs
                            if not st.session_state.call_log.empty:
                                player_calls = st.session_state.call_log[st.session_state.call_log['Player Name'] == player]
                                if not player_calls.empty:
                                    st.success(f"✅ {len(player_calls)} call(s) logged")
                                    latest_rec = player_calls.iloc[-1]['Recommendation']
                                    st.caption(f"Latest: {latest_rec}")
                            else:
                                st.caption("No calls logged yet")
        else:
            st.info("No players found matching your search criteria.")

elif page == "Scouting Requests":
    st.header("📋 Scouting Requests")
    st.markdown("Create and manage scouting requests (similar to SAP Scouting Insights).")
    
    # Initialize scouting requests in session state
    if 'scouting_requests' not in st.session_state:
        st.session_state.scouting_requests = pd.DataFrame()
    
    # Load existing requests
    scouting_requests_file = DATA_DIR / 'scouting_requests.csv'
    if scouting_requests_file.exists() and st.session_state.scouting_requests.empty:
        try:
            st.session_state.scouting_requests = pd.read_csv(scouting_requests_file)
        except:
            pass
    
    tab1, tab2 = st.tabs(["Create Request", "View Requests"])
    
    with tab1:
        st.subheader("Create New Scouting Request")
        with st.form("scouting_request_form"):
            request_title = st.text_input("Request Title", placeholder="e.g., 'Evaluate CB prospects for 2025 draft'")
            assigned_to = st.text_input("Assigned To", placeholder="Scout name")
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
            position_focus = st.multiselect(
                "Position Focus",
                ["Hybrid CB", "DM Box-To-Box", "AM Advanced Playmaker", "Right Touchline Winger", "Any"]
            )
            conference_focus = st.multiselect(
                "Conference Focus",
                ["ACC", "SEC", "Big Ten", "Big 12", "Ivy League", "Any"]
            )
            evaluation_criteria = st.text_area(
                "Evaluation Criteria",
                placeholder="What should the scout focus on? Key metrics, attributes, etc."
            )
            deadline = st.date_input("Deadline")
            notes = st.text_area("Additional Notes")
            
            submitted = st.form_submit_button("📝 Create Request", use_container_width=True)
            
            if submitted and request_title:
                new_request = {
                    'Request ID': f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    'Title': request_title,
                    'Assigned To': assigned_to,
                    'Priority': priority,
                    'Position Focus': ', '.join(position_focus) if position_focus else 'Any',
                    'Conference Focus': ', '.join(conference_focus) if conference_focus else 'Any',
                    'Evaluation Criteria': evaluation_criteria,
                    'Deadline': deadline.strftime('%Y-%m-%d'),
                    'Status': 'Open',
                    'Notes': notes,
                    'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if st.session_state.scouting_requests.empty:
                    st.session_state.scouting_requests = pd.DataFrame([new_request])
                else:
                    st.session_state.scouting_requests = pd.concat([st.session_state.scouting_requests, pd.DataFrame([new_request])], ignore_index=True)
                
                st.session_state.scouting_requests.to_csv(scouting_requests_file, index=False)
                st.success(f"✅ Request created: {new_request['Request ID']}")
                st.balloons()
    
    with tab2:
        st.subheader("All Scouting Requests")
        if st.session_state.scouting_requests.empty:
            st.info("No scouting requests yet. Create one in the 'Create Request' tab.")
        else:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_status = st.selectbox("Filter by Status", [""] + sorted(st.session_state.scouting_requests['Status'].unique().tolist()))
            with col2:
                filter_priority = st.selectbox("Filter by Priority", [""] + sorted(st.session_state.scouting_requests['Priority'].unique().tolist()))
            with col3:
                filter_assigned = st.selectbox("Filter by Assigned To", [""] + sorted(st.session_state.scouting_requests['Assigned To'].dropna().unique().tolist()))
            
            filtered_requests = st.session_state.scouting_requests.copy()
            if filter_status:
                filtered_requests = filtered_requests[filtered_requests['Status'] == filter_status]
            if filter_priority:
                filtered_requests = filtered_requests[filtered_requests['Priority'] == filter_priority]
            if filter_assigned:
                filtered_requests = filtered_requests[filtered_requests['Assigned To'] == filter_assigned]
            
            st.dataframe(filtered_requests, use_container_width=True, height=400)
            
            st.download_button(
                "📥 Download Requests (CSV)",
                filtered_requests.to_csv(index=False),
                file_name=f"scouting_requests_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

elif page == "Video Review Tracker":
    st.header("🎥 Video Review Tracker")
    st.markdown("Track video review progress for shortlisted players (complements SAP Performance Insights).")
    
    # Initialize video reviews in session state
    if 'video_reviews' not in st.session_state:
        st.session_state.video_reviews = pd.DataFrame()
    
    # Load existing reviews
    video_reviews_file = DATA_DIR / 'video_reviews.csv'
    if video_reviews_file.exists() and st.session_state.video_reviews.empty:
        try:
            st.session_state.video_reviews = pd.read_csv(video_reviews_file)
        except:
            pass
    
    tab1, tab2, tab3 = st.tabs(["Add Review", "Review Status", "Review Checklist"])
    
    with tab1:
        st.subheader("Add Video Review")
        with st.form("video_review_form"):
            player_name = st.selectbox("Player Name", [""] + players_list[:100])
            review_date = st.date_input("Review Date", value=datetime.now().date())
            games_reviewed = st.text_input("Games Reviewed", placeholder="e.g., 'vs Duke, vs UNC'")
            video_score = st.slider("Video Score (1-10)", 1, 10, 5)
            status = st.selectbox("Review Status", ["Not Started", "In Progress", "Complete"])
            quantitative_match = st.selectbox("Quantitative Match", ["Strong Match", "Mostly Match", "Some Discrepancies", "Significant Discrepancies"])
            key_observations = st.text_area("Key Observations", placeholder="Main takeaways from video review")
            red_flags_video = st.text_area("Red Flags from Video", placeholder="Any concerns observed")
            recommendation_video = st.selectbox("Recommendation", ["Strong Yes", "Yes", "Maybe", "No", "Strong No"])
            notes = st.text_area("Additional Notes")
            
            submitted = st.form_submit_button("💾 Save Review", use_container_width=True)
            
            if submitted and player_name:
                new_review = {
                    'Player Name': player_name,
                    'Review Date': review_date.strftime('%Y-%m-%d'),
                    'Games Reviewed': games_reviewed,
                    'Video Score': video_score,
                    'Status': status,
                    'Quantitative Match': quantitative_match,
                    'Key Observations': key_observations,
                    'Red Flags': red_flags_video,
                    'Recommendation': recommendation_video,
                    'Notes': notes,
                    'Created At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if st.session_state.video_reviews.empty:
                    st.session_state.video_reviews = pd.DataFrame([new_review])
                else:
                    st.session_state.video_reviews = pd.concat([st.session_state.video_reviews, pd.DataFrame([new_review])], ignore_index=True)
                
                st.session_state.video_reviews.to_csv(video_reviews_file, index=False)
                st.success(f"✅ Review saved for {player_name}")
    
    with tab2:
        st.subheader("Review Status Dashboard")
        if st.session_state.video_reviews.empty:
            st.info("No video reviews yet.")
        else:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            total_reviews = len(st.session_state.video_reviews)
            complete_reviews = len(st.session_state.video_reviews[st.session_state.video_reviews['Status'] == 'Complete'])
            avg_score = st.session_state.video_reviews['Video Score'].mean() if 'Video Score' in st.session_state.video_reviews.columns else 0
            
            with col1:
                st.metric("Total Reviews", total_reviews)
            with col2:
                st.metric("Complete", complete_reviews)
            with col3:
                st.metric("In Progress", len(st.session_state.video_reviews[st.session_state.video_reviews['Status'] == 'In Progress']))
            with col4:
                st.metric("Avg Video Score", f"{avg_score:.1f}/10")
            
            # Status breakdown
            st.markdown("### Status Breakdown")
            status_counts = st.session_state.video_reviews['Status'].value_counts()
            st.bar_chart(status_counts)
            
            # Reviews table
            st.markdown("### All Reviews")
            st.dataframe(st.session_state.video_reviews, use_container_width=True, height=400)
    
    with tab3:
        st.subheader("Video Review Checklist")
        st.markdown("Use this checklist when reviewing player videos.")
        st.info("📋 See `Video_Review_Checklist.md` for the full printable checklist.")
        
        selected_player_checklist = st.selectbox("Select Player for Checklist", [""] + players_list[:100])
        if selected_player_checklist:
            st.markdown(f"### Review Checklist for {selected_player_checklist}")
            
            st.markdown("#### Quantitative Validation")
            st.checkbox("Defensive duels match stats?")
            st.checkbox("Passing accuracy matches stats?")
            st.checkbox("Dribbling ability matches stats?")
            st.checkbox("Overall performance level matches score?")
            
            st.markdown("#### Playing Style Assessment")
            st.checkbox("Playing style matches position profile?")
            st.checkbox("Tactical awareness")
            st.checkbox("Decision-making speed")
            st.checkbox("Technical ability")
            st.checkbox("Physical attributes")
            
            st.markdown("#### Intangibles")
            st.checkbox("Body language / attitude")
            st.checkbox("Communication on field")
            st.checkbox("Leadership presence")
            st.checkbox("Resilience (response to mistakes)")
            st.checkbox("Work rate off the ball")
            
            st.markdown("#### Portland Thorns Fit")
            st.checkbox("Fits playing style?")
            st.checkbox("Fits team culture?")
            st.checkbox("Can adapt to NWSL pace?")
            st.checkbox("Potential to grow?")

elif page == "Export to SAP":
    st.header("📤 Export to SAP")
    st.markdown("Export data in SAP-compatible formats for integration.")
    
    export_type = st.radio(
        "Select Export Type",
        ["Call Logs", "Player Database", "Video Reviews", "Scouting Requests", "Combined Export"]
    )
    
    if export_type == "Call Logs":
        if st.session_state.call_log.empty:
            st.info("No call logs to export.")
        else:
            st.subheader("Call Logs Export")
            st.write(f"**Total Records**: {len(st.session_state.call_log)}")
            
            # SAP-compatible format options
            st.markdown("### Export Format")
            format_option = st.selectbox("Format", ["CSV (Standard)", "CSV (SAP Format)", "Excel"])
            
            if format_option == "CSV (SAP Format)":
                # Create SAP-compatible format
                sap_df = st.session_state.call_log.copy()
                # Rename columns to SAP-friendly names
                column_mapping = {
                    'Player Name': 'Player_Name',
                    'Call Date': 'Call_Date',
                    'Team': 'Team',
                    'Conference': 'Conference',
                    'Overall Rating': 'Overall_Rating',
                    'Recommendation': 'Recommendation'
                }
                sap_df = sap_df.rename(columns=column_mapping)
                
                st.download_button(
                    "📥 Download SAP Format (CSV)",
                    sap_df.to_csv(index=False),
                    file_name=f"sap_call_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.info("💡 This format uses SAP-friendly column names (underscores, no spaces).")
            else:
                st.download_button(
                    f"📥 Download {format_option}",
                    st.session_state.call_log.to_csv(index=False) if format_option == "CSV (Standard)" else None,
                    file_name=f"call_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    elif export_type == "Player Database":
        st.subheader("Player Database Export")
        if not players_list:
            st.info("No players loaded.")
        else:
            # Create player database export
            player_db_export = []
            for player in players_list:
                info = player_info_dict.get(player, {})
                player_db_export.append({
                    'Player_Name': player,
                    'Team': info.get('team', ''),
                    'Conference': info.get('conference', ''),
                    'Position': info.get('position', '')
                })
            
            player_db_df = pd.DataFrame(player_db_export)
            st.dataframe(player_db_df, use_container_width=True)
            
            st.download_button(
                "📥 Download Player Database (CSV)",
                player_db_df.to_csv(index=False),
                file_name=f"sap_player_database_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif export_type == "Video Reviews":
        if 'video_reviews' in st.session_state and not st.session_state.video_reviews.empty:
            st.subheader("Video Reviews Export")
            st.write(f"**Total Reviews**: {len(st.session_state.video_reviews)}")
            st.download_button(
                "📥 Download Video Reviews (CSV)",
                st.session_state.video_reviews.to_csv(index=False),
                file_name=f"sap_video_reviews_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No video reviews to export.")
    
    elif export_type == "Scouting Requests":
        if 'scouting_requests' in st.session_state and not st.session_state.scouting_requests.empty:
            st.subheader("Scouting Requests Export")
            st.write(f"**Total Requests**: {len(st.session_state.scouting_requests)}")
            st.download_button(
                "📥 Download Scouting Requests (CSV)",
                st.session_state.scouting_requests.to_csv(index=False),
                file_name=f"sap_scouting_requests_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No scouting requests to export.")
    
    elif export_type == "Combined Export":
        st.subheader("Combined Export for SAP")
        st.markdown("Export all data in one SAP-compatible file.")
        
        # Combine all data sources
        combined_data = {
            'Call_Logs': len(st.session_state.call_log) if not st.session_state.call_log.empty else 0,
            'Players': len(players_list),
            'Video_Reviews': len(st.session_state.video_reviews) if 'video_reviews' in st.session_state and not st.session_state.video_reviews.empty else 0,
            'Scouting_Requests': len(st.session_state.scouting_requests) if 'scouting_requests' in st.session_state and not st.session_state.scouting_requests.empty else 0
        }
        
        st.write("**Export Summary:**")
        for key, value in combined_data.items():
            st.write(f"- {key}: {value} records")
        
        st.info("💡 Use individual exports above for specific data types, or combine manually in Excel/SAP.")

elif page == "Export Data":
    st.header("📊 Export Data")
    
    if st.session_state.call_log.empty:
        st.info("No data to export.")
    else:
        st.download_button(
            "📥 Download Full Call Log (CSV)",
            st.session_state.call_log.to_csv(index=False),
            file_name=f"full_call_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Excel export requires BytesIO
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.call_log.to_excel(writer, index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            "📥 Download Full Call Log (Excel)",
            excel_data,
            file_name=f"full_call_log_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("### Summary Statistics")
        st.write(f"**Total Calls Logged**: {len(st.session_state.call_log)}")
        st.write(f"**Unique Players**: {st.session_state.call_log['Player Name'].nunique()}")
        st.write(f"**Average Overall Rating**: {st.session_state.call_log['Overall Rating'].mean():.2f}/10")
        
        st.markdown("### Recommendations Breakdown")
        st.bar_chart(st.session_state.call_log['Recommendation'].value_counts())

elif page == "View Player Overview":
    st.title("📄 Player Overview PDF Viewer")
    st.markdown("View player overview PDFs generated from the scouting system.")
    
    # Find all available PDFs
    pdf_files = []
    if OVERVIEW_DIR.exists():
        # Search in Top 15 and Other folders
        for folder_type in ['Top 15', 'Other']:
            folder_path = OVERVIEW_DIR / folder_type
            if folder_path.exists():
                for position_folder in folder_path.iterdir():
                    if position_folder.is_dir():
                        for pdf_file in position_folder.glob('*.pdf'):
                            pdf_files.append({
                                'path': pdf_file,
                                'name': pdf_file.stem,
                                'position': position_folder.name,
                                'type': folder_type
                            })
    
    if pdf_files:
        # Create a searchable dropdown
        pdf_names = sorted([f"{p['name']} ({p['type']})" for p in pdf_files])
        selected_pdf_name = st.selectbox("Select Player Overview", [""] + pdf_names)
        
        if selected_pdf_name:
            # Find the selected PDF
            selected_pdf = None
            for pdf in pdf_files:
                if f"{pdf['name']} ({pdf['type']})" == selected_pdf_name:
                    selected_pdf = pdf
                    break
            
            if selected_pdf and selected_pdf['path'].exists():
                # Display PDF info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Position", selected_pdf['position'].replace('_', ' '))
                with col2:
                    st.metric("Category", selected_pdf['type'])
                with col3:
                    file_size = selected_pdf['path'].stat().st_size / 1024
                    st.metric("File Size", f"{file_size:.1f} KB")
                
                # Display the PDF
                try:
                    with open(selected_pdf['path'], 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=selected_pdf['path'].name,
                            mime="application/pdf"
                        )
                        # Display PDF using iframe
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error loading PDF: {e}")
            else:
                st.error("PDF file not found")
    else:
        st.warning("⚠️ No player overview PDFs found. Please generate overviews first.")
        st.info("💡 PDFs should be located in: `Player Overviews/Top 15/` or `Player Overviews/Other/`")

elif page == "Update Player Overviews":
    st.header("🔄 Update Player Overviews with Call Data")
    st.markdown("---")
    
    st.info("""
    This feature will regenerate player overview PDFs to include qualitative information from call logs.
    The enhanced overviews will combine:
    - **Quantitative metrics** (existing player data)
    - **Call notes and assessments** (from your conversations with players/agents)
    """)
    
    # Check if call log exists
    if CALL_LOG_FILE.exists():
        call_log_df = load_call_log()
        players_with_calls = call_log_df['Player Name'].unique() if not call_log_df.empty else []
        
        if players_with_calls:
            st.success(f"✅ Found {len(players_with_calls)} players with call data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_player = st.selectbox(
                    "Select Player to Update",
                    [""] + sorted(players_with_calls.tolist())
                )
            
            with col2:
                update_option = st.radio(
                    "Update Option",
                    ["Single Player", "All Players with Calls"],
                    help="Update one player or regenerate all overviews"
                )
            
            if st.button("🔄 Regenerate Player Overview(s)", use_container_width=True):
                if update_option == "Single Player" and selected_player:
                    with st.spinner(f"Regenerating overview for {selected_player}..."):
                        try:
                            # Use the update script for single player
                            import subprocess
                            script_path = Path(__file__).parent / 'update_overviews_with_calls.py'
                            if script_path.exists():
                                result = subprocess.run(
                                    ['python3', str(script_path)],
                                    capture_output=True,
                                    text=True,
                                    cwd=str(script_path.parent)
                                )
                                if result.returncode == 0:
                                    st.success(f"✅ Overview regenerated for {selected_player}")
                                    st.info("💡 The overview PDF now includes call notes and assessments")
                                    if result.stdout:
                                        st.text(result.stdout[-300:])
                                else:
                                    st.error(f"❌ Error running script: {result.stderr}")
                                    if result.stdout:
                                        st.text(result.stdout[-500:])
                            else:
                                # Fallback to full generation script
                                script_path = Path(__file__).parent / 'generate_player_overviews.py'
                                if script_path.exists():
                                    result = subprocess.run(
                                        ['python3', str(script_path)],
                                        capture_output=True,
                                        text=True,
                                        cwd=str(script_path.parent)
                                    )
                                    if result.returncode == 0:
                                        st.success(f"✅ Overview regenerated")
                                        st.info("💡 The overview PDF now includes call notes and assessments")
                                else:
                                    st.error(f"❌ Script not found")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            st.code(str(e))
                
                elif update_option == "All Players with Calls":
                    with st.spinner(f"Regenerating overviews for {len(players_with_calls)} players..."):
                        try:
                            import subprocess
                            # Use the update script which only updates players with calls
                            script_path = Path(__file__).parent / 'update_overviews_with_calls.py'
                            if script_path.exists():
                                result = subprocess.run(
                                    ['python3', str(script_path)],
                                    capture_output=True,
                                    text=True,
                                    cwd=str(script_path.parent)
                                )
                                if result.returncode == 0:
                                    st.success(f"✅ Regenerated player overviews with call data")
                                    st.info("💡 All overview PDFs now include call notes and assessments where available")
                                    if result.stdout:
                                        st.text(result.stdout[-500:])  # Show last 500 chars
                                else:
                                    st.error(f"❌ Error running script: {result.stderr}")
                                    if result.stdout:
                                        st.text(result.stdout[-500:])
                            else:
                                # Fallback to full generation script
                                script_path = Path(__file__).parent / 'generate_player_overviews.py'
                                if script_path.exists():
                                    result = subprocess.run(
                                        ['python3', str(script_path)],
                                        capture_output=True,
                                        text=True,
                                        cwd=str(script_path.parent)
                                    )
                                    if result.returncode == 0:
                                        st.success(f"✅ Regenerated all player overviews")
                                        st.info("💡 All overview PDFs now include call notes and assessments where available")
                                else:
                                    st.error(f"❌ Script not found")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            st.code(str(e))
                else:
                    st.warning("⚠️ Please select a player or choose 'All Players with Calls'")
            
            st.markdown("---")
            st.markdown("""
            **How it works:**
            1. The script finds all players with call log entries
            2. It regenerates their overview PDFs using the existing generation script
            3. The enhanced PDFs include a new "Call Notes & Assessment" section
            4. All existing quantitative data is preserved
            """)
        else:
            st.warning("⚠️ No players with call data found. Log some calls first!")
    else:
        st.warning("⚠️ Call log file not found. Please log some calls first.")

# Player Overview PDF Viewer Page
elif page == "View Player Overview":
    st.title("📄 Player Overview PDF Viewer")
    st.markdown("View player overview PDFs generated from the scouting system.")
    
    # Find all available PDFs
    pdf_files = []
    if OVERVIEW_DIR.exists():
        # Search in Top 15 and Other folders
        for folder_type in ['Top 15', 'Other']:
            folder_path = OVERVIEW_DIR / folder_type
            if folder_path.exists():
                for position_folder in folder_path.iterdir():
                    if position_folder.is_dir():
                        for pdf_file in position_folder.glob('*.pdf'):
                            pdf_files.append({
                                'path': pdf_file,
                                'name': pdf_file.stem,
                                'position': position_folder.name,
                                'type': folder_type
                            })
    
    if pdf_files:
        # Create a searchable dropdown
        pdf_names = sorted([f"{p['name']} ({p['type']})" for p in pdf_files])
        selected_pdf_name = st.selectbox("Select Player Overview", [""] + pdf_names)
        
        if selected_pdf_name:
            # Find the selected PDF
            selected_pdf = None
            for pdf in pdf_files:
                if f"{pdf['name']} ({pdf['type']})" == selected_pdf_name:
                    selected_pdf = pdf
                    break
            
            if selected_pdf and selected_pdf['path'].exists():
                # Display PDF info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Position", selected_pdf['position'].replace('_', ' '))
                with col2:
                    st.metric("Category", selected_pdf['type'])
                with col3:
                    file_size = selected_pdf['path'].stat().st_size / 1024
                    st.metric("File Size", f"{file_size:.1f} KB")
                
                # Display the PDF
                try:
                    with open(selected_pdf['path'], 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=selected_pdf['path'].name,
                            mime="application/pdf"
                        )
                        # Display PDF using iframe
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error loading PDF: {e}")
            else:
                st.error("PDF file not found")
    else:
        st.warning("⚠️ No player overview PDFs found. Please generate overviews first.")
        st.info("💡 PDFs should be located in: `Player Overviews/Top 15/` or `Player Overviews/Other/`")

# Footer
st.markdown("---")
st.caption("Portland Thorns Scouting System | Data stored locally in CSV format")

