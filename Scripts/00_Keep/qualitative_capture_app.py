#!/usr/bin/env python3
"""
Streamlit app for capturing qualitative information from player/agent calls.
Stores data in CSV format for easy export and sharing.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, date
import json
from io import BytesIO
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Google Drive integration
GOOGLE_DRIVE_AVAILABLE = False
try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    from pydrive2.files import FileNotUploadedError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

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
    layout="wide"
)

# ===========================================
# AUTHENTICATION CONFIGURATION
# ===========================================
USERNAME = "MikeNorris"
PASSWORD = "1234"

# Initialize authentication state - persist across reruns
# Use query params as backup for hard refresh (CMD+R)
if "auth" not in st.session_state:
    # Check query params first (for hard refresh scenarios)
    try:
        qp = st.query_params
        auth_token = qp.get("auth_token", None)
        if auth_token == "authenticated":
            st.session_state["auth"] = True
        else:
            st.session_state["auth"] = False
    except:
        st.session_state["auth"] = False

# Set query param when authenticated to persist across hard refresh
if st.session_state.get("auth", False):
    try:
        st.query_params["auth_token"] = "authenticated"
    except:
        pass

# ===========================================
# LOGIN PAGE FUNCTION
# ===========================================
def login_page():
    """Display login page with Portland Thorns branding."""
    st.markdown("""
        <style>
        [data-testid="stSidebar"], [data-testid="stToolbar"], header[data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            background-size: cover;
            background-position: center;
        }
        div.block-container {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
            padding-top: 0 !important;
        }
        .login-container {
            background: rgba(20, 20, 25, 0.95);
            border: 2px solid #8B0000;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(139, 0, 0, 0.5);
            backdrop-filter: blur(12px);
            width: 450px;
            padding: 3rem 3rem;
            margin: auto;
            display: flex !important;
            flex-direction: column;
            justify-content: center;
            align-items: stretch;
        }
        .login-title {
            font-size: 2.2rem;
            font-weight: 900;
            color: #8B0000;
            margin-bottom: 0.4rem;
            text-align: center;
            text-shadow: 0 0 12px rgba(139, 0, 0, 0.5);
        }
        .login-sub {
            text-align: center;
            color: #f0f2f5;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        label { 
            color: #d7dee8 !important; 
            font-weight: 600 !important; 
            font-size: 0.95rem !important; 
        }
        input[type="text"], input[type="password"] {
            background-color: #0f1625 !important;
            color: #e8eef7 !important;
            border: 1px solid rgba(139, 0, 0, 0.3) !important;
            border-radius: 10px !important;
            height: 48px !important;
            font-size: 0.95rem !important;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #8B0000 !important;
            box-shadow: 0 0 10px rgba(139, 0, 0, 0.3) !important;
        }
        button[kind="primary"] {
            background-color: #8B0000 !important;
            border-radius: 10px !important;
            color: white !important;
            height: 48px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }
        button[kind="primary"]:hover {
            background: linear-gradient(90deg, #8B0000, #D10023) !important;
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(139, 0, 0, 0.4);
        }
        @keyframes fadein {
            from { opacity: 0; transform: translateY(-15px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .login-container {
            animation: fadein 0.8s ease;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo and branding
    logo_path = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Branding/portland-thorns-vector-logo-seeklogo/portland-thorns-seeklogo.png")
    
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_data = f.read()
            logo_base64 = base64.b64encode(logo_data).decode()
        
        st.markdown(f"""
            <div style="text-align:center; margin-bottom: 1.5rem;">
                <img src="data:image/png;base64,{logo_base64}" width="180" style="animation: fadein 1s ease;">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align:center; margin-bottom: 1.5rem;">
                <h1 style="color: #8B0000; font-size: 2.5rem;">Portland Thorns</h1>
            </div>
        """, unsafe_allow_html=True)

    # Login form
    placeholder = st.empty()
    with placeholder.container():
        st.markdown('<div class="login-title">Call Log System</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Player & Agent Call Management Platform</div>', unsafe_allow_html=True)

        user = st.text_input("Username", placeholder="Enter your username", key="login_username")
        pwd = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Login", use_container_width=True, type="primary"):
                if user == USERNAME and pwd == PASSWORD:
                    st.session_state["auth"] = True
                    # Set query param to persist auth across refresh
                    try:
                        st.query_params["auth_token"] = "authenticated"
                    except:
                        pass
                    st.success("Login successful")
                    import time
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password")

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.85rem; margin-top: 1rem;">
            Designed and created by Daniel Levitt<br>
            <a href="mailto:daniellevitt32@gmail.com" style="color: #8B0000; text-decoration: none;">daniellevitt32@gmail.com</a>
        </div>
        """, unsafe_allow_html=True)

# Portland Thorns Branding Colors
THORNS_DARK_RED = "#8B0000"  # Dark red from color scale
THORNS_RED = "#D10023"  # Primary red
THORNS_WHITE = "#FFFFFF"
THORNS_BLACK = "#000000"

# Custom CSS for Portland Thorns branding
st.markdown(f"""
<style>
    /* Main branding styles */
    .main .block-container {{
        padding-top: 2rem;
    }}
    
    /* Header with logo and designer credit */
    .branding-header {{
        background: linear-gradient(135deg, {THORNS_DARK_RED} 0%, {THORNS_RED} 100%);
        padding: 1rem 2rem;
        margin: -1rem -2rem 2rem -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    .branding-logo {{
        height: 70px;
        width: auto;
    }}
    
    .designer-credit {{
        color: {THORNS_WHITE};
        font-size: 0.85rem;
        font-weight: 400;
        text-align: right;
    }}
    
    /* Primary button styling */
    .stButton > button {{
        background-color: {THORNS_DARK_RED};
        color: {THORNS_WHITE};
        border: none;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {THORNS_RED};
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(139, 0, 0, 0.3);
    }}
    
    /* Sidebar styling - reduce spacing between sections */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
    }}
    [data-testid="stSidebar"] hr {{
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Target block container directly to reduce spacing - using negative margins */
    .main .block-container {{
        padding-bottom: 0 !important;
    }}
    /* Specifically target the div containing the HTML table iframe - negative margin */
    .main .block-container > div:has([data-testid="stIFrame"]) {{
        margin-bottom: -2rem !important;
        padding-bottom: 0 !important;
    }}
    /* Tab styling - make labels bigger */
    [data-testid="stTabs"] button {{
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        padding: 0.85rem 1.75rem !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab"] {{
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        padding: 0.85rem 1.75rem !important;
    }}
    [data-testid="stTabs"] [role="tab"] {{
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        padding: 0.85rem 1.75rem !important;
    }}
    
    /* Target the div containing the divider that comes after the table - negative margin */
    .main .block-container > div:has([data-testid="stIFrame"]) + div:has(hr) {{
        margin-top: -2rem !important;
        margin-bottom: -1rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}
    /* Target the divider itself - minimal margins */
    .main .block-container > div:has(hr) hr {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }}
    /* Target the div after the divider (radar chart section) - negative margin */
    .main .block-container > div:has(hr) + div {{
        margin-top: -1.5rem !important;
        padding-top: 0 !important;
    }}
    /* Reduce spacing for HTML components (tables) - negative margins */
    iframe[title*="streamlit"] {{
        margin-bottom: -1rem !important;
        margin-top: 0 !important;
        padding: 0 !important;
        display: block !important;
    }}
    [data-testid="stIFrame"] {{
        margin-bottom: -1rem !important;
        margin-top: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stIFrame"] {{
        margin-bottom: -1rem !important;
        margin-top: 0 !important;
        padding: 0 !important;
    }}
    /* Reduce divider spacing globally */
    hr {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }}
    .css-1d391kg {{
        background-color: #1e1e1e;
    }}
    
    /* Metric cards */
    [data-testid="stMetricValue"] {{
        color: {THORNS_DARK_RED};
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {THORNS_DARK_RED};
    }}
    
    /* Info boxes */
    .stInfo {{
        border-left: 4px solid {THORNS_DARK_RED};
    }}
    
    /* Success messages */
    .stSuccess {{
        border-left: 4px solid #00CC66;
    }}
    
    /* Selectbox and input focus */
    .stSelectbox > div > div {{
        border-color: {THORNS_DARK_RED};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {THORNS_DARK_RED};
        border-bottom: 2px solid transparent;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {THORNS_DARK_RED};
        border-bottom-color: {THORNS_DARK_RED};
    }}
</style>
""", unsafe_allow_html=True)

# Load and display logo + designer credit at top of every page
def display_branding_header():
    """Display Portland Thorns logo and designer credit at top of every page."""
    logo_path = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Branding/portland-thorns-vector-logo-seeklogo/portland-thorns-seeklogo.png")
    
    if logo_path.exists():
        # Read logo and convert to base64
        with open(logo_path, "rb") as f:
            logo_data = f.read()
            logo_base64 = base64.b64encode(logo_data).decode()
        
        st.markdown(f"""
        <div class="branding-header">
            <img src="data:image/png;base64,{logo_base64}" class="branding-logo" alt="Portland Thorns Logo">
            <div class="designer-credit">
                Designed and created by Daniel Levitt<br>
                <a href="mailto:daniellevitt32@gmail.com" style="color: {THORNS_WHITE}; text-decoration: none;">daniellevitt32@gmail.com</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback if logo not found
        st.markdown(f"""
        <div class="branding-header">
            <h2 style="color: {THORNS_WHITE}; margin: 0;">Portland Thorns</h2>
            <div class="designer-credit">
                Designed and created by Daniel Levitt<br>
                <a href="mailto:daniellevitt32@gmail.com" style="color: {THORNS_WHITE}; text-decoration: none;">daniellevitt32@gmail.com</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Language translations
TRANSLATIONS = {
    'English': {
        'title': 'Portland Thorns - Call Log System',
        'welcome_title': 'Welcome - Getting Started',
        'what_app_does': 'What This App Does',
        'what_app_does_desc': 'This system helps you capture and organize qualitative information from player and agent calls:',
        'log_calls': 'Log Calls: Record detailed information from conversations with players and agents',
        'track_assessments': 'Track Assessments: Rate players on communication, maturity, coachability, and more',
        'generate_reports': 'Generate Reports: Download PDF summaries and CSV exports',
        'view_history': 'View History: Review past calls and player summaries',
        'player_overviews': 'Player Overviews: View detailed scouting reports with charts and comparisons',
        'first_steps': 'First Steps',
        'upload_database': 'Upload Player Database (if not already done)',
        'upload_database_desc': 'Use the sidebar uploader to add your shortlist Excel file. This enables player selection and auto-population.',
        'log_first_call': 'Log Your First Call',
        'log_first_call_desc': 'Select a player from the database (or enter custom player). Fill out the call details and assessments. Save to generate PDF and CSV files.',
        'explore_features': 'Explore Features',
        'explore_features_desc': 'View call history to see all logged calls. Check player summaries for aggregated insights. Upload and view player overview PDFs.',
        'tips': 'Tips',
        'save_draft_tip': 'Use "Save Draft" to save progress without submitting',
        'search_tip': 'Search players by name in the player selection dropdown',
        'download_tip': 'Download PDFs and CSVs after each call for your records',
        'autopopulate_tip': 'Conference and Team auto-populate when you select a player',
        'ready_to_start': 'Ready to start? Close this section and begin logging your first call!',
        'got_it': 'Got it! Hide this message',
        'quick_start': 'Quick Start Guide',
        'how_to_use': 'How to Use This App',
        'step1': 'Upload Player Database (First Time Only)',
        'step1_desc': 'Upload your shortlist Excel file in the sidebar above. File will be saved permanently.',
        'step2': 'Log a New Call',
        'step2_desc': 'Select Conference → Team → Player. Fill out call details and assessments. Click "Save Call Log" at the bottom.',
        'step3': 'Download Results',
        'step3_desc': 'PDF and CSV files available after saving. View call history anytime.',
        'step4': 'View Player Overviews',
        'step4_desc': 'Upload PDF overviews or view existing ones. Compare players across metrics.',
        # Form labels
        'log_new_call': 'Phone Calls',
        'player_not_in_database': 'Player not in database',
        'player_name': 'Player Name',
        'enter_player_name': 'Enter player name',
        'conference': 'Conference',
        'team': 'Team',
        'position': 'Position',
        'search_player': 'Search Player',
        'call_date': 'Call Date',
        'call_type': 'Call Type',
        'call_number': 'Call Number',
        'duration_minutes': 'Duration (minutes)',
        'participants': 'Participants',
        'list_participants': 'List all participants in the call',
        'call_notes': 'Call Notes',
        'general_notes': 'General notes about the call',
        'agent_assessment': 'Agent Assessment',
        'agent_name': 'Agent Name',
        'or_enter_new_agent': 'Or enter new agent name',
        'leave_empty_if_using_dropdown': 'Leave empty if using dropdown above',
        'relationship': 'Relationship',
        'relationship_other': 'Relationship (Other)',
        'specify_if_other': "Specify if 'Other' selected",
        'agent_professionalism': 'Agent Professionalism (1-10)',
        'agent_responsiveness': 'Agent Responsiveness (1-10)',
        'reasonable_expectations': 'Reasonable Expectations (1-10)',
        'transparency_honesty': 'Transparency/Honesty (1-10)',
        'negotiation_style': 'Negotiation Style (1-10)',
        'negotiation_help': '1 = Aggressive, 10 = Collaborative',
        'agent_notes': 'Agent Notes',
        'player_notes_section': 'Player Notes',
        'player_notes_field': 'Player Notes',
        'general_notes_player': 'General notes about the player',
        'personality_self_awareness': 'Personality & Self Awareness',
        'how_they_carry': 'How They Carry Themselves',
        'how_they_carry_placeholder': 'Describe how the player presents themselves',
        'preparation_level': 'How prepared are they? (1-10)',
        'preparation_help': 'Knowledge of Portland Thorns and readiness to ask questions',
        'preparation_notes': 'Preparation Notes',
        'preparation_notes_placeholder': 'What questions did they ask? What did they know?',
        'how_they_view': 'How They View Themselves',
        'how_they_view_placeholder': 'How does the player describe themselves?',
        'what_important': 'What Is Important To Them',
        'what_important_placeholder': 'What matters most to this player?',
        'mindset_growth': 'Mindset Towards Growth',
        'mindset_growth_placeholder': 'How do they approach learning and improvement?',
        'has_big_injuries': 'Has Big Injuries',
        'injury_periods': 'Injury Periods',
        'injury_periods_placeholder': 'Describe injury history and recovery periods',
        'personality_traits': 'Personality Traits',
        'other_traits': 'Other traits (comma-separated)',
        'key_talking_points_section': 'Key Talking Points',
        'interest_level': 'Interest Level in Portland',
        'timeline': 'Graduation Timeline',
        'timeline_custom': 'Timeline (Custom)',
        'enter_custom_timeline': 'Enter custom timeline',
        'salary_expectations': 'Salary Expectations',
        'if_discussed': 'If discussed',
        'other_opportunities': 'Other Opportunities',
        'other_opportunities_placeholder': 'Other teams/opportunities mentioned',
        'key_talking_points': 'Key Talking Points',
        'main_discussion_points': 'Main discussion points',
        'red_flags_concerns': 'Red Flags & Concerns',
        'severity': 'Severity',
        'red_flags': 'Red Flags / Concerns',
        'any_concerns': 'Any concerns or red flags',
        'overall_assessment': 'Overall Assessment',
        'assessment_summary': 'Assessment Summary',
        'total_assessment_score': 'Total Assessment Score',
        'assessment_percentage': 'Assessment Percentage',
        'grade': 'Grade',
        'recommendation': 'Recommendation',
        'summary_notes': 'Summary Notes',
        'overall_impression': 'Overall impression and summary',
        'next_steps': 'Next Steps',
        'follow_up_needed': 'Follow-up Needed',
        'follow_up_date': 'Follow-up Date',
        'action_items': 'Action Items',
        'what_needs_happen': 'What needs to happen next?',
        'save_call_log': 'Save Call Log',
        'save_draft': 'Save Draft',
        'save_progress': 'Save Progress',
    },
    'Spanish': {
        'title': 'Portland Thorns - Sistema de Registro de Llamadas',
        'welcome_title': 'Bienvenido - Comenzar',
        'what_app_does': 'Qué Hace Esta Aplicación',
        'what_app_does_desc': 'Este sistema te ayuda a capturar y organizar información cualitativa de llamadas con jugadores y agentes:',
        'log_calls': 'Registrar Llamadas: Registra información detallada de conversaciones con jugadores y agentes',
        'track_assessments': 'Seguir Evaluaciones: Califica jugadores en comunicación, madurez, capacidad de entrenamiento y más',
        'generate_reports': 'Generar Informes: Descarga resúmenes PDF y exportaciones CSV',
        'view_history': 'Ver Historial: Revisa llamadas pasadas y resúmenes de jugadores',
        'player_overviews': 'Resúmenes de Jugadores: Ver informes de scouting detallados con gráficos y comparaciones',
        'first_steps': 'Primeros Pasos',
        'upload_database': 'Subir Base de Datos de Jugadores (si aún no se ha hecho)',
        'upload_database_desc': 'Usa el cargador en la barra lateral para agregar tu archivo Excel de lista corta. Esto permite la selección de jugadores y auto-completado.',
        'log_first_call': 'Registrar Tu Primera Llamada',
        'log_first_call_desc': 'Selecciona un jugador de la base de datos (o ingresa un jugador personalizado). Completa los detalles de la llamada y evaluaciones. Guarda para generar archivos PDF y CSV.',
        'explore_features': 'Explorar Funciones',
        'explore_features_desc': 'Ver historial de llamadas para ver todas las llamadas registradas. Revisa resúmenes de jugadores para información agregada. Sube y visualiza PDFs de resúmenes de jugadores.',
        'tips': 'Consejos',
        'save_draft_tip': 'Usa "Guardar Borrador" para guardar el progreso sin enviar',
        'search_tip': 'Busca jugadores por nombre en el menú desplegable de selección',
        'download_tip': 'Descarga PDFs y CSVs después de cada llamada para tus registros',
        'autopopulate_tip': 'Conferencia y Equipo se auto-completan cuando seleccionas un jugador',
        'ready_to_start': '¿Listo para comenzar? ¡Cierra esta sección y comienza a registrar tu primera llamada!',
        'got_it': '¡Entendido! Ocultar este mensaje',
        'quick_start': 'Guía de Inicio Rápido',
        'how_to_use': 'Cómo Usar Esta Aplicación',
        'step1': 'Subir Base de Datos de Jugadores (Solo Primera Vez)',
        'step1_desc': 'Sube tu archivo Excel de lista corta en la barra lateral arriba. El archivo se guardará permanentemente.',
        'step2': 'Registrar una Nueva Llamada',
        'step2_desc': 'Selecciona Conferencia → Equipo → Jugador. Completa los detalles de la llamada y evaluaciones. Haz clic en "Guardar Registro de Llamada" al final.',
        'step3': 'Descargar Resultados',
        'step3_desc': 'Archivos PDF y CSV disponibles después de guardar. Ver historial de llamadas en cualquier momento.',
        'step4': 'Ver Resúmenes de Jugadores',
        'step4_desc': 'Sube resúmenes PDF o visualiza los existentes. Compara jugadores en todas las métricas.',
        # Form labels
        'log_new_call': 'Registrar Nueva Llamada',
        'player_not_in_database': 'Jugador no está en la base de datos',
        'player_name': 'Nombre del Jugador',
        'enter_player_name': 'Ingresa el nombre del jugador',
        'conference': 'Conferencia',
        'team': 'Equipo',
        'position': 'Posición',
        'search_player': 'Buscar Jugador',
        'call_date': 'Fecha de la Llamada',
        'call_type': 'Tipo de Llamada',
        'call_number': 'Número de Llamada',
        'duration_minutes': 'Duración (minutos)',
        'participants': 'Participantes',
        'list_participants': 'Lista todos los participantes en la llamada',
        'call_notes': 'Notas de la Llamada',
        'general_notes': 'Notas generales sobre la llamada',
        'agent_assessment': 'Evaluación del Agente',
        'agent_name': 'Nombre del Agente',
        'or_enter_new_agent': 'O ingresa un nuevo nombre de agente',
        'leave_empty_if_using_dropdown': 'Deja vacío si usas el menú desplegable arriba',
        'relationship': 'Relación',
        'relationship_other': 'Relación (Otro)',
        'specify_if_other': "Especifica si se seleccionó 'Otro'",
        'agent_professionalism': 'Profesionalismo del Agente (1-10)',
        'agent_responsiveness': 'Capacidad de Respuesta del Agente (1-10)',
        'reasonable_expectations': 'Expectativas Razonables (1-10)',
        'transparency_honesty': 'Transparencia/Honestidad (1-10)',
        'negotiation_style': 'Estilo de Negociación (1-10)',
        'negotiation_help': '1 = Agresivo, 10 = Colaborativo',
        'agent_notes': 'Notas del Agente',
        'player_notes_section': 'Notas del Jugador',
        'player_notes_field': 'Notas del Jugador',
        'general_notes_player': 'Notas generales sobre el jugador',
        'personality_self_awareness': 'Personalidad y Autoconciencia',
        'how_they_carry': 'Cómo Se Presentan',
        'how_they_carry_placeholder': 'Describe cómo se presenta el jugador',
        'preparation_level': '¿Qué tan preparados están? (1-10)',
        'preparation_help': 'Conocimiento de Portland Thorns y disposición para hacer preguntas',
        'preparation_notes': 'Notas de Preparación',
        'preparation_notes_placeholder': '¿Qué preguntas hicieron? ¿Qué sabían?',
        'how_they_view': 'Cómo Se Ven a Sí Mismos',
        'how_they_view_placeholder': '¿Cómo se describe el jugador?',
        'what_important': 'Qué Es Importante Para Ellos',
        'what_important_placeholder': '¿Qué es lo más importante para este jugador?',
        'mindset_growth': 'Mentalidad Hacia el Crecimiento',
        'mindset_growth_placeholder': '¿Cómo abordan el aprendizaje y la mejora?',
        'has_big_injuries': 'Tiene Lesiones Importantes',
        'injury_periods': 'Períodos de Lesión',
        'injury_periods_placeholder': 'Describe el historial de lesiones y períodos de recuperación',
        'personality_traits': 'Rasgos de Personalidad',
        'other_traits': 'Otros rasgos (separados por comas)',
        'key_talking_points_section': 'Puntos Clave de Conversación',
        'interest_level': 'Nivel de Interés en Portland',
        'timeline': 'Cronograma',
        'timeline_custom': 'Cronograma (Personalizado)',
        'enter_custom_timeline': 'Ingresa cronograma personalizado',
        'salary_expectations': 'Expectativas Salariales',
        'if_discussed': 'Si se discutió',
        'other_opportunities': 'Otras Oportunidades',
        'other_opportunities_placeholder': 'Otros equipos/oportunidades mencionadas',
        'key_talking_points': 'Puntos Clave de Conversación',
        'main_discussion_points': 'Puntos principales de discusión',
        'red_flags_concerns': 'Banderas Rojas y Preocupaciones',
        'severity': 'Severidad',
        'red_flags': 'Banderas Rojas / Preocupaciones',
        'any_concerns': 'Cualquier preocupación o bandera roja',
        'overall_assessment': 'Evaluación General',
        'assessment_summary': 'Resumen de Evaluación',
        'total_assessment_score': 'Puntuación Total de Evaluación',
        'assessment_percentage': 'Porcentaje de Evaluación',
        'grade': 'Calificación',
        'recommendation': 'Recomendación',
        'summary_notes': 'Notas Resumen',
        'overall_impression': 'Impresión general y resumen',
        'next_steps': 'Próximos Pasos',
        'follow_up_needed': 'Seguimiento Necesario',
        'follow_up_date': 'Fecha de Seguimiento',
        'action_items': 'Elementos de Acción',
        'what_needs_happen': '¿Qué necesita suceder a continuación?',
        'save_call_log': 'Guardar Registro de Llamada',
        'save_draft': 'Guardar Borrador',
        'save_progress': 'Guardar Progreso',
    },
    'French': {
        'title': 'Portland Thorns - Système de Journal d\'Appels',
        'welcome_title': 'Bienvenue - Pour Commencer',
        'what_app_does': 'Ce Que Fait Cette Application',
        'what_app_does_desc': 'Ce système vous aide à capturer et organiser les informations qualitatives des appels avec les joueurs et agents:',
        'log_calls': 'Enregistrer les Appels: Enregistrez des informations détaillées des conversations avec les joueurs et agents',
        'track_assessments': 'Suivre les Évaluations: Évaluez les joueurs sur la communication, la maturité, la capacité d\'entraînement et plus',
        'generate_reports': 'Générer des Rapports: Téléchargez des résumés PDF et des exportations CSV',
        'view_history': 'Voir l\'Historique: Consultez les appels passés et les résumés des joueurs',
        'player_overviews': 'Aperçus des Joueurs: Consultez des rapports de recrutement détaillés avec graphiques et comparaisons',
        'first_steps': 'Premières Étapes',
        'upload_database': 'Télécharger la Base de Données des Joueurs (si pas déjà fait)',
        'upload_database_desc': 'Utilisez le chargeur dans la barre latérale pour ajouter votre fichier Excel de liste courte. Cela permet la sélection des joueurs et le remplissage automatique.',
        'log_first_call': 'Enregistrer Votre Premier Appel',
        'log_first_call_desc': 'Sélectionnez un joueur de la base de données (ou entrez un joueur personnalisé). Remplissez les détails de l\'appel et les évaluations. Enregistrez pour générer des fichiers PDF et CSV.',
        'explore_features': 'Explorer les Fonctionnalités',
        'explore_features_desc': 'Consultez l\'historique des appels pour voir tous les appels enregistrés. Vérifiez les résumés des joueurs pour des informations agrégées. Téléchargez et consultez les PDFs des aperçus des joueurs.',
        'tips': 'Conseils',
        'save_draft_tip': 'Utilisez "Enregistrer le Brouillon" pour sauvegarder la progression sans soumettre',
        'search_tip': 'Recherchez les joueurs par nom dans le menu déroulant de sélection',
        'download_tip': 'Téléchargez les PDFs et CSVs après chaque appel pour vos dossiers',
        'autopopulate_tip': 'La Conférence et l\'Équipe se remplissent automatiquement lorsque vous sélectionnez un joueur',
        'ready_to_start': 'Prêt à commencer? Fermez cette section et commencez à enregistrer votre premier appel!',
        'got_it': 'Compris! Masquer ce message',
        'quick_start': 'Guide de Démarrage Rapide',
        'how_to_use': 'Comment Utiliser Cette Application',
        'step1': 'Télécharger la Base de Données des Joueurs (Première Fois Seulement)',
        'step1_desc': 'Téléchargez votre fichier Excel de liste courte dans la barre latérale ci-dessus. Le fichier sera sauvegardé en permanence.',
        'step2': 'Enregistrer un Nouvel Appel',
        'step2_desc': 'Sélectionnez Conférence → Équipe → Joueur. Remplissez les détails de l\'appel et les évaluations. Cliquez sur "Enregistrer le Journal d\'Appel" en bas.',
        'step3': 'Télécharger les Résultats',
        'step3_desc': 'Fichiers PDF et CSV disponibles après l\'enregistrement. Consultez l\'historique des appels à tout moment.',
        'step4': 'Voir les Aperçus des Joueurs',
        'step4_desc': 'Téléchargez les aperçus PDF ou consultez les existants. Comparez les joueurs sur toutes les métriques.',
        # Form labels
        'log_new_call': 'Enregistrer un Nouvel Appel',
        'player_not_in_database': 'Joueur non dans la base de données',
        'player_name': 'Nom du Joueur',
        'enter_player_name': 'Entrez le nom du joueur',
        'conference': 'Conférence',
        'team': 'Équipe',
        'position': 'Position',
        'search_player': 'Rechercher un Joueur',
        'call_date': 'Date de l\'Appel',
        'call_type': 'Type d\'Appel',
        'call_number': 'Numéro d\'Appel',
        'duration_minutes': 'Durée (minutes)',
        'participants': 'Participants',
        'list_participants': 'Liste tous les participants à l\'appel',
        'call_notes': 'Notes de l\'Appel',
        'general_notes': 'Notes générales sur l\'appel',
        'agent_assessment': 'Évaluation de l\'Agent',
        'agent_name': 'Nom de l\'Agent',
        'or_enter_new_agent': 'Ou entrez un nouveau nom d\'agent',
        'leave_empty_if_using_dropdown': 'Laissez vide si vous utilisez le menu déroulant ci-dessus',
        'relationship': 'Relation',
        'relationship_other': 'Relation (Autre)',
        'specify_if_other': "Spécifiez si 'Autre' est sélectionné",
        'agent_professionalism': 'Professionnalisme de l\'Agent (1-10)',
        'agent_responsiveness': 'Réactivité de l\'Agent (1-10)',
        'reasonable_expectations': 'Attentes Raisonnables (1-10)',
        'transparency_honesty': 'Transparence/Honnêteté (1-10)',
        'negotiation_style': 'Style de Négociation (1-10)',
        'negotiation_help': '1 = Agressif, 10 = Collaboratif',
        'agent_notes': 'Notes de l\'Agent',
        'player_notes_section': 'Notes du Joueur',
        'player_notes_field': 'Notes du Joueur',
        'general_notes_player': 'Notes générales sur le joueur',
        'personality_self_awareness': 'Personnalité et Conscience de Soi',
        'how_they_carry': 'Comment Ils Se Présentent',
        'how_they_carry_placeholder': 'Décrivez comment le joueur se présente',
        'preparation_level': 'À quel point sont-ils préparés? (1-10)',
        'preparation_help': 'Connaissance de Portland Thorns et volonté de poser des questions',
        'preparation_notes': 'Notes de Préparation',
        'preparation_notes_placeholder': 'Quelles questions ont-ils posées? Que savaient-ils?',
        'how_they_view': 'Comment Ils Se Voient',
        'how_they_view_placeholder': 'Comment le joueur se décrit-il?',
        'what_important': 'Ce Qui Est Important Pour Eux',
        'what_important_placeholder': 'Qu\'est-ce qui compte le plus pour ce joueur?',
        'mindset_growth': 'Mentalité envers la Croissance',
        'mindset_growth_placeholder': 'Comment abordent-ils l\'apprentissage et l\'amélioration?',
        'has_big_injuries': 'A des Blessures Importantes',
        'injury_periods': 'Périodes de Blessure',
        'injury_periods_placeholder': 'Décrivez l\'historique des blessures et les périodes de récupération',
        'personality_traits': 'Traits de Personnalité',
        'other_traits': 'Autres traits (séparés par des virgules)',
        'key_talking_points_section': 'Points Clés de Discussion',
        'interest_level': 'Niveau d\'Intérêt pour Portland',
        'timeline': 'Calendrier',
        'timeline_custom': 'Calendrier (Personnalisé)',
        'enter_custom_timeline': 'Entrez un calendrier personnalisé',
        'salary_expectations': 'Attentes Salariales',
        'if_discussed': 'Si discuté',
        'other_opportunities': 'Autres Opportunités',
        'other_opportunities_placeholder': 'Autres équipes/opportunités mentionnées',
        'key_talking_points': 'Points Clés de Discussion',
        'main_discussion_points': 'Points principaux de discussion',
        'red_flags_concerns': 'Drapeaux Rouges et Préoccupations',
        'severity': 'Gravité',
        'red_flags': 'Drapeaux Rouges / Préoccupations',
        'any_concerns': 'Toute préoccupation ou drapeau rouge',
        'overall_assessment': 'Évaluation Globale',
        'assessment_summary': 'Résumé de l\'Évaluation',
        'total_assessment_score': 'Score Total d\'Évaluation',
        'assessment_percentage': 'Pourcentage d\'Évaluation',
        'grade': 'Note',
        'recommendation': 'Recommandation',
        'summary_notes': 'Notes de Résumé',
        'overall_impression': 'Impression générale et résumé',
        'next_steps': 'Prochaines Étapes',
        'follow_up_needed': 'Suivi Nécessaire',
        'follow_up_date': 'Date de Suivi',
        'action_items': 'Éléments d\'Action',
        'what_needs_happen': 'Que faut-il faire ensuite?',
        'save_call_log': 'Enregistrer le Journal d\'Appel',
        'save_draft': 'Enregistrer le Brouillon',
        'save_progress': 'Enregistrer le Progrès',
    },
    'Portuguese': {
        'title': 'Portland Thorns - Sistema de Registro de Chamadas',
        'welcome_title': 'Bem-vindo - Começando',
        'what_app_does': 'O Que Esta Aplicação Faz',
        'what_app_does_desc': 'Este sistema ajuda você a capturar e organizar informações qualitativas de chamadas com jogadores e agentes:',
        'log_calls': 'Registrar Chamadas: Registre informações detalhadas de conversas com jogadores e agentes',
        'track_assessments': 'Acompanhar Avaliações: Avalie jogadores em comunicação, maturidade, capacidade de treinamento e mais',
        'generate_reports': 'Gerar Relatórios: Baixe resumos PDF e exportações CSV',
        'view_history': 'Ver Histórico: Revise chamadas passadas e resumos de jogadores',
        'player_overviews': 'Visões Gerais dos Jogadores: Veja relatórios de scouting detalhados com gráficos e comparações',
        'first_steps': 'Primeiros Passos',
        'upload_database': 'Carregar Banco de Dados de Jogadores (se ainda não feito)',
        'upload_database_desc': 'Use o carregador na barra lateral para adicionar seu arquivo Excel de lista curta. Isso permite a seleção de jogadores e preenchimento automático.',
        'log_first_call': 'Registrar Sua Primeira Chamada',
        'log_first_call_desc': 'Selecione um jogador do banco de dados (ou insira um jogador personalizado). Preencha os detalhes da chamada e avaliações. Salve para gerar arquivos PDF e CSV.',
        'explore_features': 'Explorar Recursos',
        'explore_features_desc': 'Veja o histórico de chamadas para ver todas as chamadas registradas. Verifique resumos de jogadores para insights agregados. Carregue e visualize PDFs de visões gerais dos jogadores.',
        'tips': 'Dicas',
        'save_draft_tip': 'Use "Salvar Rascunho" para salvar o progresso sem enviar',
        'search_tip': 'Pesquise jogadores por nome no menu suspenso de seleção',
        'download_tip': 'Baixe PDFs e CSVs após cada chamada para seus registros',
        'autopopulate_tip': 'Conferência e Time são preenchidos automaticamente quando você seleciona um jogador',
        'ready_to_start': 'Pronto para começar? Feche esta seção e comece a registrar sua primeira chamada!',
        'got_it': 'Entendi! Ocultar esta mensagem',
        'quick_start': 'Guia de Início Rápido',
        'how_to_use': 'Como Usar Esta Aplicação',
        'step1': 'Carregar Banco de Dados de Jogadores (Apenas Primeira Vez)',
        'step1_desc': 'Carregue seu arquivo Excel de lista curta na barra lateral acima. O arquivo será salvo permanentemente.',
        'step2': 'Registrar uma Nova Chamada',
        'step2_desc': 'Selecione Conferência → Time → Jogador. Preencha os detalhes da chamada e avaliações. Clique em "Salvar Registro de Chamada" na parte inferior.',
        'step3': 'Baixar Resultados',
        'step3_desc': 'Arquivos PDF e CSV disponíveis após salvar. Veja o histórico de chamadas a qualquer momento.',
        'step4': 'Ver Visões Gerais dos Jogadores',
        'step4_desc': 'Carregue visões gerais PDF ou visualize as existentes. Compare jogadores em todas as métricas.',
        # Form labels
        'log_new_call': 'Registrar Nova Chamada',
        'player_not_in_database': 'Jogador não está no banco de dados',
        'player_name': 'Nome do Jogador',
        'enter_player_name': 'Digite o nome do jogador',
        'conference': 'Conferência',
        'team': 'Time',
        'position': 'Posição',
        'search_player': 'Buscar Jogador',
        'call_date': 'Data da Chamada',
        'call_type': 'Tipo de Chamada',
        'call_number': 'Número da Chamada',
        'duration_minutes': 'Duração (minutos)',
        'participants': 'Participantes',
        'list_participants': 'Liste todos os participantes na chamada',
        'call_notes': 'Notas da Chamada',
        'general_notes': 'Notas gerais sobre a chamada',
        'agent_assessment': 'Avaliação do Agente',
        'agent_name': 'Nome do Agente',
        'or_enter_new_agent': 'Ou digite um novo nome de agente',
        'leave_empty_if_using_dropdown': 'Deixe vazio se estiver usando o menu suspenso acima',
        'relationship': 'Relacionamento',
        'relationship_other': 'Relacionamento (Outro)',
        'specify_if_other': "Especifique se 'Outro' foi selecionado",
        'agent_professionalism': 'Profissionalismo do Agente (1-10)',
        'agent_responsiveness': 'Capacidade de Resposta do Agente (1-10)',
        'reasonable_expectations': 'Expectativas Razoáveis (1-10)',
        'transparency_honesty': 'Transparência/Honestidade (1-10)',
        'negotiation_style': 'Estilo de Negociação (1-10)',
        'negotiation_help': '1 = Agressivo, 10 = Colaborativo',
        'agent_notes': 'Notas do Agente',
        'player_notes_section': 'Notas do Jogador',
        'player_notes_field': 'Notas do Jogador',
        'general_notes_player': 'Notas gerais sobre o jogador',
        'personality_self_awareness': 'Personalidade e Autoconsciência',
        'how_they_carry': 'Como Eles Se Apresentam',
        'how_they_carry_placeholder': 'Descreva como o jogador se apresenta',
        'preparation_level': 'Quão preparados estão? (1-10)',
        'preparation_help': 'Conhecimento do Portland Thorns e prontidão para fazer perguntas',
        'preparation_notes': 'Notas de Preparação',
        'preparation_notes_placeholder': 'Quais perguntas fizeram? O que sabiam?',
        'how_they_view': 'Como Eles Se Veem',
        'how_they_view_placeholder': 'Como o jogador se descreve?',
        'what_important': 'O Que É Importante Para Eles',
        'what_important_placeholder': 'O que é mais importante para este jogador?',
        'mindset_growth': 'Mentalidade em Relação ao Crescimento',
        'mindset_growth_placeholder': 'Como eles abordam o aprendizado e a melhoria?',
        'has_big_injuries': 'Tem Lesões Importantes',
        'injury_periods': 'Períodos de Lesão',
        'injury_periods_placeholder': 'Descreva o histórico de lesões e períodos de recuperação',
        'personality_traits': 'Traços de Personalidade',
        'other_traits': 'Outros traços (separados por vírgulas)',
        'key_talking_points_section': 'Pontos Principais da Conversa',
        'interest_level': 'Nível de Interesse em Portland',
        'timeline': 'Cronograma',
        'timeline_custom': 'Cronograma (Personalizado)',
        'enter_custom_timeline': 'Digite cronograma personalizado',
        'salary_expectations': 'Expectativas Salariais',
        'if_discussed': 'Se discutido',
        'other_opportunities': 'Outras Oportunidades',
        'other_opportunities_placeholder': 'Outros times/oportunidades mencionadas',
        'key_talking_points': 'Pontos Principais da Conversa',
        'main_discussion_points': 'Pontos principais de discussão',
        'red_flags_concerns': 'Bandeiras Vermelhas e Preocupações',
        'severity': 'Severidade',
        'red_flags': 'Bandeiras Vermelhas / Preocupações',
        'any_concerns': 'Qualquer preocupação ou bandeira vermelha',
        'overall_assessment': 'Avaliação Geral',
        'assessment_summary': 'Resumo da Avaliação',
        'total_assessment_score': 'Pontuação Total da Avaliação',
        'assessment_percentage': 'Porcentagem da Avaliação',
        'grade': 'Nota',
        'recommendation': 'Recomendação',
        'summary_notes': 'Notas Resumo',
        'overall_impression': 'Impressão geral e resumo',
        'next_steps': 'Próximos Passos',
        'follow_up_needed': 'Acompanhamento Necessário',
        'follow_up_date': 'Data de Acompanhamento',
        'action_items': 'Itens de Ação',
        'what_needs_happen': 'O que precisa acontecer a seguir?',
        'save_call_log': 'Salvar Registro de Chamada',
        'save_draft': 'Salvar Rascunho',
        'save_progress': 'Salvar Progresso',
    },
    'German': {
        'title': 'Portland Thorns - Anrufprotokoll-System',
        'welcome_title': 'Willkommen - Erste Schritte',
        'what_app_does': 'Was Diese App Macht',
        'what_app_does_desc': 'Dieses System hilft Ihnen, qualitative Informationen aus Gesprächen mit Spielern und Agenten zu erfassen und zu organisieren:',
        'log_calls': 'Anrufe Protokollieren: Erfassen Sie detaillierte Informationen aus Gesprächen mit Spielern und Agenten',
        'track_assessments': 'Bewertungen Verfolgen: Bewerten Sie Spieler in Kommunikation, Reife, Trainierbarkeit und mehr',
        'generate_reports': 'Berichte Generieren: Laden Sie PDF-Zusammenfassungen und CSV-Exporte herunter',
        'view_history': 'Verlauf Anzeigen: Überprüfen Sie vergangene Anrufe und Spielerzusammenfassungen',
        'player_overviews': 'Spieler-Übersichten: Sehen Sie detaillierte Scouting-Berichte mit Diagrammen und Vergleichen',
        'first_steps': 'Erste Schritte',
        'upload_database': 'Spielerdatenbank Hochladen (falls noch nicht geschehen)',
        'upload_database_desc': 'Verwenden Sie den Uploader in der Seitenleiste, um Ihre Excel-Shortlist-Datei hinzuzufügen. Dies ermöglicht die Spielerauswahl und automatisches Ausfüllen.',
        'log_first_call': 'Ihren Ersten Anruf Protokollieren',
        'log_first_call_desc': 'Wählen Sie einen Spieler aus der Datenbank (oder geben Sie einen benutzerdefinierten Spieler ein). Füllen Sie die Anrufdetails und Bewertungen aus. Speichern Sie, um PDF- und CSV-Dateien zu generieren.',
        'explore_features': 'Funktionen Erkunden',
        'explore_features_desc': 'Sehen Sie den Anrufverlauf, um alle protokollierten Anrufe zu sehen. Überprüfen Sie Spielerzusammenfassungen für aggregierte Erkenntnisse. Laden Sie Spieler-Übersichts-PDFs hoch und anzeigen.',
        'tips': 'Tipps',
        'save_draft_tip': 'Verwenden Sie "Entwurf Speichern", um den Fortschritt ohne Übermittlung zu speichern',
        'search_tip': 'Suchen Sie Spieler nach Namen im Spielerauswahl-Dropdown',
        'download_tip': 'Laden Sie PDFs und CSVs nach jedem Anruf für Ihre Aufzeichnungen herunter',
        'autopopulate_tip': 'Konferenz und Team werden automatisch ausgefüllt, wenn Sie einen Spieler auswählen',
        'ready_to_start': 'Bereit zum Starten? Schließen Sie diesen Abschnitt und beginnen Sie mit der Protokollierung Ihres ersten Anrufs!',
        'got_it': 'Verstanden! Diese Nachricht ausblenden',
        'quick_start': 'Schnellstart-Anleitung',
        'how_to_use': 'Wie Man Diese App Verwendet',
        'step1': 'Spielerdatenbank Hochladen (Nur Beim Ersten Mal)',
        'step1_desc': 'Laden Sie Ihre Excel-Shortlist-Datei in der Seitenleiste oben hoch. Die Datei wird dauerhaft gespeichert.',
        'step2': 'Einen Neuen Anruf Protokollieren',
        'step2_desc': 'Wählen Sie Konferenz → Team → Spieler. Füllen Sie die Anrufdetails und Bewertungen aus. Klicken Sie unten auf "Anrufprotokoll Speichern".',
        'step3': 'Ergebnisse Herunterladen',
        'step3_desc': 'PDF- und CSV-Dateien stehen nach dem Speichern zur Verfügung. Sehen Sie den Anrufverlauf jederzeit ein.',
        'step4': 'Spieler-Übersichten Anzeigen',
        'step4_desc': 'Laden Sie PDF-Übersichten hoch oder zeigen Sie vorhandene an. Vergleichen Sie Spieler über alle Metriken.',
        # Form labels
        'log_new_call': 'Neuen Anruf Protokollieren',
        'player_not_in_database': 'Spieler nicht in der Datenbank',
        'player_name': 'Spielername',
        'enter_player_name': 'Spielernamen eingeben',
        'conference': 'Konferenz',
        'team': 'Team',
        'position': 'Position',
        'search_player': 'Spieler Suchen',
        'call_date': 'Anrufdatum',
        'call_type': 'Anruftyp',
        'call_number': 'Anrufnummer',
        'duration_minutes': 'Dauer (Minuten)',
        'participants': 'Teilnehmer',
        'list_participants': 'Liste aller Teilnehmer am Anruf',
        'call_notes': 'Anrufnotizen',
        'general_notes': 'Allgemeine Notizen zum Anruf',
        'agent_assessment': 'Agentenbewertung',
        'agent_name': 'Agentenname',
        'or_enter_new_agent': 'Oder neuen Agentennamen eingeben',
        'leave_empty_if_using_dropdown': 'Leer lassen, wenn Sie das Dropdown-Menü oben verwenden',
        'relationship': 'Beziehung',
        'relationship_other': 'Beziehung (Andere)',
        'specify_if_other': "Angeben, wenn 'Andere' ausgewählt wurde",
        'agent_professionalism': 'Agentenprofessionalität (1-10)',
        'agent_responsiveness': 'Agentenreaktionsfähigkeit (1-10)',
        'reasonable_expectations': 'Angemessene Erwartungen (1-10)',
        'transparency_honesty': 'Transparenz/Ehrlichkeit (1-10)',
        'negotiation_style': 'Verhandlungsstil (1-10)',
        'negotiation_help': '1 = Aggressiv, 10 = Kollaborativ',
        'agent_notes': 'Agentennotizen',
        'player_notes_section': 'Spielernotizen',
        'player_notes_field': 'Spielernotizen',
        'general_notes_player': 'Allgemeine Notizen zum Spieler',
        'personality_self_awareness': 'Persönlichkeit und Selbstbewusstsein',
        'how_they_carry': 'Wie Sie Sich Präsentieren',
        'how_they_carry_placeholder': 'Beschreiben Sie, wie sich der Spieler präsentiert',
        'preparation_level': 'Wie gut sind sie vorbereitet? (1-10)',
        'preparation_help': 'Kenntnis von Portland Thorns und Bereitschaft, Fragen zu stellen',
        'preparation_notes': 'Vorbereitungsnotizen',
        'preparation_notes_placeholder': 'Welche Fragen haben sie gestellt? Was wussten sie?',
        'how_they_view': 'Wie Sie Sich Sehen',
        'how_they_view_placeholder': 'Wie beschreibt sich der Spieler?',
        'what_important': 'Was Ist Wichtig Für Sie',
        'what_important_placeholder': 'Was ist für diesen Spieler am wichtigsten?',
        'mindset_growth': 'Einstellung zum Wachstum',
        'mindset_growth_placeholder': 'Wie gehen sie an Lernen und Verbesserung heran?',
        'has_big_injuries': 'Hat Große Verletzungen',
        'injury_periods': 'Verletzungsperioden',
        'injury_periods_placeholder': 'Beschreiben Sie die Verletzungshistorie und Erholungsperioden',
        'personality_traits': 'Persönlichkeitsmerkmale',
        'other_traits': 'Andere Merkmale (durch Kommas getrennt)',
        'key_talking_points_section': 'Wichtige Gesprächspunkte',
        'interest_level': 'Interessensniveau an Portland',
        'timeline': 'Zeitplan',
        'timeline_custom': 'Zeitplan (Benutzerdefiniert)',
        'enter_custom_timeline': 'Benutzerdefinierten Zeitplan eingeben',
        'salary_expectations': 'Gehaltserwartungen',
        'if_discussed': 'Falls besprochen',
        'other_opportunities': 'Andere Möglichkeiten',
        'other_opportunities_placeholder': 'Andere Teams/Möglichkeiten erwähnt',
        'key_talking_points': 'Wichtige Gesprächspunkte',
        'main_discussion_points': 'Hauptdiskussionspunkte',
        'red_flags_concerns': 'Rote Flaggen und Bedenken',
        'severity': 'Schweregrad',
        'red_flags': 'Rote Flaggen / Bedenken',
        'any_concerns': 'Irgendwelche Bedenken oder rote Flaggen',
        'overall_assessment': 'Gesamtbewertung',
        'assessment_summary': 'Bewertungszusammenfassung',
        'total_assessment_score': 'Gesamtbewertungspunktzahl',
        'assessment_percentage': 'Bewertungsprozentsatz',
        'grade': 'Note',
        'recommendation': 'Empfehlung',
        'summary_notes': 'Zusammenfassungsnotizen',
        'overall_impression': 'Gesamteindruck und Zusammenfassung',
        'next_steps': 'Nächste Schritte',
        'follow_up_needed': 'Nachfassung Erforderlich',
        'follow_up_date': 'Nachfassdatum',
        'action_items': 'Aktionspunkte',
        'what_needs_happen': 'Was muss als Nächstes passieren?',
        'save_call_log': 'Anrufprotokoll Speichern',
        'save_draft': 'Entwurf Speichern',
        'save_progress': 'Fortschritt Speichern',
    },
    'Italian': {
        'title': 'Portland Thorns - Sistema di Registro Chiamate',
        'welcome_title': 'Benvenuto - Iniziare',
        'what_app_does': 'Cosa Fa Questa Applicazione',
        'what_app_does_desc': 'Questo sistema ti aiuta a catturare e organizzare informazioni qualitative dalle chiamate con giocatori e agenti:',
        'log_calls': 'Registrare Chiamate: Registra informazioni dettagliate dalle conversazioni con giocatori e agenti',
        'track_assessments': 'Tracciare Valutazioni: Valuta i giocatori su comunicazione, maturità, allenabilità e altro',
        'generate_reports': 'Generare Report: Scarica riassunti PDF ed esportazioni CSV',
        'view_history': 'Visualizzare Cronologia: Rivedi chiamate passate e riassunti dei giocatori',
        'player_overviews': 'Panoramiche Giocatori: Visualizza report di scouting dettagliati con grafici e confronti',
        'first_steps': 'Primi Passi',
        'upload_database': 'Caricare Database Giocatori (se non già fatto)',
        'upload_database_desc': 'Usa il caricatore nella barra laterale per aggiungere il tuo file Excel della lista corta. Questo abilita la selezione dei giocatori e il completamento automatico.',
        'log_first_call': 'Registrare la Tua Prima Chiamata',
        'log_first_call_desc': 'Seleziona un giocatore dal database (o inserisci un giocatore personalizzato). Compila i dettagli della chiamata e le valutazioni. Salva per generare file PDF e CSV.',
        'explore_features': 'Esplorare Funzionalità',
        'explore_features_desc': 'Visualizza la cronologia delle chiamate per vedere tutte le chiamate registrate. Controlla i riassunti dei giocatori per informazioni aggregate. Carica e visualizza PDF delle panoramiche dei giocatori.',
        'tips': 'Suggerimenti',
        'save_draft_tip': 'Usa "Salva Bozza" per salvare il progresso senza inviare',
        'search_tip': 'Cerca giocatori per nome nel menu a discesa di selezione',
        'download_tip': 'Scarica PDF e CSV dopo ogni chiamata per i tuoi registri',
        'autopopulate_tip': 'Conferenza e Squadra si compilano automaticamente quando selezioni un giocatore',
        'ready_to_start': 'Pronto per iniziare? Chiudi questa sezione e inizia a registrare la tua prima chiamata!',
        'got_it': 'Capito! Nascondi questo messaggio',
        'quick_start': 'Guida di Avvio Rapido',
        'how_to_use': 'Come Usare Questa Applicazione',
        'step1': 'Caricare Database Giocatori (Solo Prima Volta)',
        'step1_desc': 'Carica il tuo file Excel della lista corta nella barra laterale sopra. Il file verrà salvato permanentemente.',
        'step2': 'Registrare una Nuova Chiamata',
        'step2_desc': 'Seleziona Conferenza → Squadra → Giocatore. Compila i dettagli della chiamata e le valutazioni. Clicca "Salva Registro Chiamata" in fondo.',
        'step3': 'Scaricare Risultati',
        'step3_desc': 'File PDF e CSV disponibili dopo il salvataggio. Visualizza la cronologia delle chiamate in qualsiasi momento.',
        'step4': 'Visualizzare Panoramiche Giocatori',
        'step4_desc': 'Carica panoramiche PDF o visualizza quelle esistenti. Confronta i giocatori su tutte le metriche.',
        # Form labels
        'log_new_call': 'Registrare Nuova Chiamata',
        'player_not_in_database': 'Giocatore non nel database',
        'player_name': 'Nome del Giocatore',
        'enter_player_name': 'Inserisci il nome del giocatore',
        'conference': 'Conferenza',
        'team': 'Squadra',
        'position': 'Posizione',
        'search_player': 'Cerca Giocatore',
        'call_date': 'Data della Chiamata',
        'call_type': 'Tipo di Chiamata',
        'call_number': 'Numero di Chiamata',
        'duration_minutes': 'Durata (minuti)',
        'participants': 'Partecipanti',
        'list_participants': 'Elenca tutti i partecipanti alla chiamata',
        'call_notes': 'Note della Chiamata',
        'general_notes': 'Note generali sulla chiamata',
        'agent_assessment': 'Valutazione dell\'Agente',
        'agent_name': 'Nome dell\'Agente',
        'or_enter_new_agent': 'O inserisci un nuovo nome di agente',
        'leave_empty_if_using_dropdown': 'Lascia vuoto se usi il menu a discesa sopra',
        'relationship': 'Relazione',
        'relationship_other': 'Relazione (Altro)',
        'specify_if_other': "Specifica se 'Altro' è stato selezionato",
        'agent_professionalism': 'Professionalità dell\'Agente (1-10)',
        'agent_responsiveness': 'Reattività dell\'Agente (1-10)',
        'reasonable_expectations': 'Aspettative Ragionevoli (1-10)',
        'transparency_honesty': 'Trasparenza/Onestà (1-10)',
        'negotiation_style': 'Stile di Negoziazione (1-10)',
        'negotiation_help': '1 = Aggressivo, 10 = Collaborativo',
        'agent_notes': 'Note dell\'Agente',
        'player_notes_section': 'Note del Giocatore',
        'player_notes_field': 'Note del Giocatore',
        'general_notes_player': 'Note generali sul giocatore',
        'personality_self_awareness': 'Personalità e Autoconsapevolezza',
        'how_they_carry': 'Come Si Presentano',
        'how_they_carry_placeholder': 'Descrivi come si presenta il giocatore',
        'preparation_level': 'Quanto sono preparati? (1-10)',
        'preparation_help': 'Conoscenza di Portland Thorns e prontezza a fare domande',
        'preparation_notes': 'Note di Preparazione',
        'preparation_notes_placeholder': 'Che domande hanno fatto? Cosa sapevano?',
        'how_they_view': 'Come Si Vedono',
        'how_they_view_placeholder': 'Come si descrive il giocatore?',
        'what_important': 'Cosa È Importante Per Loro',
        'what_important_placeholder': 'Cosa conta di più per questo giocatore?',
        'mindset_growth': 'Mentalità Verso la Crescita',
        'mindset_growth_placeholder': 'Come affrontano l\'apprendimento e il miglioramento?',
        'has_big_injuries': 'Ha Lesioni Importanti',
        'injury_periods': 'Periodi di Lesione',
        'injury_periods_placeholder': 'Descrivi la storia delle lesioni e i periodi di recupero',
        'personality_traits': 'Tratti di Personalità',
        'other_traits': 'Altri tratti (separati da virgole)',
        'key_talking_points_section': 'Punti Chiave della Conversazione',
        'interest_level': 'Livello di Interesse in Portland',
        'timeline': 'Cronologia',
        'timeline_custom': 'Cronologia (Personalizzata)',
        'enter_custom_timeline': 'Inserisci cronologia personalizzata',
        'salary_expectations': 'Aspettative Salariali',
        'if_discussed': 'Se discusso',
        'other_opportunities': 'Altre Opportunità',
        'other_opportunities_placeholder': 'Altri team/opportunità menzionate',
        'key_talking_points': 'Punti Chiave della Conversazione',
        'main_discussion_points': 'Punti principali di discussione',
        'red_flags_concerns': 'Bandiere Rosse e Preoccupazioni',
        'severity': 'Gravità',
        'red_flags': 'Bandiere Rosse / Preoccupazioni',
        'any_concerns': 'Qualsiasi preoccupazione o bandiera rossa',
        'overall_assessment': 'Valutazione Complessiva',
        'assessment_summary': 'Riepilogo della Valutazione',
        'total_assessment_score': 'Punteggio Totale della Valutazione',
        'assessment_percentage': 'Percentuale della Valutazione',
        'grade': 'Voto',
        'recommendation': 'Raccomandazione',
        'summary_notes': 'Note di Riepilogo',
        'overall_impression': 'Impressione generale e riepilogo',
        'next_steps': 'Prossimi Passi',
        'follow_up_needed': 'Follow-up Necessario',
        'follow_up_date': 'Data di Follow-up',
        'action_items': 'Elementi di Azione',
        'what_needs_happen': 'Cosa deve succedere dopo?',
        'save_call_log': 'Salva Registro Chiamata',
        'save_draft': 'Salva Bozza',
        'save_progress': 'Salva Progresso',
    },
    'Arabic': {
        'title': 'بورتلاند ثورنز - نظام سجل المكالمات',
        'welcome_title': 'مرحباً - البدء',
        'what_app_does': 'ماذا تفعل هذه التطبيق',
        'what_app_does_desc': 'يساعدك هذا النظام على التقاط وتنظيم المعلومات النوعية من المكالمات مع اللاعبين والوكلاء:',
        'log_calls': 'تسجيل المكالمات: سجل معلومات مفصلة من المحادثات مع اللاعبين والوكلاء',
        'track_assessments': 'تتبع التقييمات: قيّم اللاعبين في التواصل والنضج والقابلية للتدريب والمزيد',
        'generate_reports': 'إنشاء التقارير: قم بتنزيل ملخصات PDF وصادرات CSV',
        'view_history': 'عرض السجل: راجع المكالمات السابقة وملخصات اللاعبين',
        'player_overviews': 'نظرة عامة على اللاعبين: عرض تقارير الاستكشاف التفصيلية مع الرسوم البيانية والمقارنات',
        'first_steps': 'الخطوات الأولى',
        'upload_database': 'تحميل قاعدة بيانات اللاعبين (إن لم يتم ذلك بالفعل)',
        'upload_database_desc': 'استخدم أداة التحميل في الشريط الجانبي لإضافة ملف Excel لقائمة المرشحين. يتيح هذا اختيار اللاعبين والتعبئة التلقائية.',
        'log_first_call': 'تسجيل أول مكالمة لك',
        'log_first_call_desc': 'اختر لاعباً من قاعدة البيانات (أو أدخل لاعباً مخصصاً). املأ تفاصيل المكالمة والتقييمات. احفظ لإنشاء ملفات PDF و CSV.',
        'explore_features': 'استكشاف الميزات',
        'explore_features_desc': 'عرض سجل المكالمات لرؤية جميع المكالمات المسجلة. تحقق من ملخصات اللاعبين للحصول على رؤى مجمعة. قم بتحميل وعرض ملفات PDF لنظرة عامة على اللاعبين.',
        'tips': 'نصائح',
        'save_draft_tip': 'استخدم "حفظ المسودة" لحفظ التقدم دون إرسال',
        'search_tip': 'ابحث عن اللاعبين بالاسم في القائمة المنسدلة للاختيار',
        'download_tip': 'قم بتنزيل ملفات PDF و CSV بعد كل مكالمة لسجلاتك',
        'autopopulate_tip': 'يتم ملء المؤتمر والفريق تلقائياً عند اختيار لاعب',
        'ready_to_start': 'جاهز للبدء؟ أغلق هذا القسم وابدأ في تسجيل أول مكالمة لك!',
        'got_it': 'فهمت! إخفاء هذه الرسالة',
        'quick_start': 'دليل البدء السريع',
        'how_to_use': 'كيفية استخدام هذا التطبيق',
        'step1': 'تحميل قاعدة بيانات اللاعبين (للمرة الأولى فقط)',
        'step1_desc': 'قم بتحميل ملف Excel لقائمة المرشحين في الشريط الجانبي أعلاه. سيتم حفظ الملف بشكل دائم.',
        'step2': 'تسجيل مكالمة جديدة',
        'step2_desc': 'اختر المؤتمر → الفريق → اللاعب. املأ تفاصيل المكالمة والتقييمات. انقر على "حفظ سجل المكالمة" في الأسفل.',
        'step3': 'تنزيل النتائج',
        'step3_desc': 'ملفات PDF و CSV متاحة بعد الحفظ. عرض سجل المكالمات في أي وقت.',
        'step4': 'عرض نظرة عامة على اللاعبين',
        'step4_desc': 'قم بتحميل نظرة عامة PDF أو عرض الموجودة. قارن اللاعبين عبر جميع المقاييس.',
        # Form labels
        'log_new_call': 'تسجيل مكالمة جديدة',
        'player_not_in_database': 'اللاعب غير موجود في قاعدة البيانات',
        'player_name': 'اسم اللاعب',
        'enter_player_name': 'أدخل اسم اللاعب',
        'conference': 'المؤتمر',
        'team': 'الفريق',
        'position': 'المركز',
        'search_player': 'البحث عن لاعب',
        'call_date': 'تاريخ المكالمة',
        'call_type': 'نوع المكالمة',
        'call_number': 'رقم المكالمة',
        'duration_minutes': 'المدة (بالدقائق)',
        'participants': 'المشاركون',
        'list_participants': 'قائمة جميع المشاركين في المكالمة',
        'call_notes': 'ملاحظات المكالمة',
        'general_notes': 'ملاحظات عامة حول المكالمة',
        'agent_assessment': 'تقييم الوكيل',
        'agent_name': 'اسم الوكيل',
        'or_enter_new_agent': 'أو أدخل اسم وكيل جديد',
        'leave_empty_if_using_dropdown': 'اتركه فارغاً إذا كنت تستخدم القائمة المنسدلة أعلاه',
        'relationship': 'العلاقة',
        'relationship_other': 'العلاقة (أخرى)',
        'specify_if_other': "حدد إذا تم اختيار 'أخرى'",
        'agent_professionalism': 'احترافية الوكيل (1-10)',
        'agent_responsiveness': 'استجابة الوكيل (1-10)',
        'reasonable_expectations': 'توقعات معقولة (1-10)',
        'transparency_honesty': 'الشفافية/الصدق (1-10)',
        'negotiation_style': 'أسلوب التفاوض (1-10)',
        'negotiation_help': '1 = عدواني، 10 = تعاوني',
        'agent_notes': 'ملاحظات الوكيل',
        'player_notes_section': 'ملاحظات اللاعب',
        'player_notes_field': 'ملاحظات اللاعب',
        'general_notes_player': 'ملاحظات عامة حول اللاعب',
        'personality_self_awareness': 'الشخصية والوعي الذاتي',
        'how_they_carry': 'كيف يقدمون أنفسهم',
        'how_they_carry_placeholder': 'صف كيف يقدم اللاعب نفسه',
        'preparation_level': 'ما مدى استعدادهم؟ (1-10)',
        'preparation_help': 'معرفة بورتلاند ثورنز والاستعداد لطرح الأسئلة',
        'preparation_notes': 'ملاحظات التحضير',
        'preparation_notes_placeholder': 'ما الأسئلة التي طرحوها؟ ماذا عرفوا؟',
        'how_they_view': 'كيف ينظرون لأنفسهم',
        'how_they_view_placeholder': 'كيف يصف اللاعب نفسه؟',
        'what_important': 'ما هو المهم بالنسبة لهم',
        'what_important_placeholder': 'ما هو الأهم لهذا اللاعب؟',
        'mindset_growth': 'عقلية تجاه النمو',
        'mindset_growth_placeholder': 'كيف يتعاملون مع التعلم والتحسين؟',
        'has_big_injuries': 'لديه إصابات كبيرة',
        'injury_periods': 'فترات الإصابة',
        'injury_periods_placeholder': 'وصف تاريخ الإصابات وفترات التعافي',
        'personality_traits': 'سمات الشخصية',
        'other_traits': 'سمات أخرى (مفصولة بفواصل)',
        'key_talking_points_section': 'نقاط الحديث الرئيسية',
        'interest_level': 'مستوى الاهتمام ببورتلاند',
        'timeline': 'الجدول الزمني',
        'timeline_custom': 'الجدول الزمني (مخصص)',
        'enter_custom_timeline': 'أدخل جدولاً زمنياً مخصصاً',
        'salary_expectations': 'توقعات الراتب',
        'if_discussed': 'إذا تمت مناقشته',
        'other_opportunities': 'فرص أخرى',
        'other_opportunities_placeholder': 'فرق/فرص أخرى تم ذكرها',
        'key_talking_points': 'نقاط الحديث الرئيسية',
        'main_discussion_points': 'نقاط النقاش الرئيسية',
        'red_flags_concerns': 'علامات حمراء ومخاوف',
        'severity': 'الشدة',
        'red_flags': 'علامات حمراء / مخاوف',
        'any_concerns': 'أي مخاوف أو علامات حمراء',
        'overall_assessment': 'التقييم الشامل',
        'assessment_summary': 'ملخص التقييم',
        'total_assessment_score': 'إجمالي نقاط التقييم',
        'assessment_percentage': 'نسبة التقييم',
        'grade': 'الدرجة',
        'recommendation': 'التوصية',
        'summary_notes': 'ملاحظات الملخص',
        'overall_impression': 'الانطباع العام والملخص',
        'next_steps': 'الخطوات التالية',
        'follow_up_needed': 'متابعة مطلوبة',
        'follow_up_date': 'تاريخ المتابعة',
        'action_items': 'عناصر العمل',
        'what_needs_happen': 'ما الذي يحتاج أن يحدث بعد ذلك؟',
        'save_call_log': 'حفظ سجل المكالمة',
        'save_draft': 'حفظ المسودة',
        'save_progress': 'حفظ التقدم',
    },
}

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state.language = 'English'

def t(key):
    """Get translation for current language."""
    return TRANSLATIONS.get(st.session_state.language, TRANSLATIONS['English']).get(key, key)

# Data storage - use relative paths for Streamlit Cloud compatibility
# On Streamlit Cloud, the app runs from the repo root
# For local development, detect the base directory from script location
_script_dir = Path(__file__).parent
# Script is in Scripts/00_Keep/, so go up 2 levels to get to Advanced Search directory
# Scripts/00_Keep -> Scripts -> Advanced Search
_local_base = _script_dir.parent.parent
if _local_base.exists() and list(_local_base.glob('Portland Thorns*.xlsx')):
    # Local development - use detected path (check for any Portland Thorns Excel file)
    BASE_DIR = _local_base
else:
    # Fallback: try absolute path
    _abs_base = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search")
    if _abs_base.exists() and (_abs_base / 'Qualitative_Data' / 'call_log.csv').exists():
        BASE_DIR = _abs_base
    else:
        # Streamlit Cloud or other environment - use current directory
        BASE_DIR = Path('.')

DATA_DIR = BASE_DIR / 'Qualitative_Data'
# Create directory and parents if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CALL_LOG_FILE = DATA_DIR / 'call_log.csv'
AGENT_DB_FILE = DATA_DIR / 'agents.csv'
DRAFT_FILE = DATA_DIR / 'call_log_draft.json'
PRESETS_FILE = DATA_DIR / 'column_visibility_presets.json'

# Try multiple possible shortlist file names
POSSIBLE_SHORTLIST_FILES = [
    BASE_DIR / 'Portland Thorns 2025 Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Long Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Short Shortlist.xlsx',
    BASE_DIR / 'AI Shortlist.xlsx',
]

# Find the first existing shortlist file
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

# If no uploaded file, check local files
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
                                    
                                    # Normalize conference names (handle variations like BIG10, IVY, etc.)
                                    if conference and pd.notna(conference):
                                        conference_str = str(conference).upper().strip()
                                        # Map common variations to standard names
                                        conference_map = {
                                            'BIG10': 'Big Ten',
                                            'BIG 10': 'Big Ten',
                                            'B1G': 'Big Ten',
                                            'BIG12': 'Big 12',
                                            'BIG 12': 'Big 12',
                                            'IVY': 'Ivy League',
                                            'IVY LEAGUE': 'Ivy League',
                                            'ACC': 'ACC',
                                            'SEC': 'SEC',
                                            'BIG TEN': 'Big Ten',
                                            'BIG TWELVE': 'Big 12',
                                        }
                                        conference = conference_map.get(conference_str, conference_str)
                                    
                                    # If conference not in columns or still empty, try to extract from team name
                                    if not conference or pd.isna(conference) or conference == '':
                                        team_str = str(team).upper()
                                        
                                        # ACC teams
                                        acc_teams = ['DUKE', 'NORTH CAROLINA', 'VIRGINIA', 'CLEMSON', 'FLORIDA STATE', 'VIRGINIA TECH', 'SYRACUSE', 'LOUISVILLE', 'PITTSBURGH', 'BOSTON COLLEGE', 'NC STATE', 'WAKE FOREST', 'MIAMI', 'NOTRE DAME']
                                        # SEC teams
                                        sec_teams = ['ALABAMA', 'GEORGIA', 'FLORIDA', 'LSU', 'TENNESSEE', 'ARKANSAS', 'SOUTH CAROLINA', 'MISSISSIPPI', 'MISSISSIPPI STATE', 'AUBURN', 'KENTUCKY', 'VANDERBILT', 'MISSOURI', 'TEXAS A&M']
                                        # Big Ten teams
                                        big10_teams = ['MICHIGAN', 'OHIO STATE', 'PENN STATE', 'MICHIGAN STATE', 'WISCONSIN', 'IOWA', 'NEBRASKA', 'MINNESOTA', 'INDIANA', 'PURDUE', 'ILLINOIS', 'NORTHWESTERN', 'MARYLAND', 'RUTGERS', 'USC', 'UCLA']
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
            df = pd.read_csv(CALL_LOG_FILE)
            # Ensure we return a DataFrame even if empty
            if df.empty:
                return pd.DataFrame()
            return df
        except Exception as e:
            # Don't show error in UI during normal operation, just return empty
            import traceback
            print(f"Error loading call log: {e}")
            print(traceback.format_exc())
            return pd.DataFrame()
    else:
        # Debug: print path if file doesn't exist
        print(f"Call log file not found at: {CALL_LOG_FILE}")
        print(f"BASE_DIR: {BASE_DIR}")
        print(f"DATA_DIR: {DATA_DIR}")
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

def save_column_presets(presets_dict):
    """Save column visibility presets to JSON file."""
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump(presets_dict, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving presets: {e}")
        return False

def load_column_presets():
    """Load column visibility presets from JSON file."""
    try:
        if PRESETS_FILE.exists():
            with open(PRESETS_FILE, 'r') as f:
                presets_dict = json.load(f)
            return presets_dict
        return {}
    except Exception as e:
        return {}

def reset_form():
    """Reset all form fields without logging out."""
    # Clear all form-related session state variables
    form_keys = [
        'form1_call_date', 'form1_call_type', 'form1_duration', 'form1_team',
        'form1_conference', 'form1_conference_other', 'form1_position_profile',
        'form1_participants', 'form1_call_notes', 'form1_agent_name',
        'form1_agent_selected', 'form1_agent_custom', 'form1_relationship',
        'form1_relationship_other', 'form1_agent_professionalism',
        'form1_agent_responsiveness', 'form1_agent_expectations',
        'form1_agent_transparency', 'form1_agent_negotiation_style',
        'form1_agent_notes', 'form2_player_notes',
        'form2_how_they_carry_themselves', 'form2_preparation_level',
        'form2_preparation_notes', 'form2_how_they_view_themselves',
        'form2_what_is_important_to_them', 'form2_mindset_towards_growth',
        'form2_has_big_injuries', 'form2_injury_periods',
        'form2_personality_traits', 'form2_other_traits',
        'form2_interest_level', 'form2_timeline', 'form2_timeline_selected',
        'form2_timeline_custom', 'form2_salary_expectations',
        'form2_other_opportunities', 'form2_key_talking_points',
        'form2_red_flags', 'form2_red_flag_severity',
        'communication', 'maturity', 'coachability', 'leadership',
        'work_ethic', 'confidence', 'tactical_knowledge', 'team_fit',
        'overall_rating', 'form2_recommendation', 'form2_summary_notes',
        'follow_up_needed', 'follow_up_date', 'action_items',
        'filter_conference', 'filter_team', 'player_search',
        'selected_player_team', 'selected_player_conference',
        'selected_player_position'
    ]
    
    for key in form_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear draft file
    clear_draft()
    
    # Clear form history for undo
    if 'form_history' in st.session_state:
        st.session_state.form_history = []
    if 'form_history_index' in st.session_state:
        st.session_state.form_history_index = -1

def save_form_state_to_history():
    """Save current form state to history for undo functionality."""
    if 'form_history' not in st.session_state:
        st.session_state.form_history = []
    if 'form_history_index' not in st.session_state:
        st.session_state.form_history_index = -1
    
    # Get current form state
    current_state = {}
    form_keys = [
        'form1_call_date', 'form1_call_type', 'form1_duration', 'form1_team',
        'form1_conference', 'form1_conference_other', 'form1_position_profile',
        'form1_participants', 'form1_call_notes', 'form1_agent_name',
        'form1_agent_selected', 'form1_agent_custom', 'form1_relationship',
        'form1_relationship_other', 'form1_agent_professionalism',
        'form1_agent_responsiveness', 'form1_agent_expectations',
        'form1_agent_transparency', 'form1_agent_negotiation_style',
        'form1_agent_notes', 'form2_player_notes',
        'form2_how_they_carry_themselves', 'form2_preparation_level',
        'form2_preparation_notes', 'form2_how_they_view_themselves',
        'form2_what_is_important_to_them', 'form2_mindset_towards_growth',
        'form2_has_big_injuries', 'form2_injury_periods',
        'form2_personality_traits', 'form2_other_traits',
        'form2_interest_level', 'form2_timeline', 'form2_timeline_selected',
        'form2_timeline_custom', 'form2_salary_expectations',
        'form2_other_opportunities', 'form2_key_talking_points',
        'form2_red_flags', 'form2_red_flag_severity',
        'communication', 'maturity', 'coachability', 'leadership',
        'work_ethic', 'confidence', 'tactical_knowledge', 'team_fit',
        'overall_rating', 'form2_recommendation', 'form2_summary_notes',
        'follow_up_needed', 'follow_up_date', 'action_items'
    ]
    
    for key in form_keys:
        if key in st.session_state:
            current_state[key] = st.session_state[key]
        else:
            current_state[key] = None  # Track missing keys too
    
    # Only save if state has changed (deep comparison)
    if st.session_state.form_history and st.session_state.form_history_index >= 0:
        last_state = st.session_state.form_history[st.session_state.form_history_index]
        # Deep comparison - check if dictionaries are equal
        if last_state == current_state:
            return  # No change, don't save
    
    # Remove any states after current index (when undoing and then making new changes)
    if st.session_state.form_history_index < len(st.session_state.form_history) - 1:
        st.session_state.form_history = st.session_state.form_history[:st.session_state.form_history_index + 1]
    
    # Add new state to history
    st.session_state.form_history.append(current_state.copy())
    st.session_state.form_history_index = len(st.session_state.form_history) - 1
    
    # Limit history to last 50 states
    if len(st.session_state.form_history) > 50:
        st.session_state.form_history = st.session_state.form_history[-50:]
        st.session_state.form_history_index = len(st.session_state.form_history) - 1

def save_state_if_changed(field_key, old_value, new_value):
    """Helper function to save form state if a field value changed."""
    if not st.session_state.get('_undoing', False) and not st.session_state.get('_redoing', False):
        if new_value != old_value:
            # Value changed - save the OLD state before updating
            # Temporarily restore old value, save state, then update
            current_value = st.session_state.get(field_key, None)
            st.session_state[field_key] = old_value
            save_form_state_to_history()
            st.session_state[field_key] = new_value  # Now update to new value
            return True
    return False

def restore_form_state_from_history(index):
    """Restore form state from history at given index."""
    if 'form_history' not in st.session_state or not st.session_state.form_history:
        return False
    
    if index < 0 or index >= len(st.session_state.form_history):
        return False
    
    state = st.session_state.form_history[index]
    for key, value in state.items():
        st.session_state[key] = value
    
    st.session_state.form_history_index = index
    return True

def undo_form():
    """Undo last form change."""
    if 'form_history_index' not in st.session_state or st.session_state.form_history_index <= 0:
        return False
    
    new_index = st.session_state.form_history_index - 1
    return restore_form_state_from_history(new_index)

def redo_form():
    """Redo last undone form change."""
    if 'form_history' not in st.session_state or 'form_history_index' not in st.session_state:
        return False
    
    if st.session_state.form_history_index >= len(st.session_state.form_history) - 1:
        return False
    
    new_index = st.session_state.form_history_index + 1
    return restore_form_state_from_history(new_index)

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

def create_google_calendar_link(title, start_date, description="", location=""):
    """Create a Google Calendar link for an event."""
    from urllib.parse import quote
    
    # Format dates for Google Calendar (YYYYMMDDTHHMMSS)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = start_datetime.replace(hour=start_datetime.hour + 1)  # 1 hour duration
    
    start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
    end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
    
    # Build Google Calendar URL
    params = {
        'action': 'TEMPLATE',
        'text': title,
        'dates': f"{start_str}/{end_str}",
        'details': description,
        'location': location
    }
    
    url = "https://calendar.google.com/calendar/render?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items() if v])
    return url

def create_outlook_calendar_link(title, start_date, description="", location=""):
    """Create an Outlook Calendar link for an event."""
    from urllib.parse import quote
    
    # Format dates for Outlook (YYYY-MM-DDTHH:MM:SS)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = start_datetime.replace(hour=start_datetime.hour + 1)  # 1 hour duration
    
    start_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Build Outlook Calendar URL
    params = {
        'subject': title,
        'startdt': start_str,
        'enddt': end_str,
        'body': description,
        'location': location
    }
    
    url = "https://outlook.live.com/calendar/0/deeplink/compose?" + "&".join([f"{k}={quote(str(v))}" for k, v in params.items() if v])
    return url

def authenticate_google_drive():
    """Authenticate with Google Drive API."""
    if not GOOGLE_DRIVE_AVAILABLE:
        return None
    
    try:
        # Check for client_secrets.json
        creds_file = Path("client_secrets.json")
        if not creds_file.exists():
            st.error("""
            **Google Drive Setup Required**
            
            To use Google Drive sync, you need to:
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select an existing one
            3. Enable the Google Drive API
            4. Create OAuth 2.0 credentials (Desktop app)
            5. Download the credentials as `client_secrets.json`
            6. Place `client_secrets.json` in the same directory as this app
            
            See [PyDrive2 documentation](https://docs.iterative.ai/PyDrive2/) for detailed instructions.
            """)
            return None
        
        gauth = GoogleAuth()
        # Set settings for authentication
        gauth.settings['client_config_file'] = str(creds_file)
        
        # Try to load saved client credentials
        creds_path = Path("mycreds.txt")
        if creds_path.exists():
            gauth.LoadCredentialsFile(str(creds_path))
        
        if gauth.credentials is None:
            # Authenticate if they're not there
            st.info("🔐 Please authenticate with Google Drive. A browser window will open.")
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(str(creds_path))
        
        drive = GoogleDrive(gauth)
        return drive
    except FileNotFoundError:
        st.error("`client_secrets.json` file not found. Please set up Google Drive credentials first.")
        return None
    except Exception as e:
        st.error(f"Error authenticating with Google Drive: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def get_or_create_folder(drive, folder_name="Portland Thorns Call Logs"):
    """Get or create a folder in Google Drive."""
    if not drive:
        return None
    
    try:
        # Search for existing folder
        file_list = drive.ListFile({'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
        
        if file_list:
            return file_list[0]['id']
        else:
            # Create new folder
            folder_metadata = {
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive.CreateFile(folder_metadata)
            folder.Upload()
            return folder['id']
    except Exception as e:
        st.error(f"Error creating folder in Google Drive: {str(e)}")
        return None

def upload_to_google_drive(file_path, folder_name="Portland Thorns Call Logs"):
    """Upload a file to Google Drive."""
    if not GOOGLE_DRIVE_AVAILABLE:
        return False, "Google Drive library not installed. Install with: pip install PyDrive2"
    
    if not file_path or not Path(file_path).exists():
        return False, "File does not exist"
    
    try:
        # Authenticate
        drive = authenticate_google_drive()
        if not drive:
            return False, "Failed to authenticate with Google Drive"
        
        # Get or create folder
        folder_id = get_or_create_folder(drive, folder_name)
        if not folder_id:
            return False, "Failed to create or find folder in Google Drive"
        
        # Check if file already exists (by name)
        file_name = Path(file_path).name
        existing_files = drive.ListFile({
            'q': f"title='{file_name}' and '{folder_id}' in parents and trashed=false"
        }).GetList()
        
        if existing_files:
            # Update existing file
            file_drive = existing_files[0]
            file_drive.SetContentFile(str(file_path))
            file_drive.Upload()
            return True, f"Updated {file_name} in Google Drive"
        else:
            # Upload new file
            file_drive = drive.CreateFile({
                'title': file_name,
                'parents': [{'id': folder_id}]
            })
            file_drive.SetContentFile(str(file_path))
            file_drive.Upload()
            return True, f"Uploaded {file_name} to Google Drive"
            
    except Exception as e:
        return False, f"Error uploading to Google Drive: {str(e)}"

def generate_call_log_pdf(entry):
    """Generate PDF from call log entry using ReportLab."""
    if not PDF_AVAILABLE:
        return None
    
    try:
        # Create PDF in memory - reduced margins to fit on one page
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                              rightMargin=0.3*inch, leftMargin=0.3*inch,
                              topMargin=0.3*inch, bottomMargin=0.3*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles - reduced sizes to fit on one page
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=8,
            borderWidth=0,
            borderPadding=0,
            borderColor=colors.HexColor('#1f77b4'),
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            spaceAfter=4,
            spaceBefore=6,
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=7,
            spaceAfter=2,
        )
        small_style = ParagraphStyle(
            'CustomSmall',
            parent=styles['Normal'],
            fontSize=6,
            textColor=colors.HexColor('#666666'),
        )
        
        # Helper function to get value or N/A
        def get_value(key, default='N/A'):
            val = entry.get(key, default)
            if val is None or val == '' or (isinstance(val, str) and val.strip() == ''):
                return default
            return str(val)
        
        # Title
        player_name = escape_text(entry.get('Player Name', 'Unknown Player'))
        title = Paragraph(f"Call Log Report - {player_name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.05*inch))
        
        # Call Information
        elements.append(Paragraph("Call Information", heading_style))
        call_data = [
            ['Call Date:', escape_text(get_value('Call Date')), 
             'Call Type:', escape_text(get_value('Call Type'))],
            ['Duration:', f"{entry.get('Duration (min)', 0)} min", 
             'Team:', escape_text(get_value('Team'))],
            ['Conference:', escape_text(get_value('Conference')), 
             'Position:', escape_text(get_value('Position Profile'))],
            ['Participants:', escape_text(get_value('Participants'))],
        ]
        call_table = Table(call_data, colWidths=[1.1*inch, 2.4*inch, 1.1*inch, 2.4*inch])
        call_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(call_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Agent Assessment
        elements.append(Paragraph("Agent Assessment", heading_style))
        agent_name = escape_text(get_value('Agent Name'))
        relationship = escape_text(get_value('Relationship'))
        agent_data = [
            ['Agent:', f"{agent_name} ({relationship})"],
            ['Scores:', f"Prof: {entry.get('Agent Professionalism', 'N/A')}/10 | "
                       f"Resp: {entry.get('Agent Responsiveness', 'N/A')}/10 | "
                       f"Exp: {entry.get('Agent Expectations', 'N/A')}/10 | "
                       f"Trans: {entry.get('Agent Transparency', 'N/A')}/10 | "
                       f"Neg: {entry.get('Agent Negotiation Style', 'N/A')}/10"],
            ['Notes:', truncate_text(get_value('Agent Notes'), 80)],
        ]
        agent_table = Table(agent_data, colWidths=[1.1*inch, 5.9*inch])
        agent_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(agent_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Player Notes
        elements.append(Paragraph("Player Notes", heading_style))
        player_notes = truncate_text(get_value('Player Notes'), 120)
        notes_para = Paragraph(f"<b>{player_notes}</b>", normal_style)
        elements.append(notes_para)
        elements.append(Spacer(1, 0.1*inch))
        
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
        assessment_table = Table(assessment_data, colWidths=[0.9*inch, 0.7*inch, 0.9*inch, 0.7*inch, 0.9*inch, 0.7*inch])
        assessment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
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
        elements.append(Spacer(1, 0.1*inch))
        
        # Personality & Self Awareness
        elements.append(Paragraph("Personality & Self Awareness", heading_style))
        personality_items = [
            ('Carry themselves:', get_value('How They Carry Themselves'), 60),
            ('View themselves:', get_value('How They View Themselves'), 60),
            ('Important:', get_value('What Is Important To Them'), 60),
            ('Growth mindset:', get_value('Mindset Towards Growth'), 60),
        ]
        for label, value, max_len in personality_items:
            text = truncate_text(value, max_len)
            para = Paragraph(f"<b>{label}</b> {escape_text(text)}", normal_style)
            elements.append(para)
        # Preparation (special format)
        prep_level = entry.get('Preparation Level', 'N/A')
        prep_notes = truncate_text(get_value('Preparation Notes'), 50)
        prep_text = f"{prep_level}/10 - {prep_notes}"
        elements.append(Paragraph(f"<b>Preparation:</b> {escape_text(prep_text)}", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Key Talking Points - more compact layout
        elements.append(Paragraph("Key Talking Points", heading_style))
        talking_data = [
            ['Interest:', escape_text(get_value('Interest Level')), 
             'Timeline:', escape_text(get_value('Timeline'))],
            ['Salary:', escape_text(truncate_text(get_value('Salary Expectations'), 50))],
            ['Other Opps:', escape_text(truncate_text(get_value('Other Opportunities'), 50))],
            ['Talking Points:', escape_text(truncate_text(get_value('Key Talking Points'), 80))],
        ]
        talking_table = Table(talking_data, colWidths=[0.9*inch, 2.8*inch, 0.9*inch, 2.4*inch])
        talking_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
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
        elements.append(Spacer(1, 0.1*inch))
        
        # Red Flags & Assessment
        elements.append(Paragraph("Red Flags & Assessment", heading_style))
        red_flag_severity = escape_text(get_value('Red Flag Severity'))
        red_flags = truncate_text(get_value('Red Flags'), 80)
        recommendation = escape_text(get_value('Recommendation'))
        summary = truncate_text(get_value('Summary Notes'), 90)
        elements.append(Paragraph(f"<b>Red Flags:</b> {red_flag_severity} - {red_flags}", normal_style))
        elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", normal_style))
        elements.append(Paragraph(f"<b>Summary:</b> {summary}", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Next Steps
        elements.append(Paragraph("Next Steps", heading_style))
        follow_up = 'Yes' if entry.get('Follow-up Needed') else 'No'
        follow_up_date = entry.get('Follow-up Date', '')
        if follow_up == 'Yes' and follow_up_date:
            follow_up += f" - {follow_up_date}"
        action_items = truncate_text(get_value('Action Items'), 80)
        elements.append(Paragraph(f"<b>Follow-up:</b> {follow_up}", normal_style))
        elements.append(Paragraph(f"<b>Action Items:</b> {action_items}", normal_style))
        elements.append(Spacer(1, 0.05*inch))
        
        # Footer
        call_notes = truncate_text(get_value('Call Notes'), 60)
        created_at = escape_text(get_value('Created At'))
        footer_text = f"Call Notes: {call_notes} | Created: {created_at}"
        elements.append(Paragraph(footer_text, small_style))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

def send_feedback_email(feedback_type, subject, description, user_email=None):
    """
    Send feedback email to daniellevitt32@gmail.com.
    
    Args:
        feedback_type: Type of feedback (Bug, Question, Suggestion, Other)
        subject: Subject line
        description: Detailed description
        user_email: Optional user email for response
    
    Returns:
        True if sent successfully, False otherwise
    """
    recipient_email = "daniellevitt32@gmail.com"
    
    # Try to get email credentials from Streamlit secrets
    try:
        if 'email' in st.secrets:
            smtp_server = st.secrets['email'].get('smtp_server', 'smtp.gmail.com')
            smtp_port = st.secrets['email'].get('smtp_port', 587)
            sender_email = st.secrets['email'].get('sender_email', '')
            sender_password = st.secrets['email'].get('sender_password', '')
        else:
            # Fallback: try to use environment variables or default Gmail settings
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = ''
            sender_password = ''
    except:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = ''
        sender_password = ''
    
    # If no credentials configured, return False (will show instructions)
    if not sender_email or not sender_password:
        return None  # None means not configured
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"[Portland Thorns App] {feedback_type}: {subject}"
        
        # Create email body
        body = f"""
Feedback Type: {feedback_type}
Subject: {subject}

Description:
{description}

---
"""
        if user_email:
            body += f"User Email: {user_email}\n"
        body += f"Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        body += f"App: Portland Thorns Call Log System\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

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

# Load agent database
agents_list = load_agent_database()

def get_conferences_from_database():
    """Get list of all conferences from player database."""
    conferences = set()
    for player_name, info in player_info_dict.items():
        conf = info.get('conference', '')
        if conf and str(conf).strip():
            # Normalize conference name
            conf_str = str(conf).strip()
            conferences.add(conf_str)
    
    # If no conferences found in database, provide default list
    if not conferences:
        conferences = {'ACC', 'SEC', 'Big Ten', 'Big 12', 'Ivy League'}
    
    return sorted(list(conferences))

def get_teams_by_conference(conference):
    """Get list of teams for a given conference."""
    if not conference:
        return []
    teams = set()
    for player_name, info in player_info_dict.items():
        # Try exact match first
        conf = info.get('conference', '')
        if conf and str(conf).strip() == str(conference).strip():
            team = info.get('team', '')
            if team and str(team).strip():
                teams.add(str(team).strip())
    
    # If no teams found in database, provide default teams for the conference
    if not teams:
        conference_upper = str(conference).upper().strip()
        default_teams = {
            'ACC': ['Duke', 'North Carolina', 'Virginia', 'Clemson', 'Florida State', 'Virginia Tech', 'Syracuse', 'Louisville', 'Pittsburgh', 'Boston College', 'NC State', 'Wake Forest', 'Miami', 'Notre Dame'],
            'SEC': ['Alabama', 'Georgia', 'Florida', 'LSU', 'Tennessee', 'Arkansas', 'South Carolina', 'Mississippi', 'Mississippi State', 'Auburn', 'Kentucky', 'Vanderbilt', 'Missouri', 'Texas A&M'],
            'BIG TEN': ['Michigan', 'Ohio State', 'Penn State', 'Michigan State', 'Wisconsin', 'Iowa', 'Nebraska', 'Minnesota', 'Indiana', 'Purdue', 'Illinois', 'Northwestern', 'Maryland', 'Rutgers', 'USC', 'UCLA'],
            'BIG 12': ['Texas', 'Oklahoma', 'Kansas', 'Baylor', 'TCU', 'Oklahoma State', 'Texas Tech', 'Iowa State', 'West Virginia', 'Kansas State', 'Houston', 'Cincinnati', 'UCF', 'BYU'],
            'IVY LEAGUE': ['Harvard', 'Yale', 'Princeton', 'Columbia', 'Penn', 'Brown', 'Dartmouth', 'Cornell'],
        }
        
        # Map conference name variations
        conference_map = {
            'BIG TEN': 'BIG TEN',
            'BIG 10': 'BIG TEN',
            'B1G': 'BIG TEN',
            'BIG12': 'BIG 12',
            'BIG 12': 'BIG 12',
            'IVY': 'IVY LEAGUE',
            'IVY LEAGUE': 'IVY LEAGUE',
            'ACC': 'ACC',
            'SEC': 'SEC',
        }
        
        mapped_conf = conference_map.get(conference_upper, conference_upper)
        if mapped_conf in default_teams:
            teams = set(default_teams[mapped_conf])
        elif conference_upper == 'ACC':
            teams = set(default_teams['ACC'])
        elif conference_upper == 'SEC':
            teams = set(default_teams['SEC'])
        elif 'BIG TEN' in conference_upper or 'BIG 10' in conference_upper or 'B1G' in conference_upper:
            teams = set(default_teams['BIG TEN'])
        elif 'BIG 12' in conference_upper or 'BIG12' in conference_upper:
            teams = set(default_teams['BIG 12'])
        elif 'IVY' in conference_upper:
            teams = set(default_teams['IVY LEAGUE'])
    
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

def get_call_number_for_player(player_name, team=None):
    """Get the next call number for a player based on existing calls."""
    if not player_name or not player_name.strip():
        return 1
    
    try:
        if CALL_LOG_FILE.exists():
            df = pd.read_csv(CALL_LOG_FILE)
            if df.empty or 'Player Name' not in df.columns:
                return 1
            
            # Filter by player name (case-insensitive, flexible matching)
            player_name_clean = str(player_name).strip().lower()
            df['Player Name'] = df['Player Name'].astype(str).replace('nan', '')
            matches = df[df['Player Name'].str.lower().str.strip() == player_name_clean].copy()
            
            # If team provided, also filter by team
            if team and len(matches) > 0:
                team_clean = str(team).strip().lower()
                matches['Team'] = matches['Team'].astype(str).replace('nan', '')
                team_matches = (
                    matches['Team'].str.lower().str.strip() == team_clean
                ) | (
                    matches['Team'].str.strip() == ''
                )
                matches = matches[team_matches]
            
            # Get max call number from existing calls
            if 'Call Number' in matches.columns:
                matches['Call Number'] = pd.to_numeric(matches['Call Number'], errors='coerce')
                max_call_num = matches['Call Number'].max()
                if pd.notna(max_call_num):
                    return int(max_call_num) + 1
            
            # If no Call Number column, count existing calls
            return len(matches) + 1
    except Exception as e:
        print(f"Error calculating call number: {e}")
    
    return 1

# Sidebar organization - Priority order:
# 1. Navigation (most important)
# 2. Upload Player Database
# 3. Tips/Help
# 4. Save Draft & Form Controls (only on Phone Calls page)

# Language selector at the top
col_lang1, col_lang2, col_lang3 = st.columns([1, 2, 1])
with col_lang2:
    selected_language = st.selectbox(
        "🌐 Language / Idioma / Langue / Idioma / Sprache / Lingua / العربية",
        ['English', 'Spanish', 'French', 'Portuguese', 'German', 'Italian', 'Arabic'],
        index=['English', 'Spanish', 'French', 'Portuguese', 'German', 'Italian', 'Arabic'].index(st.session_state.language) if st.session_state.language in ['English', 'Spanish', 'French', 'Portuguese', 'German', 'Italian', 'Arabic'] else 0,
        key='language_selector'
    )
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()

st.markdown("---")

# ===========================================
# AUTHENTICATION CHECK
# ===========================================
if not st.session_state["auth"]:
    login_page()
    st.stop()  # Stop execution if not authenticated

# Main app (only shown if authenticated)
# Display branding header on every page
display_branding_header()

st.title(f"{t('title')}")
st.markdown("---")

# Sidebar navigation
# Player Overview PDF Viewer
OVERVIEW_DIR = BASE_DIR / 'Player Overviews'

# 1. Navigation menu (most important - at top)
st.sidebar.markdown("### Navigation")
page = st.sidebar.selectbox(
    "Select Page", 
    [
        "Phone Calls", 
        "Video Analysis",  # Enhanced video tracking
        "Player Summary",
        "Performance Metrics",  # Power BI-style metrics visualization
        "To Do List",  # Task management page
        # "Player Database", 
        # "Scouting Requests", 
        # "View Player Overview",
        # "Update Player Overviews",
        # "Export to SAP",
        # "Export Data"
    ],
    key="page_selector",
    label_visibility="collapsed"
)

# Load players and player info (needed for sidebar display)
players_list = load_player_database()
player_info_dict = load_player_info()

# 2. Upload Player Database
st.sidebar.markdown("### Upload Player Database")
uploaded_file = st.sidebar.file_uploader(
    "Upload player database (Excel file)",
    type=['xlsx', 'xls'],
    help="Upload a shortlist or conference report Excel file. Files are saved permanently.",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    try:
        # Save uploaded file to DATA_DIR (persistent storage)
        uploaded_path = DATA_DIR / uploaded_file.name
        with open(uploaded_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        # Clear cache to reload with new file
        load_player_database.clear()
        load_player_info.clear()
        # Show temporary success message
        st.sidebar.success(f"Uploaded and saved: {uploaded_file.name}")
        st.rerun()
    except Exception as e:
        # Show temporary error message
        st.sidebar.error(f"Error uploading file: {str(e)}")

# Check if uploaded file exists (but don't show permanent status message)
UPLOADED_PLAYER_FILE = None
if PLAYER_DB_FILE and PLAYER_DB_FILE.exists() and DATA_DIR in PLAYER_DB_FILE.parents:
    UPLOADED_PLAYER_FILE = PLAYER_DB_FILE

# 3. Tips/Help button (replaces welcome message)
st.sidebar.markdown("### Tips & Help")
with st.sidebar.expander("How to Use This App", expanded=False):
    st.markdown(f"""
    ### {t('what_app_does')}
    
    {t('what_app_does_desc')}
    
    - **{t('log_calls')}**
    - **{t('track_assessments')}**
    - **{t('generate_reports')}**
    - **{t('view_history')}**
    - **{t('player_overviews')}**
    
    ### {t('first_steps')}
    
    1. **{t('upload_database')}**
       - {t('upload_database_desc')}
    
    2. **{t('log_first_call')}**
       - {t('log_first_call_desc')}
    
    3. **{t('explore_features')}**
       - {t('explore_features_desc')}
    
    ### {t('tips')}
    
    - {t('save_draft_tip')}
    - {t('search_tip')}
    - {t('download_tip')}
    - {t('autopopulate_tip')}
    
    ### ⌨️ Keyboard Shortcuts
    
    **Form Editing:**
    - **⌘Z** (Mac) / **Ctrl+Z** (Windows) - Undo last change
    - **⌘⇧Z** (Mac) / **Ctrl+Shift+Z** (Windows) - Redo last undone change
    - **⌘R** (Mac) / **Ctrl+R** (Windows) - Refresh page (keeps you logged in)
    
    **Navigation:**
    - **⌘K** (Mac) / **Ctrl+K** (Windows) - Focus search/input fields
    - **Tab** - Move to next field
    - **Shift+Tab** - Move to previous field
    - **Enter** - Submit form (when in a form)
    
    **General:**
    - **⌘/** (Mac) / **Ctrl+/** (Windows) - Show keyboard shortcuts help
    - **Esc** - Close dialogs or cancel actions
    
    ### {t('ready_to_start')}
    """)

with st.sidebar.expander("Frequently Asked Questions", expanded=False):
    st.markdown("### Getting Started")
    
    with st.expander("How do I upload a player database?", expanded=False):
        st.markdown("""
        Look for the **"Upload Player Database"** section in the left sidebar. Click **"Browse files"** or drag and drop your Excel file. Supported formats: `.xlsx` or `.xls` files. The file will be saved permanently and loaded automatically.
        """)
    
    with st.expander("How do I log my first call?", expanded=False):
        st.markdown("""
        Go to **"Phone Calls"** in the navigation menu. Select a **Conference** → **Team** → **Player** from the database. Fill in the call details (date, type, duration, notes, assessments) and click **"Save Call Log"** at the bottom.
        """)
    
    with st.expander("What information is required to log a call?", expanded=False):
        st.markdown("""
        Required: Player Name, Call Date, Call Type. All other fields are optional but recommended for comprehensive tracking.
        """)
    
    st.markdown("### Features & Functionality")
    
    with st.expander("How do I generate a PDF report?", expanded=False):
        st.markdown("""
        PDF reports are generated automatically after logging a call and clicking **"Save Call Log"**. The PDF includes all call information, assessments, talking points, and notes.
        """)
    
    with st.expander("How does the Call Number feature work?", expanded=False):
        st.markdown("""
        Call Numbers are auto-calculated based on existing calls for that player (First call = 1, Second call = 2, etc.). You can manually override if needed.
        """)
    
    with st.expander("How do I track video reviews?", expanded=False):
        st.markdown("""
        Go to **"Video Analysis"** in the navigation. Click **"Add Review"** tab and fill in player name, video type, source, and your analysis. All reviews are saved and can be viewed with filters.
        """)
    
    st.markdown("### Data & Storage")
    
    with st.expander("Where is my data stored?", expanded=False):
        st.markdown("""
        All call logs are saved in CSV format locally. Cloud storage functionality is being developed for multi-device access.
        """)
    
    with st.expander("Can I export my data?", expanded=False):
        st.markdown("""
        Yes! Download call logs from "Call History" page in CSV or PDF format. All exports include timestamps and can be filtered before downloading.
        """)
    
    st.markdown("### Technical")
    
    with st.expander("Can I use this on my phone or tablet?", expanded=False):
        st.markdown("""
        Yes! The app is mobile-friendly and works on phones, tablets, and laptops with responsive design.
        """)
    
    with st.expander("What languages are supported?", expanded=False):
        st.markdown("""
        Multi-language support: English, Spanish, French, Portuguese, German, Italian, and Arabic. Use the language selector at the top of the page.
        """)
    
    with st.expander("How do I report a bug or issue?", expanded=False):
        st.markdown("""
        Go to **"Feedback & Support"** in the sidebar under Tips & Help, select **"Bug Report"** as the feedback type, and provide details. You can also email directly: **daniellevitt32@gmail.com**
        """)
    
    st.markdown("### Calendar & Integration")
    
    with st.expander("How does calendar integration work?", expanded=False):
        st.markdown("""
        When logging a call, fill in the **"Next Steps"** section, check **"Follow-up needed"** and select a date, then check **"Add to Google Calendar"** or **"Add to Outlook Calendar"**. The event will be created automatically.
        """)
    
    st.markdown("### 📧 Contact & Support")
    
    with st.expander("How can I get help or contact support?", expanded=False):
        st.markdown("""
        - Check this FAQs section for common questions
        - Use "Feedback & Support" in the sidebar to submit questions
        - Email directly: **daniellevitt32@gmail.com**
        - Response time: Typically within 24-48 hours
        """)

with st.sidebar.expander("Feedback & Support", expanded=False):
    st.markdown("### Submit Your Feedback")
    st.markdown("Have a question, found a bug, or have a suggestion? We'd love to hear from you!")
    
    with st.form("feedback_form_sidebar"):
        feedback_type = st.selectbox(
            "Type of Feedback",
            ["Bug Report", "Question", "Suggestion", "Feature Request", "Other"],
            help="Select the category that best describes your feedback"
        )
        
        subject = st.text_input(
            "Subject",
            placeholder="Brief summary of your feedback",
            help="A short title describing your issue or question"
        )
        
        description = st.text_area(
            "Description",
            placeholder="Please provide as much detail as possible...",
            height=150,
            help="Detailed description of your issue, question, or suggestion"
        )
        
        user_email = st.text_input(
            "Your Email (Optional)",
            placeholder="your.email@example.com",
            help="Optional: Provide your email if you'd like a response"
        )
        
        submitted = st.form_submit_button("Send Feedback", use_container_width=True, type="primary")
        
        if submitted:
            if not subject or not description:
                st.error("Please fill in both Subject and Description fields.")
            else:
                with st.spinner("Sending your feedback..."):
                    result = send_feedback_email(feedback_type, subject, description, user_email)
                    
                    if result is True:
                        st.success("Thank you! Your feedback has been sent successfully. We'll review it and get back to you if needed.")
                    elif result is None:
                        # Email not configured - show instructions and save feedback locally
                        st.warning("Email sending is not currently configured, but your feedback has been recorded.")
                        
                        # Save feedback to local file as backup
                        feedback_file = DATA_DIR / 'feedback_log.csv'
                        feedback_entry = {
                            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Type': feedback_type,
                            'Subject': subject,
                            'Description': description,
                            'User Email': user_email if user_email else 'Not provided'
                        }
                        
                        try:
                            if feedback_file.exists():
                                feedback_df = pd.read_csv(feedback_file)
                                feedback_df = pd.concat([feedback_df, pd.DataFrame([feedback_entry])], ignore_index=True)
                            else:
                                feedback_df = pd.DataFrame([feedback_entry])
                            feedback_df.to_csv(feedback_file, index=False)
                            st.success("Your feedback has been saved locally and will be reviewed.")
                        except Exception as e:
                            st.error(f"Error saving feedback: {e}")
                        
                        st.info("""
                        **To enable automatic email notifications:**
                        
                        Email setup is required for automatic delivery. For now, your feedback has been saved locally.
                        
                        **Direct Contact:**
                        You can also reach out directly at: **daniellevitt32@gmail.com**
                        """)
                    else:
                        st.error("There was an error sending your feedback. Please try again or contact daniellevitt32@gmail.com directly.")
    
    st.markdown("---")
    st.markdown("### Direct Contact")
    st.markdown("""
    You can also reach out directly:
    - **Email:** [daniellevitt32@gmail.com](mailto:daniellevitt32@gmail.com)
    - **Response Time:** We typically respond within 24-48 hours
    """)

# 4. Form Controls (only on Phone Calls page)
if page == "Phone Calls":
    st.sidebar.markdown("### Form Controls")
    
    # Save Draft button
    if st.sidebar.button(f"{t('save_draft')}", key="save_draft_btn", use_container_width=True, help="Save your progress without submitting. Data will be restored when you return."):
        if save_draft():
            st.sidebar.success("Draft saved!")
    
    # Show draft status
    draft_exists = DRAFT_FILE.exists()
    if draft_exists:
        draft_data = load_draft()
        if draft_data and 'saved_at' in draft_data:
            st.sidebar.caption(f"Draft saved: {draft_data['saved_at']}")
        if st.sidebar.button("Clear Draft", key="clear_draft_btn", use_container_width=True):
            clear_draft()
            st.rerun()
    
    # Refresh button
    if st.sidebar.button("Refresh Form", key="refresh_form_btn", use_container_width=True, help="Clear all form fields and start fresh (does not log you out)"):
        reset_form()
        st.sidebar.success("Form refreshed! All fields cleared.")
        st.rerun()

if page == "Phone Calls":
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
    
    # Welcome message removed - now available in sidebar Tips & Help section
    
    st.header(f"{t('log_new_call')}")
    
    # Create tabs for Phone Calls page
    tab1, tab2, tab3 = st.tabs(["Call Log System", "Call History", "Player Call Rankings"])
    
    with tab1:
        # Save form state to history BEFORE any fields are rendered/updated
        # This ensures undo captures the state before changes are made
        if not st.session_state.get('_undoing', False) and not st.session_state.get('_redoing', False):
            # Only save if this is a new interaction (not just a rerun with same values)
            # We'll check for actual changes in save_form_state_to_history()
            if 'form_history' not in st.session_state or len(st.session_state.get('form_history', [])) == 0:
                # Initialize with current state if history is empty
                save_form_state_to_history()
            else:
                # Save state before any potential changes
                save_form_state_to_history()
        
        # Call Recording Upload (Audio/Video) - MOVED TO TOP
        st.markdown("### Call Recording")
        st.markdown("Upload audio or video recording of the call (phone call audio or video call recording). You can re-listen/watch later.")
        call_recording = st.file_uploader(
        "Upload Call Recording",
        type=['mp3', 'wav', 'm4a', 'mp4', 'mov', 'avi'],
        help="Upload audio (mp3, wav, m4a) or video (mp4, mov, avi) recordings of the call. Files are stored locally.",
        key="call_recording_uploader"
        )
    
        # Create call recordings directory
        call_recordings_dir = DATA_DIR / 'call_recordings'
        call_recordings_dir.mkdir(exist_ok=True)
        
        call_recording_path = None
        if call_recording is not None:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # We'll use a placeholder since player_name might not be selected yet
            file_extension = call_recording.name.split('.')[-1] if '.' in call_recording.name else 'mp3'
            recording_filename = f"recording_{timestamp}.{file_extension}"
            recording_file_path = call_recordings_dir / recording_filename
            
            # Save the uploaded file immediately
            try:
                with open(recording_file_path, 'wb') as f:
                    f.write(call_recording.getbuffer())
                st.success(f"Recording uploaded: {call_recording.name} ({call_recording.size / (1024*1024):.2f} MB)")
                call_recording_path = str(recording_file_path)
                st.session_state['pending_call_recording_path'] = call_recording_path
            except Exception as e:
                st.error(f"Error saving recording: {e}")
                call_recording_path = None
        else:
            # Check for previously uploaded recording
            call_recording_path = st.session_state.get('pending_call_recording_path', None)
    
        # Show recording preview if available
        if call_recording is not None:
            st.markdown("**Recording Preview:**")
            try:
                # Determine if it's audio or video
                file_ext = call_recording.name.split('.')[-1].lower() if '.' in call_recording.name else ''
                if file_ext in ['mp3', 'wav', 'm4a']:
                    st.audio(call_recording)
                elif file_ext in ['mp4', 'mov', 'avi']:
                    st.video(call_recording)
            except Exception as e:
                st.error(f"Error displaying recording preview: {e}")
        elif call_recording_path and Path(call_recording_path).exists():
            st.markdown("**Recording Preview:**")
            try:
                recording_file = Path(call_recording_path)
                file_ext = recording_file.suffix.lower()
                with open(recording_file, 'rb') as f:
                    recording_bytes = f.read()
                if file_ext in ['.mp3', '.wav', '.m4a']:
                    st.audio(recording_bytes)
                elif file_ext in ['.mp4', '.mov', '.avi']:
                    st.video(recording_bytes)
            except Exception as e:
                st.error(f"Error displaying recording: {e}")
    
        st.markdown("---")
    
        # Player selection OUTSIDE form so it updates reactively
        use_custom_player = st.checkbox(t('player_not_in_database'), key="use_custom_player")
    
        if use_custom_player:
            # Custom player entry
            player_name = st.text_input(t('player_name'), key="custom_player_name", placeholder=t('enter_player_name'))
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
                t('conference'),
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
                    t('team'),
                    [""] + teams_list,
                    key="filter_team_select",
                    index=0 if not current_team else (teams_list.index(current_team) + 1 if current_team in teams_list else 0)
                )
                st.session_state.filter_team = team_filter
            else:
                st.selectbox(t('team'), [""], key="filter_team_select_disabled", disabled=True)
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
        if not players_list:
            st.warning("⚠️ **No player database loaded.** Please upload a player database file using the sidebar uploader (under 'Upload Player Database') to enable player selection.")
            st.info("💡 **Tip:** You can still log calls for players not in the database by checking 'Player not in database' below.")
            player_name = st.text_input(t('player_name'), key="player_select_manual")
        else:
            col_search, col_select = st.columns([2, 3])
            with col_search:
                player_search = st.text_input(f"{t('search_player')}", key="player_search")
            with col_select:
                if player_search:
                    filtered_players = [p for p in available_players if player_search.lower() in p.lower()]
                else:
                    filtered_players = available_players
                
                player_name = st.selectbox(t('player_name'), [""] + filtered_players[:200], key="player_select")  # Increased limit since we're filtering
    
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
                st.info(f"**{t('team')}**: {auto_team}")
            with col_info2:
                st.info(f"**{t('conference')}**: {auto_conference}")
            with col_info3:
                st.info(f"**{t('position')}**: {auto_position}")
        elif not player_name:
            st.session_state.selected_player_team = ''
            st.session_state.selected_player_conference = ''
            st.session_state.selected_player_position = ''
        # Show info boxes even when no player selected
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.info(f"**{t('team')}**: -")
        with col_info2:
            st.info(f"**{t('conference')}**: -")
        with col_info3:
            st.info(f"**{t('position')}**: -")
    
        # Call details and Agent Assessment - no form wrapper for reactive updates
        col1, col2 = st.columns(2)
    
        with col1:
            call_date = st.date_input(t('call_date'), value=st.session_state.get('form1_call_date', datetime.now().date()))
            call_type = st.selectbox(t('call_type'), ["Player Call", "Agent Call", "Both"], index=["Player Call", "Agent Call", "Both"].index(st.session_state.get('form1_call_type', "Player Call")) if st.session_state.get('form1_call_type', "Player Call") in ["Player Call", "Agent Call", "Both"] else 0)
        
        # Calculate call number for selected player
        call_number = 1
        if player_name and player_name.strip():
            # Get team for call number calculation
            calc_team = (st.session_state.get('filter_team') or 
                        st.session_state.get('form1_team') or 
                        st.session_state.selected_player_team)
            call_number = get_call_number_for_player(player_name, calc_team)
        
        # Allow manual override of call number
        call_number = st.number_input(t('call_number'), min_value=1, max_value=100, value=call_number, help="Call number for this player (auto-calculated based on existing calls)")
        
        duration = st.number_input(t('duration_minutes'), min_value=0, max_value=300, value=st.session_state.get('form1_duration', 30))
        
        # Use filter values if manually selected, otherwise use auto-populated values from player selection
        # Priority: filter values > auto-populated > form1 values
        team = (st.session_state.get('filter_team') or 
                st.session_state.get('form1_team') or 
                st.session_state.selected_player_team)
        conference = (st.session_state.get('filter_conference') or 
                      st.session_state.get('form1_conference') or 
                      st.session_state.selected_player_conference)
        conference_other = st.session_state.get('form1_conference_other', '')
        # Position Profile removed - using auto-populated position from player selection
        position_profile = st.session_state.selected_player_position
    
        with col2:
            participants = st.text_area(t('participants'), value=st.session_state.get('form1_participants', ''), placeholder=t('list_participants'))
            call_notes = st.text_area(t('call_notes'), value=st.session_state.get('form1_call_notes', ''), placeholder=t('general_notes'))
    
        st.markdown(f"### {t('agent_assessment')}")
        # Agent name with dropdown + custom entry
        agent_options = [""] + agents_list
        agent_selected = st.selectbox(t('agent_name'), agent_options, key="agent_select", index=agent_options.index(st.session_state.get('form1_agent_selected', '')) if st.session_state.get('form1_agent_selected', '') in agent_options else 0)
        agent_custom = st.text_input(t('or_enter_new_agent'), value=st.session_state.get('form1_agent_custom', ''), placeholder=t('leave_empty_if_using_dropdown'), key="agent_custom")
    
        # Use custom if provided, otherwise use selected
        agent_name = agent_custom.strip() if agent_custom.strip() else agent_selected
        relationship = st.selectbox(
        t('relationship'),
        ["Professional Agent", "Family Member", "Parent", "Guardian", "Other"],
        index=["Professional Agent", "Family Member", "Parent", "Guardian", "Other"].index(st.session_state.get('form1_relationship', "Professional Agent")) if st.session_state.get('form1_relationship', "Professional Agent") in ["Professional Agent", "Family Member", "Parent", "Guardian", "Other"] else 0,
        help="Select the relationship of the person representing the player"
        )
        relationship_other = st.text_input(t('relationship_other'), value=st.session_state.get('form1_relationship_other', ''), placeholder=t('specify_if_other'), disabled=(relationship != "Other"))
    
        col6, col7, col8, col9, col10 = st.columns(5)
        with col6:
            agent_professionalism = st.slider(t('agent_professionalism'), 1, 10, st.session_state.get('form1_agent_professionalism', 5))
        with col7:
            agent_responsiveness = st.slider(t('agent_responsiveness'), 1, 10, st.session_state.get('form1_agent_responsiveness', 5))
        with col8:
            agent_expectations = st.slider(t('reasonable_expectations'), 1, 10, st.session_state.get('form1_agent_expectations', 5))
        with col9:
            agent_transparency = st.slider(t('transparency_honesty'), 1, 10, st.session_state.get('form1_agent_transparency', 5))
        with col10:
            agent_negotiation_style = st.slider(t('negotiation_style'), 1, 10, st.session_state.get('form1_agent_negotiation_style', 5), help=t('negotiation_help'))
    
        agent_notes = st.text_area(t('agent_notes'), value=st.session_state.get('form1_agent_notes', ''))
    
        # Store values in session state for form submission
        st.session_state.form1_call_date = call_date
        st.session_state.form1_call_type = call_type
        st.session_state.form1_call_number = call_number
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
        st.markdown(f"### {t('player_notes_section')}")
        player_notes = st.text_area(t('player_notes_field'), value=st.session_state.get('form2_player_notes', ''), placeholder=t('general_notes_player'))
        st.session_state.form2_player_notes = player_notes
    
        st.markdown(f"### {t('personality_self_awareness')}")
        how_they_carry_themselves = st.text_area(
        t('how_they_carry'),
        placeholder=t('how_they_carry_placeholder')
        )
        preparation_level = st.slider(t('preparation_level'), 1, 10, 5, help=t('preparation_help'))
        preparation_notes = st.text_area(
        t('preparation_notes'),
        placeholder=t('preparation_notes_placeholder')
        )
    
        st.markdown("### Self Awareness / Player Identity")
        how_they_view_themselves = st.text_area(
        t('how_they_view'),
        placeholder=t('how_they_view_placeholder')
        )
        what_is_important_to_them = st.text_area(
        t('what_important'),
        placeholder=t('what_important_placeholder')
        )
        mindset_towards_growth = st.text_area(
        t('mindset_growth'),
        placeholder=t('mindset_growth_placeholder')
        )
    
        st.markdown("### Injuries")
        has_big_injuries = st.selectbox(
        t('has_big_injuries'),
        ["No", "Yes", "Unknown"]
        )
        injury_periods = st.text_area(
        t('injury_periods'),
        placeholder=t('injury_periods_placeholder'),
        disabled=(has_big_injuries != "Yes")
        )
    
        st.markdown(f"### {t('personality_traits')}")
        personality_traits = st.multiselect(
        "Select applicable traits",
        ["Competitive", "Resilient", "Humble", "Driven", "Team-first", "Self-aware", "Confident", "Focused", "Adaptable", "Other"]
        )
        other_traits = st.text_input(t('other_traits'))
    
        st.markdown(f"### {t('key_talking_points_section')}")
        interest_level = st.selectbox(t('interest_level'), ["Very High", "High", "Medium", "Low", "Very Low", "Unknown"])
    
        # Timeline dropdown with custom option
        timeline_options = ["Immediately", "3 months", "6 months", "1 year", "Other"]
        timeline_selected = st.selectbox(t('timeline'), timeline_options, index=timeline_options.index(st.session_state.get('form2_timeline_selected', 'Immediately')) if st.session_state.get('form2_timeline_selected', 'Immediately') in timeline_options else 0)
        st.session_state.form2_timeline_selected = timeline_selected
    
        if timeline_selected == "Other":
            timeline_custom = st.text_input(t('timeline_custom'), value=st.session_state.get('form2_timeline_custom', ''), placeholder=t('enter_custom_timeline'))
            st.session_state.form2_timeline_custom = timeline_custom
            timeline = timeline_custom
        else:
            timeline = timeline_selected
            st.session_state.form2_timeline_custom = ''
    
        salary_expectations = st.text_input(t('salary_expectations'), placeholder=t('if_discussed'))
        other_opportunities = st.text_area(t('other_opportunities'), placeholder=t('other_opportunities_placeholder'))
        key_talking_points = st.text_area(t('key_talking_points'), placeholder=t('main_discussion_points'))
    
        st.markdown(f"### {t('red_flags_concerns')}")
        red_flag_severity = st.selectbox(t('severity'), ["None", "Low", "Medium", "High"])
    
        # Get old value BEFORE rendering the field (for undo to work)
        old_red_flags = st.session_state.get('form2_red_flags', '')
        red_flags = st.text_area(t('red_flags'), placeholder=t('any_concerns'), value=old_red_flags, key='red_flags_input')
    
        # Save state if value changed (using helper function)
        save_state_if_changed('form2_red_flags', old_red_flags, red_flags)
    
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
    
        st.markdown(f"### {t('assessment_summary')}")
        col_score1, col_score2, col_score3 = st.columns(3)
        with col_score1:
            st.metric(t('total_assessment_score'), f"{assessment_total}/{max_possible}")
        with col_score2:
            st.metric(t('assessment_percentage'), f"{assessment_percentage:.1f}%")
        with col_score3:
            st.metric(t('grade'), assessment_grade)
    
        st.markdown(f"### {t('overall_assessment')}")
        recommendation = st.selectbox(t('recommendation'), ["Strong Yes", "Yes", "Maybe", "No", "Strong No"])
        summary_notes = st.text_area(t('summary_notes'), placeholder=t('overall_impression'))
    
        # Store Overall Assessment values in session state
        st.session_state.form2_recommendation = recommendation
        st.session_state.form2_summary_notes = summary_notes
    
        # Next Steps section - outside form for reactive updates
        st.markdown(f"### {t('next_steps')}")
        follow_up_needed = st.checkbox(t('follow_up_needed'), value=st.session_state.get('follow_up_needed', False))
        st.session_state.follow_up_needed = follow_up_needed
    
        # Always show date input, but disable it when checkbox is unchecked
        follow_up_date = st.date_input(
        t('follow_up_date'), 
        value=st.session_state.get('follow_up_date', datetime.now().date()) if st.session_state.get('follow_up_date') else datetime.now().date(),
        disabled=not follow_up_needed
        )
        if follow_up_needed:
            st.session_state.follow_up_date = follow_up_date
        else:
            st.session_state.follow_up_date = None
    
        action_items = st.text_area(t('action_items'), value=st.session_state.get('action_items', ''), placeholder=t('what_needs_happen'))
        st.session_state.action_items = action_items
    
        # Calendar Integration
        if follow_up_needed and follow_up_date:
            st.markdown("#### 📅 Add to Calendar")
            calendar_col1, calendar_col2 = st.columns(2)
            
            # Get player name for event title
            player_name = st.session_state.get('player_select', '') or st.session_state.get('custom_player_name', 'Unknown Player')
            action_items_text = st.session_state.get('action_items', '')
            
            # Create event title
            event_title = f"Follow-up: {player_name}"
            event_description = f"Follow-up call with {player_name}"
            if action_items_text:
                event_description += f"\n\nAction Items:\n{action_items_text}"
            
            with calendar_col1:
                google_cal_link = create_google_calendar_link(
                    event_title,
                    follow_up_date,
                    event_description
                )
                st.markdown(f'<a href="{google_cal_link}" target="_blank" style="text-decoration: none;"><button style="background-color: #4285F4; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%;">📅 Add to Google Calendar</button></a>', unsafe_allow_html=True)
            
            with calendar_col2:
                outlook_cal_link = create_outlook_calendar_link(
                    event_title,
                    follow_up_date,
                    event_description
                )
                st.markdown(f'<a href="{outlook_cal_link}" target="_blank" style="text-decoration: none;"><button style="background-color: #0078D4; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%;">📅 Add to Outlook Calendar</button></a>', unsafe_allow_html=True)
    
        
        # Add keyboard shortcut support via JavaScript
        components.html("""
        <script>
        (function() {
            function findButtonByKey(key) {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = btn.textContent || '';
                    if (key === 'undo' && text.includes('Undo')) {
                        return btn;
                    }
                    if (key === 'redo' && text.includes('Redo')) {
                        return btn;
                    }
                }
                return null;
            }
            
            document.addEventListener('keydown', function(e) {
                // CMD+Z or CTRL+Z for Undo
                if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey && !e.altKey) {
                    e.preventDefault();
                    e.stopPropagation();
                    const undoBtn = findButtonByKey('undo');
                    if (undoBtn && !undoBtn.disabled) {
                        undoBtn.click();
                    }
                }
                // CMD+SHIFT+Z or CTRL+SHIFT+Z for Redo
                if ((e.metaKey || e.ctrlKey) && e.key === 'z' && e.shiftKey && !e.altKey) {
                    e.preventDefault();
                    e.stopPropagation();
                    const redoBtn = findButtonByKey('redo');
                    if (redoBtn && !redoBtn.disabled) {
                        redoBtn.click();
                    }
                }
            }, true);
        })();
        </script>
        """, height=0)
    
        # Final form for submission only
        with st.form("call_log_form_final"):
            # Google Drive sync option
            save_to_drive = st.checkbox(
                "💾 Save to Google Drive",
                value=st.session_state.get('save_to_drive', False),
                help="Upload call log to Google Drive after saving locally"
            )
            st.session_state.save_to_drive = save_to_drive
            
            submitted = st.form_submit_button(f"{t('save_call_log')}", use_container_width=True)
            
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
                # Use filter values if manually selected, otherwise use auto-populated or form1 values
                final_team = (st.session_state.get('filter_team') or 
                             st.session_state.get('form1_team') or 
                             st.session_state.selected_player_team or '')
                
                # Conference: check if "Other" was selected, otherwise use filter/auto-populated/form1
                conference_value = (st.session_state.get('filter_conference') or 
                                   st.session_state.get('form1_conference') or 
                                   st.session_state.selected_player_conference or '')
                final_conference = st.session_state.get('form1_conference_other') if conference_value == "Other" else conference_value
                
                final_relationship = st.session_state.get('form1_relationship_other') if st.session_state.get('form1_relationship') == "Other" else st.session_state.get('form1_relationship', '')
                
                # Get call recording path from session state
                call_recording_path_final = st.session_state.get('pending_call_recording_path', None)
                
                new_entry = {
                    'Call Date': (st.session_state.get('form1_call_date') or datetime.now().date()).strftime('%Y-%m-%d') if isinstance(st.session_state.get('form1_call_date', None), date) else datetime.now().date().strftime('%Y-%m-%d'),
                    'Player Name': player_name,
                    'Team': final_team,
                    'Conference': final_conference,
                    'Position Profile': st.session_state.get('form1_position_profile', ''),
                    'Call Type': st.session_state.get('form1_call_type', ''),
                    'Call Number': st.session_state.get('form1_call_number', 1),
                    'Duration (min)': st.session_state.get('form1_duration', 0),
                    'Participants': st.session_state.get('form1_participants', ''),
                    'Call Notes': st.session_state.get('form1_call_notes', ''),
                    'Call Recording': call_recording_path_final if call_recording_path_final else '',
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
                # Refresh session state with updated call log
                st.session_state.call_log = load_call_log()
                # Clear draft after successful submission
                clear_draft()
                # Clear pending recording path after successful save
                if 'pending_call_recording_path' in st.session_state:
                    del st.session_state['pending_call_recording_path']
                st.success("Call log saved successfully!")
                
                # Upload to Google Drive if enabled
                if save_to_drive:
                    with st.spinner("Uploading to Google Drive..."):
                        success, message = upload_to_google_drive(str(CALL_LOG_FILE))
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.warning(f"⚠️ {message}")
                            if "not installed" in message.lower():
                                st.info("💡 To enable Google Drive sync, install PyDrive2: `pip install PyDrive2`")
                
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
                        st.info("Install reportlab to enable PDF downloads: `pip install reportlab`")
    
        # PDF download button (outside form)
        if st.session_state.get('show_pdf_download', False):
            pdf_bytes = st.session_state.get('pdf_download_data')
            pdf_filename = st.session_state.get('pdf_download_filename', 'call_log.pdf')
            if pdf_bytes:
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True,
                    key="pdf_download_btn"
                )
                # Clear the download state after showing
            st.session_state['show_pdf_download'] = False
    
    with tab2:
        st.subheader("Call History")
        
        # Refresh call log from file to ensure we have latest data
        st.session_state.call_log = load_call_log()
        
        # Debug info (remove after fixing)
        if st.session_state.call_log.empty:
            with st.expander("Debug Info", expanded=False):
                st.write(f"Call log file path: {CALL_LOG_FILE}")
            st.write(f"File exists: {CALL_LOG_FILE.exists()}")
            if CALL_LOG_FILE.exists():
                st.write(f"File size: {CALL_LOG_FILE.stat().st_size} bytes")
                try:
                    test_df = pd.read_csv(CALL_LOG_FILE)
                    st.write(f"Rows in file: {len(test_df)}")
                    st.write(f"Columns: {list(test_df.columns)[:5]}")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        
        # Initialize view_mode if not set (must be before buttons)
        if "view_mode" not in st.session_state:
            st.session_state.view_mode = "Summary"
        
        # Get view_mode - always define it before use
        view_mode = st.session_state.get("view_mode", "Summary")
        
        if st.session_state.call_log.empty:
            st.info("No call logs yet. Log your first call!")
        else:
            # Use toggle buttons for better visibility
            st.markdown("### View Mode")
            
            # Add custom CSS for view mode buttons
            st.markdown("""
            <style>
                div[data-testid="stButton"] > button[kind="secondary"] {
                    background-color: #000000 !important;
                    color: #ffffff !important;
                    border: 1px solid #3a3a3a !important;
                }
                div[data-testid="stButton"] > button[kind="secondary"]:hover {
                    background-color: #1a1a1a !important;
                    border-color: #8B0000 !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Get current view mode safely (with default)
            current_view_mode = st.session_state.get("view_mode", "Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Summary", use_container_width=True, type="primary" if current_view_mode == "Summary" else "secondary"):
                    st.session_state.view_mode = "Summary"
                    st.rerun()
            with col2:
                if st.button("Expanded", use_container_width=True, type="primary" if current_view_mode == "Expanded" else "secondary"):
                    st.session_state.view_mode = "Expanded"
                    st.rerun()
            
            # Update view_mode after button clicks
            view_mode = st.session_state.get("view_mode", "Summary")
            st.markdown("---")
            
            # ===========================================
            # IMPROVEMENT 7: Enhanced Date Range Filter
            # ===========================================
            # Initialize sorting state before using it
            if "table_sort_column" not in st.session_state:
                st.session_state.table_sort_column = None
            if "table_sort_direction" not in st.session_state:
                st.session_state.table_sort_direction = "asc"
            
            st.markdown("### Filters")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # Check if 'Player Name' column exists
                if 'Player Name' in st.session_state.call_log.columns:
                    filter_player = st.multiselect("Filter by Player", sorted(st.session_state.call_log['Player Name'].unique().tolist()))
                else:
                    filter_player = []
            with col2:
                # Check if 'Recommendation' column exists
                if 'Recommendation' in st.session_state.call_log.columns:
                    filter_recommendation = st.multiselect("Filter by Recommendation", sorted(st.session_state.call_log['Recommendation'].unique().tolist()))
                else:
                    filter_recommendation = []
            with col3:
                date_preset = st.selectbox("Date Preset", ["All Time", "Last 7 Days", "Last 30 Days", "This Month", "This Year", "Custom Range"])
            with col4:
                if date_preset == "Custom Range":
                    date_start = st.date_input("Start Date", value=None, key="date_start")
                    date_end = st.date_input("End Date", value=None, key="date_end")
                else:
                    date_start = None
                    date_end = None
            
            # Calculate player percentiles to add as column (before filtering)
            def calculate_percentiles_for_table(call_log_df):
                """Calculate percentiles for all players and return as dictionary."""
                if 'Player Name' not in call_log_df.columns or call_log_df.empty:
                    return {}
                all_players = call_log_df['Player Name'].unique()
                player_scores = []
                
                for p in all_players:
                    p_calls = call_log_df[call_log_df['Player Name'] == p]
                    avg_score = (
                        p_calls['Communication'].mean() + p_calls['Maturity'].mean() + 
                        p_calls['Coachability'].mean() + p_calls['Leadership'].mean() + 
                        p_calls['Work Ethic'].mean() + p_calls['Confidence'].mean() + 
                        p_calls['Tactical Knowledge'].mean() + p_calls['Team Fit'].mean() + 
                        p_calls['Overall Rating'].mean()
                    ) / 9
                    player_scores.append({'player': p, 'score': avg_score})
                
                scores_df = pd.DataFrame(player_scores)
                scores_df = scores_df.sort_values('score', ascending=False)
                scores_df['rank'] = range(1, len(scores_df) + 1)
                
                # Fix percentile calculation: rank 1 (best) should be 100th percentile, rank N (worst) should be lowest
                # Formula: percentile = ((total - rank) / (total - 1)) * 100
                total = len(scores_df)
                if total > 1:
                    scores_df['percentile'] = ((total - scores_df['rank']) / (total - 1) * 100).round(1)
                else:
                    scores_df['percentile'] = 100.0  # If only one player, they're 100th percentile
                
                # Return percentile dictionary
                return dict(zip(scores_df['player'], scores_df['percentile']))
            
            # Get percentiles
            percentile_dict = calculate_percentiles_for_table(st.session_state.call_log)
            
            # Apply filters
            filtered_log = st.session_state.call_log.copy()
            
            # Apply regular filters
            if filter_player:
                filtered_log = filtered_log[filtered_log['Player Name'].isin(filter_player)]
            if filter_recommendation:
                filtered_log = filtered_log[filtered_log['Recommendation'].isin(filter_recommendation)]
            
            # Apply date range filter
            if date_preset != "All Time":
                try:
                    filtered_log['Call Date'] = pd.to_datetime(filtered_log['Call Date'], errors='coerce')
                    today = datetime.now().date()
                    
                    if date_preset == "Last 7 Days":
                        date_start = today - timedelta(days=7)
                        date_end = today
                    elif date_preset == "Last 30 Days":
                        date_start = today - timedelta(days=30)
                        date_end = today
                    elif date_preset == "This Month":
                        date_start = datetime.now().replace(day=1).date()
                        date_end = today
                    elif date_preset == "This Year":
                        date_start = datetime.now().replace(month=1, day=1).date()
                        date_end = today
                    elif date_preset == "Custom Range":
                        if date_start and date_end:
                            date_start = date_start
                            date_end = date_end
                        else:
                            date_start = None
                            date_end = None
                    
                    if date_start and date_end:
                        filtered_log = filtered_log[
                            (filtered_log['Call Date'].dt.date >= date_start) & 
                            (filtered_log['Call Date'].dt.date <= date_end)
                        ]
                except Exception as e:
                    pass
            
            # Percentile column already added before filtering
            
            # Rename columns
            column_renames = {
                'Player Percentile': 'Percentile',
                'Assessment Total Score': 'Assessment Score',
                'Agent Name': 'Agent',
                'Follow-up Needed': 'Follow-up',
                'Call Number': 'Call No.'
            }
            filtered_log = filtered_log.rename(columns=column_renames)
            
            # Format values
            if 'Follow-up' in filtered_log.columns:
                filtered_log['Follow-up'] = filtered_log['Follow-up'].apply(lambda x: 'Yes' if x == True or str(x).lower() == 'true' else 'No')
            
            if 'Call No.' in filtered_log.columns:
                filtered_log['Call No.'] = filtered_log['Call No.'].apply(lambda x: int(float(x)) if pd.notna(x) and str(x) != '' else x)
            
            # Define summary columns in the specified order
            summary_columns = [
                'Player Name',
                'Percentile',
                'Team',
                'Conference',
                'Position Profile',
                'Call Type',
                'Call Date',
                'Assessment Score',
                'Assessment Grade',
                'Agent',
                'Interest Level',
                'Salary Expectations',
                'Red Flags',
                'Recommendation',
                'Follow-up',
                'Follow-up Date',
                'Call No.'
            ]
            
            # ===========================================
            # IMPROVEMENT 6: Column Visibility Toggle
            # ===========================================
            if "column_visibility" not in st.session_state:
                st.session_state.column_visibility = {}
            
            # Initialize checkbox key counter to force widget reset when clearing
            if "checkbox_key_counter" not in st.session_state:
                st.session_state.checkbox_key_counter = 0
            
            # Initialize column visibility presets - load from file if exists
            if "column_visibility_presets" not in st.session_state:
                st.session_state.column_visibility_presets = load_column_presets()
            
            # Select columns based on view mode
            if view_mode == "Summary":
                # Only include columns that exist in the dataframe
                available_summary_cols = [col for col in summary_columns if col in filtered_log.columns]
                filtered_log = filtered_log[available_summary_cols]
                all_available_cols = available_summary_cols
            else:
                # Expanded view - show all columns, but keep percentile after Player Name
                cols = list(filtered_log.columns)
                if 'Player Name' in cols and 'Percentile' in cols:
                    player_idx = cols.index('Player Name')
                    cols.insert(player_idx + 1, cols.pop(cols.index('Percentile')))
                filtered_log = filtered_log[cols]
                all_available_cols = cols
            
            # Column visibility toggle (only for Expanded view)
            if view_mode == "Expanded":
                with st.expander("👁️ Show/Hide Columns", expanded=False):
                    # Preset management section
                    preset_col1, preset_col2, preset_col3 = st.columns([2, 2, 1])
                with preset_col1:
                    # Initialize last applied preset tracker
                    if "last_applied_preset" not in st.session_state:
                        st.session_state.last_applied_preset = None
                    
                    # Load preset dropdown
                    preset_names = ["None"] + list(st.session_state.column_visibility_presets.keys())
                    selected_preset = st.selectbox(
                        "Load Preset",
                        preset_names,
                        key="preset_selector",
                        help="Select a saved column visibility preset"
                    )
                    
                    # Only apply preset if it changed and is not "None"
                    if selected_preset != "None" and selected_preset != st.session_state.last_applied_preset:
                        # Apply the selected preset
                        preset_visibility = st.session_state.column_visibility_presets[selected_preset]
                        for col in all_available_cols:
                            # Only apply if column exists in preset, otherwise keep current state
                            if col in preset_visibility:
                                st.session_state.column_visibility[col] = preset_visibility[col]
                            else:
                                # If column doesn't exist in preset, default to True
                                st.session_state.column_visibility[col] = True
                        # Track that we applied this preset
                        st.session_state.last_applied_preset = selected_preset
                        # Increment counter to force widget reset
                        st.session_state.checkbox_key_counter += 1
                        st.rerun()
                    elif selected_preset == "None" and st.session_state.last_applied_preset is not None:
                        # Reset tracker when "None" is selected
                        st.session_state.last_applied_preset = None
                
                with preset_col2:
                    # Save current selection as preset
                    new_preset_name = st.text_input(
                        "Save as Preset",
                        key="new_preset_name",
                        placeholder="Enter preset name...",
                        help="Save current column selection as a named preset"
                    )
                
                with preset_col3:
                    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                    if st.button("💾 Save", key="save_preset", use_container_width=True):
                        if new_preset_name and new_preset_name.strip():
                            # Save current column visibility state
                            current_visibility = {}
                            for col in all_available_cols:
                                current_visibility[col] = st.session_state.column_visibility.get(col, True)
                            st.session_state.column_visibility_presets[new_preset_name.strip()] = current_visibility
                            # Save to file for persistence
                            save_column_presets(st.session_state.column_visibility_presets)
                            st.success(f"Preset '{new_preset_name.strip()}' saved!")
                            st.rerun()
                        else:
                            st.warning("Please enter a preset name")
                
                # Delete preset option
                if st.session_state.column_visibility_presets:
                    delete_col1, delete_col2 = st.columns([3, 1])
                    with delete_col1:
                        preset_to_delete = st.selectbox(
                            "Delete Preset",
                            ["None"] + list(st.session_state.column_visibility_presets.keys()),
                            key="delete_preset_selector"
                        )
                    with delete_col2:
                        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                        if st.button("🗑️ Delete", key="delete_preset", use_container_width=True):
                            if preset_to_delete != "None":
                                del st.session_state.column_visibility_presets[preset_to_delete]
                                # Save to file after deletion
                                save_column_presets(st.session_state.column_visibility_presets)
                                st.success(f"Preset '{preset_to_delete}' deleted!")
                                st.rerun()
                
                st.markdown("---")
                
                # Clear all and Select all buttons
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    if st.button("Clear all", key="clear_all_cols", use_container_width=True):
                        # Clear all column visibility settings for current columns
                        for col in all_available_cols:
                            st.session_state.column_visibility[col] = False
                        # Increment counter to force new widget keys (this resets widget state)
                        st.session_state.checkbox_key_counter += 1
                        st.rerun()
                with button_col2:
                    if st.button("Select all", key="select_all_cols", use_container_width=True):
                        # Select all column visibility settings for current columns
                        for col in all_available_cols:
                            st.session_state.column_visibility[col] = True
                        # Increment counter to force new widget keys (this resets widget state)
                        st.session_state.checkbox_key_counter += 1
                        st.rerun()
                
                col_vis_cols = st.columns(3)
                col_idx = 0
                for col in all_available_cols:
                    # Initialize to True if not set
                    if col not in st.session_state.column_visibility:
                        st.session_state.column_visibility[col] = True
                    
                    with col_vis_cols[col_idx % 3]:
                        # Get the current value from session state
                        current_value = st.session_state.column_visibility.get(col, True)
                        # Use counter in key to force widget reset when clearing
                        checkbox_key = f"col_vis_{col}_{st.session_state.checkbox_key_counter}"
                        # Use the checkbox value to update session state
                        checkbox_value = st.checkbox(
                            col, 
                            value=current_value,
                            key=checkbox_key
                        )
                        # Always update session state with checkbox value
                        st.session_state.column_visibility[col] = checkbox_value
                    col_idx += 1
                
                # Filter columns based on visibility
                visible_cols = [col for col in all_available_cols if st.session_state.column_visibility.get(col, True)]
                filtered_log = filtered_log[visible_cols]
        
            # Sort dropdown - adaptive to visible columns (after column visibility is determined)
            st.markdown("### Sort")
            sort_col1, sort_col2 = st.columns(2)
            with sort_col1:
                # Determine which columns are currently visible for sorting
                if view_mode == "Summary":
                    visible_for_sort = [col for col in summary_columns if col in filtered_log.columns]
                else:
                    # For Expanded, use the columns that are actually visible
                    visible_for_sort = list(filtered_log.columns)
                
                # Exclude text-heavy columns that don't make sense to sort
                sortable_columns = [col for col in visible_for_sort if col not in [
                    'Call Notes', 'Preparation Notes', 'How They View Themselves', 
                    'What Is Important To Them', 'Mindset Towards Growth', 'Agent Notes',
                    'Player Notes', 'Key Talking Points', 'Summary Notes', 'Red Flags',
                    'Action Items', 'Other Opportunities', 'Injury Periods', 
                    'Personality Traits', 'Other Traits', 'Agent Expectations',
                    'Agent Negotiation Style', 'How They Carry Themselves'
                ]]
                
                sort_options = ["None"] + sortable_columns
                
                # Get current sort column for dropdown default
                current_sort = st.session_state.table_sort_column if st.session_state.table_sort_column else "None"
                # Map back if needed
                reverse_column_map = {
                    'Percentile': 'Player Percentile',
                    'Assessment Score': 'Assessment Total Score',
                    'Agent': 'Agent Name',
                    'Follow-up': 'Follow-up Needed',
                    'Call No.': 'Call Number'
                }
                if current_sort in reverse_column_map:
                    current_sort = reverse_column_map[current_sort]
                if current_sort not in sort_options:
                    current_sort = "None"
                
                selected_sort_column = st.selectbox(
                    "Sort by",
                    sort_options,
                    index=sort_options.index(current_sort) if current_sort in sort_options else 0,
                    key="sort_by_dropdown"
                )
                
                # Map selected column to display name for table
                column_map = {
                    'Player Percentile': 'Percentile',
                    'Assessment Total Score': 'Assessment Score',
                    'Agent Name': 'Agent',
                    'Follow-up Needed': 'Follow-up',
                    'Call Number': 'Call No.'
                }
                if selected_sort_column != "None":
                    st.session_state.table_sort_column = column_map.get(selected_sort_column, selected_sort_column)
                else:
                    st.session_state.table_sort_column = None
            
            with sort_col2:
                # Sort direction dropdown
                if selected_sort_column != "None":
                    sort_direction = st.selectbox(
                        "Direction",
                        ["Ascending", "Descending"],
                        index=0 if st.session_state.table_sort_direction == "asc" else 1,
                        key="sort_direction_dropdown"
                    )
                    st.session_state.table_sort_direction = "asc" if sort_direction == "Ascending" else "desc"
            
            # Initialize sorting state
            if "table_sort_column" not in st.session_state:
                st.session_state.table_sort_column = None
            if "table_sort_direction" not in st.session_state:
                st.session_state.table_sort_direction = "asc"
        
        # Sorting is now handled in the Filters section (col5)
        
        # Initialize column order in session state
        if "column_order" not in st.session_state:
            st.session_state.column_order = list(filtered_log.columns)
        
        # Apply sorting if column is set (before resetting index)
        sorted_column = None
        if st.session_state.table_sort_column and st.session_state.table_sort_column in filtered_log.columns:
            sorted_column = st.session_state.table_sort_column
            ascending = st.session_state.table_sort_direction == "asc"
            try:
                # Try to sort as numeric first
                filtered_log[st.session_state.table_sort_column] = pd.to_numeric(filtered_log[st.session_state.table_sort_column], errors='ignore')
                filtered_log = filtered_log.sort_values(by=st.session_state.table_sort_column, ascending=ascending, na_position='last')
            except:
                # If numeric fails, sort as string
                filtered_log = filtered_log.sort_values(by=st.session_state.table_sort_column, ascending=ascending, na_position='last')
            
            # Move sorted column to leftmost position
            cols = list(filtered_log.columns)
            if sorted_column in cols:
                cols.remove(sorted_column)
                cols.insert(0, sorted_column)
                filtered_log = filtered_log[cols]
                # Update column order
                st.session_state.column_order = cols
        
        # Apply custom column order if it exists and matches current columns
        if "column_order" in st.session_state and len(st.session_state.column_order) == len(filtered_log.columns):
            # Only reorder if all columns match
            if set(st.session_state.column_order) == set(filtered_log.columns):
                # If sorted column exists, keep it first, then apply custom order for rest
                if sorted_column and sorted_column in st.session_state.column_order:
                    remaining_cols = [c for c in st.session_state.column_order if c != sorted_column]
                    new_order = [sorted_column] + remaining_cols
                else:
                    new_order = st.session_state.column_order
                # Only reorder if the order is different
                if new_order != list(filtered_log.columns):
                    filtered_log = filtered_log[new_order]
        
        # Reset index to start at 1 instead of 0
        filtered_log = filtered_log.reset_index(drop=True)
        filtered_log.index = filtered_log.index + 1
        filtered_log.index.name = None
        
        # Define text-heavy columns that should be expandable
        text_heavy_columns = [
            'Call Notes',
            'Preparation Notes',
            'How They View Themselves',
            'What Is Important To Them',
            'Mindset Towards Growth',
            'Agent Notes',
            'Player Notes',
            'Key Talking Points',
            'Summary Notes',
            'Red Flags',
            'Action Items',
            'Other Opportunities',
            'Injury Periods',
            'Personality Traits',
            'Other Traits',
            'Agent Expectations',
            'Agent Negotiation Style',
            'How They Carry Themselves'
        ]
        
        # Initialize session state for cell expansion
        if "expanded_cell_data" not in st.session_state:
            st.session_state.expanded_cell_data = None
        
        # Format date columns before creating table data
        if 'Call Date' in filtered_log.columns:
            try:
                filtered_log['Call Date'] = pd.to_datetime(filtered_log['Call Date'], errors='coerce')
                filtered_log['Call Date'] = filtered_log['Call Date'].dt.strftime('%Y-%m-%d')
            except:
                pass
        
        if 'Follow-up Date' in filtered_log.columns:
            try:
                filtered_log['Follow-up Date'] = pd.to_datetime(filtered_log['Follow-up Date'], errors='coerce')
                filtered_log['Follow-up Date'] = filtered_log['Follow-up Date'].dt.strftime('%Y-%m-%d')
            except:
                pass
        
        # Prepare data for custom HTML table
        # Convert dataframe to JSON for JavaScript
        table_data = filtered_log.to_dict('records')
        table_columns = list(filtered_log.columns)
        
        # Create truncation length
        truncate_length = 50
        
        # Build header row with sort indicator, highlighting, and drag-and-drop
        header_cells = []
        sorted_col = st.session_state.table_sort_column if st.session_state.table_sort_column else None
        for col in table_columns:
            sort_indicator = ""
            is_sorted = sorted_col == col
            highlight_style = ""
            if is_sorted:
                if st.session_state.table_sort_direction == "asc":
                    sort_indicator = " ▲"
                else:
                    sort_indicator = " ▼"
                highlight_style = 'style="background: linear-gradient(180deg, #D10023 0%, #8B0000 100%) !important; color: #ffffff !important; border-bottom: 2px solid #ffffff !important;"'
            
            drag_attr = 'draggable="true" ondragstart="handleDragStart(event)" ondragover="handleDragOver(event)" ondrop="handleDrop(event)" ondragend="handleDragEnd(event)"'
            
            if col == "Percentile":
                header_cells.append(f'<th {drag_attr} {highlight_style} data-col="{col}">{col} <span style="cursor: help; color: #8B0000; font-weight: bold; margin-left: 4px;" onclick="event.stopPropagation(); showPercentileHelp();" title="Click for help">?</span>{sort_indicator}</th>')
            else:
                header_cells.append(f'<th {drag_attr} {highlight_style} data-col="{col}">{col}{sort_indicator}</th>')
        header_row = ' '.join(header_cells)
        
        # Create HTML/JavaScript component for interactive table
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: transparent;
                    color: #fafafa;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}
                .table-wrapper {{
                    background: #1e1e1e;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                }}
                .table-container {{
                    overflow-x: auto;
                    max-height: 500px;
                    overflow-y: auto;
                    position: relative;
                }}
                .table-container::-webkit-scrollbar {{
                    width: 8px;
                    height: 8px;
                }}
                .table-container::-webkit-scrollbar-track {{
                    background: #1e1e1e;
                }}
                .table-container::-webkit-scrollbar-thumb {{
                    background: #3a3a3a;
                    border-radius: 4px;
                }}
                .table-container::-webkit-scrollbar-thumb:hover {{
                    background: #4a4a4a;
                }}
                table {{
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    background-color: transparent;
                    margin: 0;
                }}
                thead {{
                    position: sticky;
                    top: 0;
                    z-index: 100;
                }}
                th {{
                    background: linear-gradient(180deg, #2d2d2d 0%, #1e1e1e 100%);
                    color: #ffffff;
                    padding: 8px 12px;
                    text-align: left;
                    border-bottom: 2px solid #8B0000;
                    font-weight: 600;
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    white-space: nowrap;
                    position: relative;
                    transition: background-color 0.2s ease;
                    cursor: move;
                    user-select: none;
                }}
                th:hover {{
                    background: linear-gradient(180deg, #3a3a3a 0%, #2d2d2d 100%);
                }}
                th.dragging {{
                    opacity: 0.5;
                    background: linear-gradient(180deg, #D10023 0%, #8B0000 100%) !important;
                }}
                th.drag-over {{
                    border-left: 3px solid #D10023;
                }}
                th::after {{
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    height: 1px;
                    background: linear-gradient(90deg, transparent, #8B0000, transparent);
                }}
                td {{
                    padding: 8px 12px;
                    border-bottom: 1px solid rgba(58, 58, 58, 0.5);
                    max-width: 200px;
                    word-wrap: break-word;
                    font-size: 0.8125rem;
                    line-height: 1.4;
                    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                    color: #e0e0e0;
                    font-weight: 700 !important;
                }}
                tbody td {{
                    font-weight: 700 !important;
                }}
                tbody tr {{
                    background-color: #000000;
                    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                    border-left: 3px solid transparent;
                }}
                tbody tr:nth-child(even) {{
                    background-color: #2a2a2a;
                }}
                tbody tr:hover {{
                    background-color: rgba(139, 0, 0, 0.3) !important;
                    border-left-color: #8B0000;
                    transform: translateX(2px);
                }}
                tbody tr:last-child td {{
                    border-bottom: none;
                }}
                .expandable-cell {{
                    cursor: pointer;
                    color: #8B0000;
                    text-decoration: underline;
                    text-decoration-color: #8B0000;
                    text-underline-offset: 2px;
                    position: relative;
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                    font-weight: 600;
                    font-size: 0.875rem;
                }}
                .expandable-cell::before {{
                    content: '▶';
                    margin-right: 4px;
                    font-size: 0.75rem;
                    display: inline-block;
                    transition: transform 0.2s ease;
                }}
                .expandable-cell:hover {{
                    color: #D10023;
                    background-color: rgba(139, 0, 0, 0.2) !important;
                    text-decoration-color: #D10023;
                    transform: translateX(2px);
                }}
                .expandable-cell:hover::before {{
                    transform: translateX(2px);
                }}
                .modal {{
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.85);
                    backdrop-filter: blur(4px);
                    animation: fadeIn 0.2s ease;
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                .modal-content {{
                    background-color: #1e1e1e;
                    margin: 5% auto;
                    padding: 0;
                    border: none;
                    border-radius: 12px;
                    width: 80%;
                    max-width: 800px;
                    max-height: 80vh;
                    overflow: hidden;
                    color: #fafafa;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                    animation: slideDown 0.3s ease;
                }}
                @keyframes slideDown {{
                    from {{
                        transform: translateY(-20px);
                        opacity: 0;
                    }}
                    to {{
                        transform: translateY(0);
                        opacity: 1;
                    }}
                }}
                .modal-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px 24px;
                    border-bottom: 1px solid #3a3a3a;
                    background: linear-gradient(180deg, #2a2a2a 0%, #1e1e1e 100%);
                }}
                .modal-title {{
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #8B0000;
                    letter-spacing: 0.3px;
                }}
                .close {{
                    color: #aaa;
                    font-size: 24px;
                    font-weight: 300;
                    cursor: pointer;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    transition: all 0.2s ease;
                }}
                .close:hover {{
                    background-color: #3a3a3a;
                    color: #fafafa;
                }}
                .modal-body {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    line-height: 1.3;
                    padding: 24px;
                    background-color: #1e1e1e;
                    max-height: calc(80vh - 100px);
                    overflow-y: auto;
                }}
                .modal-body p {{
                    margin-bottom: 0.0rem;
                    margin-top: 0.0rem;
                }}
                .modal-body p:first-child {{
                    margin-top: 0;
                    margin-bottom: 0;
                }}
                .modal-body p:has(strong) {{
                    margin-bottom: 0;
                    margin-top: 0.0rem;
                }}
                .modal-body p:has(strong):first-child {{
                    margin-top: 0;
                }}
                .modal-body p:has(strong) + p {{
                    margin-top: 0.0rem;
                    margin-bottom: 0.0rem;
                }}
                .play-recording-btn {{
                    background-color: #8B0000;
                    color: #ffffff;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.75rem;
                    font-weight: 600;
                    transition: all 0.2s ease;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .play-recording-btn:hover {{
                    background-color: #A00000;
                    transform: scale(1.05);
                }}
                .modal-body audio, .modal-body video {{
                    width: 100%;
                    max-width: 100%;
                    margin-top: 16px;
                }}
                .modal-body ul, .modal-body ol {{
                    margin-top: 0.0rem;
                    margin-bottom: 0.0rem;
                }}
                .modal-body li {{
                    margin-bottom: 0.0rem;
                }}
                .modal-body ul ul {{
                    margin-top: 0.0rem;
                    margin-bottom: 0.0rem;
                }}
                .modal-body::-webkit-scrollbar {{
                    width: 1px;
                }}
                .modal-body::-webkit-scrollbar-track {{
                    background: #1e1e1e;
                }}
                .modal-body::-webkit-scrollbar-thumb {{
                    background: #3a3a3a;
                    border-radius: 1px;
                }}
                .modal-body::-webkit-scrollbar-thumb:hover {{
                    background: #4a4a4a;
                }}
            </style>
        </head>
        <body>
            <div class="table-wrapper">
                <div class="table-container">
                    <table id="dataTable">
                    <thead>
                        <tr>
                            {header_row}
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add table rows
        for row_idx, row in enumerate(table_data):
            html_code += "<tr>"
            for col in table_columns:
                raw_value = row.get(col, '')
                
                # Convert to string (dates are already formatted above)
                if pd.notna(raw_value):
                    cell_value = str(raw_value)
                else:
                    cell_value = ''
                
                # Special handling for Call Recording column
                if col == 'Call Recording' and cell_value and len(str(cell_value).strip()) > 0:
                    # Show play button for recordings
                    recording_path = str(cell_value).replace('\\', '/')
                    file_ext = Path(recording_path).suffix.lower() if recording_path else ''
                    is_audio = file_ext in ['.mp3', '.wav', '.m4a']
                    is_video = file_ext in ['.mp4', '.mov', '.avi']
                    if is_audio or is_video:
                        # Escape the path for JavaScript
                        escaped_path = recording_path.replace('\\', '/').replace("'", "\\'").replace('"', '\\"')
                        html_code += f'''
                    <td>
                        <button class="play-recording-btn" onclick="showRecordingModal('{escaped_path}', {str(is_audio).lower()})" title="Play recording">
                            ▶ Play
                        </button>
                    </td>
                    '''
                    else:
                        html_code += f"<td>-</td>"
                # Check if this column should be expandable
                elif col in text_heavy_columns and cell_value and len(str(cell_value).strip()) > 0:
                    # Escape quotes for JavaScript
                    escaped_value = str(cell_value).replace('"', '&quot;').replace("'", "&#39;").replace('\n', '\\n')
                    html_code += f'''
                    <td class="expandable-cell" 
                        onclick="showModal('{col}', `{escaped_value}`)"
                        title="Click to view full text">
                        Expand
                    </td>
                    '''
                else:
                    # Escape HTML
                    escaped_cell = str(cell_value).replace('<', '&lt;').replace('>', '&gt;')
                    html_code += f"<td>{escaped_cell}</td>"
            html_code += "</tr>"
        
        html_code += """
                    </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Modal for expanded text -->
            <div id="textModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <div class="modal-title" id="modalTitle"></div>
                        <span class="close" onclick="closeModal()">&times;</span>
                    </div>
                    <div class="modal-body" id="modalBody"></div>
                </div>
            </div>
            
            <!-- Modal for Percentile help -->
            <div id="percentileHelpModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <div class="modal-title">Percentile - Explanation</div>
                        <span class="close" onclick="closePercentileHelp()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <p><strong>What is Percentile?</strong></p>
                        <p>The Percentile metric shows how a player ranks compared to all other players spoken to by the club based on their assessment scores.</p>
                        <p><strong>How is it calculated?</strong></p>
                        <p>The percentile is calculated by:</p>
                        <ol>
                            <li>Calculating each player's average score across all 9 assessment metrics:
                                <ul>
                                    <li>Communication</li>
                                    <li>Maturity</li>
                                    <li>Coachability</li>
                                    <li>Leadership</li>
                                    <li>Work Ethic</li>
                                    <li>Confidence</li>
                                    <li>Tactical Knowledge</li>
                                    <li>Team Fit</li>
                                    <li>Overall Rating</li>
                                </ul>
                            </li>
                            <li>Ranking all players from highest to lowest average score</li>
                            <li>Calculating the percentile: (Rank / Total Players) × 100</li>
                        </ol>
                        <p><strong>Example:</strong> A percentile of 95.3 means the player ranks higher than 95.3% of all players spoken to by the club. Rank 1 (best player) = 100th percentile, while the lowest ranked player = 0th percentile.</p>
                        <p><strong>Note:</strong> Percentiles are recalculated automatically whenever new call logs are added, ensuring rankings stay current.</p>
                    </div>
                </div>
            </div>
            
            <!-- Modal for Call Recording -->
            <div id="recordingModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <div class="modal-title">Call Recording</div>
                        <span class="close" onclick="closeRecordingModal()">&times;</span>
                    </div>
                    <div class="modal-body" id="recordingModalBody">
                        <p>Loading recording...</p>
                    </div>
                </div>
            </div>
            
            <script>
                function showModal(columnName, fullText) {{
                    document.getElementById('modalTitle').textContent = columnName;
                    document.getElementById('modalBody').textContent = fullText;
                    document.getElementById('textModal').style.display = 'block';
                }}
                
                function closeModal() {{
                    document.getElementById('textModal').style.display = 'none';
                }}
                
                function showPercentileHelp() {{
                    document.getElementById('percentileHelpModal').style.display = 'block';
                }}
                
                function closePercentileHelp() {{
                    document.getElementById('percentileHelpModal').style.display = 'none';
                }}
                
                function showRecordingModal(recordingPath, isAudio) {{
                    const modalBody = document.getElementById('recordingModalBody');
                    // Show recording info - actual playback will be handled by Streamlit below the table
                    modalBody.innerHTML = `
                        <p style="color: #8B0000; font-weight: 600; margin-bottom: 12px;">Call Recording</p>
                        <p style="margin-bottom: 8px;"><strong>File:</strong> ${recordingPath.split('/').pop()}</p>
                        <p style="margin-bottom: 8px;"><strong>Type:</strong> ${isAudio ? 'Audio' : 'Video'}</p>
                        <p style="margin-top: 16px; color: #aaa; font-size: 0.9rem;">The recording player will appear below the table.</p>
                    `;
                    document.getElementById('recordingModal').style.display = 'block';
                }}
                
                function closeRecordingModal() {{
                    const modalBody = document.getElementById('recordingModalBody');
                    modalBody.innerHTML = '<p>Loading recording...</p>';
                    document.getElementById('recordingModal').style.display = 'none';
                }}
                
                // Close modal when clicking outside of it
                window.onclick = function(event) {{
                    const modal = document.getElementById('textModal');
                    const helpModal = document.getElementById('percentileHelpModal');
                    const recordingModal = document.getElementById('recordingModal');
                    if (event.target == modal) {{
                        closeModal();
                    }}
                    if (event.target == helpModal) {{
                        closePercentileHelp();
                    }}
                    if (event.target == recordingModal) {{
                        closeRecordingModal();
                    }}
                }}
                
                // Close modal with Escape key
                document.addEventListener('keydown', function(event) {{
                    if (event.key === 'Escape') {{
                        closeModal();
                        closePercentileHelp();
                    }}
                }});
                
                // Headers are no longer clickable - sorting is done via dropdown above
                
                // Drag and drop functionality for column reordering
                let draggedElement = null;
                let draggedIndex = null;
                
                function handleDragStart(e) {{
                    draggedElement = e.target;
                    draggedIndex = Array.from(e.target.parentNode.children).indexOf(e.target);
                    e.target.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/html', e.target.innerHTML);
                }}
                
                function handleDragOver(e) {{
                    if (e.preventDefault) {{
                        e.preventDefault();
                    }}
                    e.dataTransfer.dropEffect = 'move';
                    
                    const target = e.target.closest('th');
                    if (target && target !== draggedElement) {{
                        target.classList.add('drag-over');
                    }}
                    return false;
                }}
                
                function handleDragEnd(e) {{
                    e.target.classList.remove('dragging');
                    document.querySelectorAll('th').forEach(th => {{
                        th.classList.remove('drag-over');
                    }});
                }}
                
                function handleDrop(e) {{
                    if (e.stopPropagation) {{
                        e.stopPropagation();
                    }}
                    
                    const target = e.target.closest('th');
                    if (target && target !== draggedElement && draggedElement) {{
                        const targetIndex = Array.from(target.parentNode.children).indexOf(target);
                        const thead = target.parentNode;
                        const tbody = document.querySelector('tbody');
                        
                        // Reorder header cells
                        if (draggedIndex < targetIndex) {{
                            thead.insertBefore(draggedElement, target.nextSibling);
                        }} else {{
                            thead.insertBefore(draggedElement, target);
                        }}
                        
                        // Reorder data columns in all rows
                        const rows = tbody.querySelectorAll('tr');
                        rows.forEach(row => {{
                            const cells = Array.from(row.children);
                            const draggedCell = cells[draggedIndex];
                            const targetCell = cells[targetIndex];
                            
                            if (draggedIndex < targetIndex) {{
                                row.insertBefore(draggedCell, targetCell.nextSibling);
                            }} else {{
                                row.insertBefore(draggedCell, targetCell);
                            }}
                        }});
                        
                        // Update draggedIndex for next drag
                        draggedIndex = targetIndex;
                        
                        // Get new column order - extract column name from data-col attribute or text
                        const newOrder = Array.from(thead.querySelectorAll('th')).map(th => {{
                            let colName = th.getAttribute('data-col');
                            if (!colName) {{
                                // Extract column name from text (remove sort indicators and help icons)
                                colName = th.textContent.trim()
                                    .replace(/[▲▼]/g, '')
                                    .replace(/[?]/g, '')
                                    .trim()
                                    .split(' ')[0];
                            }}
                            return colName;
                        }});
                        
                        // Store in localStorage for persistence across reruns
                        try {{
                            localStorage.setItem('columnOrder', JSON.stringify(newOrder));
                        }} catch(e) {{
                            console.log('Could not save column order:', e);
                        }}
                        
                        // Trigger Streamlit rerun by posting message (if parent supports it)
                        if (window.parent && window.parent.postMessage) {{
                            window.parent.postMessage({{
                                type: 'streamlit:setComponentValue',
                                value: JSON.stringify({{'columnOrder': newOrder}})
                            }}, '*');
                        }}
                    }}
                    
                    target.classList.remove('drag-over');
                    return false;
                }}
                
                // Listen for messages from parent (Streamlit)
                window.addEventListener('message', function(event) {{
                    if (event.data && event.data.type === 'columnReorder') {{
                        // Column order updated
                        console.log('Column order updated:', event.data.columns);
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Display the custom HTML table
        components.html(html_code, height=550, scrolling=True)
        
        # Display call recordings below the table (only if column exists)
        if 'Call Recording' in filtered_log.columns:
            recordings_in_view = filtered_log[filtered_log['Call Recording'].notna() & (filtered_log['Call Recording'] != '')]
        else:
            recordings_in_view = pd.DataFrame()
        
        if not recordings_in_view.empty:
            st.markdown("---")
            st.markdown("### Call Recordings")
            for idx, row in recordings_in_view.iterrows():
                recording_path = row.get('Call Recording', '')
                if recording_path and Path(recording_path).exists():
                    player_name = row.get('Player Name', 'Unknown')
                    call_date = row.get('Call Date', '')
                    with st.expander(f"Recording: {player_name} - {call_date}"):
                        try:
                            recording_file = Path(recording_path)
                            file_ext = recording_file.suffix.lower()
                            with open(recording_file, 'rb') as f:
                                recording_bytes = f.read()
                            if file_ext in ['.mp3', '.wav', '.m4a']:
                                st.audio(recording_bytes)
                            elif file_ext in ['.mp4', '.mov', '.avi']:
                                st.video(recording_bytes)
                            else:
                                st.info(f"Recording file: {recording_file.name}")
                        except Exception as e:
                            st.error(f"Error loading recording: {e}")
        
        st.download_button(
            "Download Filtered Data (CSV)",
            filtered_log.to_csv(index=False),
            file_name=f"call_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with tab3:
        st.subheader("Player Call Rankings")
        st.markdown("Rankings are based on assessment scores from all call logs and update automatically when new calls are added.")
        
        # Refresh call log from file to ensure we have latest data
        st.session_state.call_log = load_call_log()
    
        if st.session_state.call_log.empty:
            st.info("No call logs yet. Log some calls to see player rankings!")
        else:
            # Calculate player rankings based on assessment scores
            def calculate_player_rankings(call_log_df):
                """Calculate percentile-based rankings for all players."""
                # Group by player and calculate average assessment metrics
                player_stats = []
                
                for player_name in call_log_df['Player Name'].unique():
                    player_calls = call_log_df[call_log_df['Player Name'] == player_name]
                    
                    # Calculate averages for all assessment metrics
                    avg_communication = player_calls['Communication'].mean()
                    avg_maturity = player_calls['Maturity'].mean()
                    avg_coachability = player_calls['Coachability'].mean()
                    avg_leadership = player_calls['Leadership'].mean()
                    avg_work_ethic = player_calls['Work Ethic'].mean()
                    avg_confidence = player_calls['Confidence'].mean()
                    avg_tactical_knowledge = player_calls['Tactical Knowledge'].mean()
                    avg_team_fit = player_calls['Team Fit'].mean()
                    avg_overall_rating = player_calls['Overall Rating'].mean()
                    
                    # Calculate overall average assessment score
                    overall_avg = (
                        avg_communication + avg_maturity + avg_coachability + 
                        avg_leadership + avg_work_ethic + avg_confidence + 
                        avg_tactical_knowledge + avg_team_fit + avg_overall_rating
                    ) / 9
                    
                    # Get latest recommendation
                    latest_recommendation = player_calls.iloc[-1]['Recommendation'] if len(player_calls) > 0 else 'Unknown'
                    
                    # Get team and conference (from most recent call)
                    latest_team = player_calls.iloc[-1].get('Team', '') if len(player_calls) > 0 else ''
                    latest_conference = player_calls.iloc[-1].get('Conference', '') if len(player_calls) > 0 else ''
                    latest_position = player_calls.iloc[-1].get('Position Profile', '') if len(player_calls) > 0 else ''
                    
                    player_stats.append({
                        'Player Name': player_name,
                        'Team': latest_team,
                        'Conference': latest_conference,
                        'Position': latest_position,
                        'Total Calls': len(player_calls),
                        'Avg Communication': round(avg_communication, 2),
                        'Avg Maturity': round(avg_maturity, 2),
                        'Avg Coachability': round(avg_coachability, 2),
                        'Avg Leadership': round(avg_leadership, 2),
                        'Avg Work Ethic': round(avg_work_ethic, 2),
                        'Avg Confidence': round(avg_confidence, 2),
                        'Avg Tactical Knowledge': round(avg_tactical_knowledge, 2),
                        'Avg Team Fit': round(avg_team_fit, 2),
                        'Avg Overall Rating': round(avg_overall_rating, 2),
                        'Overall Average Score': round(overall_avg, 2),
                        'Latest Recommendation': latest_recommendation,
                        'Last Call Date': player_calls['Call Date'].max() if len(player_calls) > 0 else ''
                    })
                
                # Convert to DataFrame
                rankings_df = pd.DataFrame(player_stats)
                
                # Calculate percentile ranks
                rankings_df['Percentile Rank'] = rankings_df['Overall Average Score'].rank(pct=True) * 100
                rankings_df['Percentile Rank'] = rankings_df['Percentile Rank'].round(1)
                
                # Sort by overall average score (descending)
                rankings_df = rankings_df.sort_values('Overall Average Score', ascending=False)
                
                # Add rank number
                rankings_df['Rank'] = range(1, len(rankings_df) + 1)
                
                # Reorder columns
                cols = ['Rank', 'Player Name', 'Team', 'Conference', 'Position', 'Total Calls', 
                       'Overall Average Score', 'Percentile Rank', 'Latest Recommendation', 'Last Call Date',
                       'Avg Communication', 'Avg Maturity', 'Avg Coachability', 'Avg Leadership',
                       'Avg Work Ethic', 'Avg Confidence', 'Avg Tactical Knowledge', 'Avg Team Fit', 'Avg Overall Rating']
                rankings_df = rankings_df[cols]
                
                return rankings_df
            
            # Calculate rankings
            rankings_df = calculate_player_rankings(st.session_state.call_log)
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Players Ranked", len(rankings_df))
            with col2:
                st.metric("Top 10% Players", len(rankings_df[rankings_df['Percentile Rank'] >= 90]))
            with col3:
                st.metric("Top 25% Players", len(rankings_df[rankings_df['Percentile Rank'] >= 75]))
            with col4:
                avg_score = rankings_df['Overall Average Score'].mean()
                st.metric("Average Score", f"{avg_score:.1f}")
            
            st.markdown("---")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_conference = st.selectbox("Filter by Conference", [""] + sorted(rankings_df['Conference'].dropna().unique().tolist()))
            with col2:
                filter_position = st.selectbox("Filter by Position", [""] + sorted(rankings_df['Position'].dropna().unique().tolist()))
            with col3:
                percentile_filter = st.selectbox("Filter by Percentile", ["All", "Top 10%", "Top 25%", "Top 50%", "Bottom 50%"])
            
            # Apply filters
            filtered_rankings = rankings_df.copy()
            if filter_conference:
                filtered_rankings = filtered_rankings[filtered_rankings['Conference'] == filter_conference]
            if filter_position:
                filtered_rankings = filtered_rankings[filtered_rankings['Position'] == filter_position]
            if percentile_filter == "Top 10%":
                filtered_rankings = filtered_rankings[filtered_rankings['Percentile Rank'] >= 90]
            elif percentile_filter == "Top 25%":
                filtered_rankings = filtered_rankings[filtered_rankings['Percentile Rank'] >= 75]
            elif percentile_filter == "Top 50%":
                filtered_rankings = filtered_rankings[filtered_rankings['Percentile Rank'] >= 50]
            elif percentile_filter == "Bottom 50%":
                filtered_rankings = filtered_rankings[filtered_rankings['Percentile Rank'] < 50]
            
            # Display rankings table using HTML-based style (same as Call History)
            st.subheader("Player Rankings")
            
            # Reset index to start at 1 instead of 0
            display_rankings = filtered_rankings.reset_index(drop=True)
            display_rankings.index = display_rankings.index + 1
            display_rankings.index.name = None
            
            # Prepare data for custom HTML table
            table_data = display_rankings.to_dict('records')
            table_columns = list(display_rankings.columns)
            
            # Build header row
            header_cells = []
            for col in table_columns:
                header_cells.append(f'<th>{col}</th>')
            header_row = ' '.join(header_cells)
            
            # Create HTML/JavaScript component for interactive table (same style as Call History)
            html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: transparent;
                        color: #fafafa;
                        -webkit-font-smoothing: antialiased;
                        -moz-osx-font-smoothing: grayscale;
                    }}
                    .table-wrapper {{
                        background: #1e1e1e;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                    }}
                    .table-container {{
                        overflow-x: auto;
                        max-height: 500px;
                        overflow-y: auto;
                        position: relative;
                    }}
                    .table-container::-webkit-scrollbar {{
                        width: 8px;
                        height: 8px;
                    }}
                    .table-container::-webkit-scrollbar-track {{
                        background: #1e1e1e;
                    }}
                    .table-container::-webkit-scrollbar-thumb {{
                        background: #3a3a3a;
                        border-radius: 4px;
                    }}
                    .table-container::-webkit-scrollbar-thumb:hover {{
                        background: #4a4a4a;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: separate;
                        border-spacing: 0;
                        background-color: transparent;
                        margin: 0;
                    }}
                    thead {{
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }}
                    th {{
                        background: linear-gradient(180deg, #2d2d2d 0%, #1e1e1e 100%);
                        color: #ffffff;
                        padding: 8px 12px;
                        text-align: left;
                        border-bottom: 2px solid #8B0000;
                        font-weight: 600;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        white-space: nowrap;
                        position: relative;
                        transition: background-color 0.2s ease;
                    }}
                    th:hover {{
                        background: linear-gradient(180deg, #3a3a3a 0%, #2d2d2d 100%);
                    }}
                    th::after {{
                        content: '';
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        right: 0;
                        height: 1px;
                        background: linear-gradient(90deg, transparent, #8B0000, transparent);
                    }}
                    td {{
                        padding: 8px 12px;
                        border-bottom: 1px solid rgba(58, 58, 58, 0.5);
                        max-width: 200px;
                        word-wrap: break-word;
                        font-size: 0.8125rem;
                        line-height: 1.4;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                        color: #e0e0e0;
                        font-weight: 700 !important;
                    }}
                    tbody td {{
                        font-weight: 700 !important;
                    }}
                    tbody tr {{
                        background-color: #000000;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                        border-left: 3px solid transparent;
                    }}
                    tbody tr:nth-child(even) {{
                        background-color: #2a2a2a;
                    }}
                    tbody tr:hover {{
                        background-color: rgba(139, 0, 0, 0.3) !important;
                        border-left-color: #8B0000;
                        transform: translateX(2px);
                    }}
                    tbody tr:last-child td {{
                        border-bottom: none;
                    }}
                </style>
            </head>
            <body>
                <div class="table-wrapper">
                    <div class="table-container">
                        <table id="dataTable">
                        <thead>
                            <tr>
                                {header_row}
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add table rows
            for row_idx, row in enumerate(table_data):
                html_code += "<tr>"
                for col in table_columns:
                    raw_value = row.get(col, '')
                    
                    # Convert to string
                    if pd.notna(raw_value):
                        cell_value = str(raw_value)
                    else:
                        cell_value = ''
                    
                    # Escape HTML
                    escaped_cell = str(cell_value).replace('<', '&lt;').replace('>', '&gt;')
                    html_code += f"<td>{escaped_cell}</td>"
                html_code += "</tr>"
            
            html_code += """
                        </tbody>
                        </table>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Display the HTML table
            components.html(html_code, height=550, scrolling=True)
            
            # Download button
            st.download_button(
                "Download Rankings (CSV)",
                filtered_rankings.to_csv(index=False),
                file_name=f"player_rankings_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Show percentile distribution
            st.markdown("---")
            st.subheader("Percentile Distribution")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top Performers by Percentile:**")
                percentile_ranges = [
                    ("Top 1%", 99, 100),
                    ("Top 5%", 95, 99),
                    ("Top 10%", 90, 95),
                    ("Top 25%", 75, 90),
                    ("Top 50%", 50, 75),
                    ("Bottom 50%", 0, 50)
                ]
                
                for label, min_pct, max_pct in percentile_ranges:
                    count = len(rankings_df[(rankings_df['Percentile Rank'] >= min_pct) & (rankings_df['Percentile Rank'] < max_pct)])
                    if count > 0:
                        st.write(f"- **{label}**: {count} players")
            
            with col2:
                st.markdown("**Recommendation Distribution:**")
                rec_counts = rankings_df['Latest Recommendation'].value_counts()
                for rec, count in rec_counts.items():
                    st.write(f"- **{rec}**: {count} players")

elif page == "Player Summary":
        st.header("Player Summary")
    
        # Refresh call log from file to ensure we have latest data
        st.session_state.call_log = load_call_log()
        
        # Load video reviews
        video_reviews_file = DATA_DIR / 'video_reviews.csv'
        if 'video_reviews' not in st.session_state:
            st.session_state.video_reviews = pd.DataFrame()
        if video_reviews_file.exists() and st.session_state.video_reviews.empty:
            try:
                st.session_state.video_reviews = pd.read_csv(video_reviews_file)
            except:
                pass
        
        # Get all unique players from both call logs and video reviews
        all_players = set()
        if not st.session_state.call_log.empty and 'Player Name' in st.session_state.call_log.columns:
            all_players.update(st.session_state.call_log['Player Name'].unique().tolist())
        if not st.session_state.video_reviews.empty and 'Player Name' in st.session_state.video_reviews.columns:
            all_players.update(st.session_state.video_reviews['Player Name'].unique().tolist())
        
        if not all_players:
            st.info("No call logs or video reviews yet.")
            selected_player = None
        else:
            selected_player = st.selectbox("Select Player", sorted(list(all_players)))
        
        if selected_player:
            # Filter call logs for selected player
            if not st.session_state.call_log.empty and 'Player Name' in st.session_state.call_log.columns:
                player_calls = st.session_state.call_log[st.session_state.call_log['Player Name'] == selected_player]
            else:
                player_calls = pd.DataFrame()
            
            # Filter video reviews for selected player
            if not st.session_state.video_reviews.empty and 'Player Name' in st.session_state.video_reviews.columns:
                player_video_reviews = st.session_state.video_reviews[st.session_state.video_reviews['Player Name'] == selected_player]
            else:
                player_video_reviews = pd.DataFrame()
            
            # Calculate player's ranking
            def get_player_ranking(player_name, call_log_df):
                """Get a player's rank and percentile."""
                all_players = call_log_df['Player Name'].unique()
                player_scores = []
                
                for p in all_players:
                    p_calls = call_log_df[call_log_df['Player Name'] == p]
                    avg_score = (
                        p_calls['Communication'].mean() + p_calls['Maturity'].mean() + 
                        p_calls['Coachability'].mean() + p_calls['Leadership'].mean() + 
                        p_calls['Work Ethic'].mean() + p_calls['Confidence'].mean() + 
                        p_calls['Tactical Knowledge'].mean() + p_calls['Team Fit'].mean() + 
                        p_calls['Overall Rating'].mean()
                    ) / 9
                    player_scores.append({'player': p, 'score': avg_score})
                
                scores_df = pd.DataFrame(player_scores)
                scores_df = scores_df.sort_values('score', ascending=False)
                scores_df['rank'] = range(1, len(scores_df) + 1)
                
                # Fix percentile calculation: rank 1 (best) should be 100th percentile, rank N (worst) should be lowest
                # Formula: percentile = ((total - rank) / (total - 1)) * 100
                # This gives: rank 1 = 100th percentile, rank N = 0th percentile
                total = len(scores_df)
                if total > 1:
                    scores_df['percentile'] = ((total - scores_df['rank']) / (total - 1) * 100).round(1)
                else:
                    scores_df['percentile'] = 100.0  # If only one player, they're 100th percentile
                
                player_row = scores_df[scores_df['player'] == player_name]
                if not player_row.empty:
                    return int(player_row.iloc[0]['rank']), float(player_row.iloc[0]['percentile']), len(scores_df)
                return None, None, len(scores_df)
            
            # Calculate player ranking (only if we have call logs)
            if not player_calls.empty:
                player_rank, player_percentile, total_players = get_player_ranking(selected_player, st.session_state.call_log)
            else:
                player_rank, player_percentile, total_players = None, None, 0
            
            st.subheader(f"Summary for {selected_player}")
            
            # ========== PHONE CALL SECTION ==========
            st.markdown("## 📞 Phone Call")
            
            # Phone Call Summary Metrics
            phone_col1, phone_col2, phone_col3, phone_col4 = st.columns(4)
            with phone_col1:
                st.metric("Total Calls", len(player_calls))
            with phone_col2:
                if not player_calls.empty and 'Overall Rating' in player_calls.columns:
                    avg_rating = player_calls['Overall Rating'].mean()
                    st.metric("Avg Overall Rating", f"{avg_rating:.1f}/10")
                else:
                    st.metric("Avg Overall Rating", "N/A")
            with phone_col3:
                if player_rank:
                    st.metric("Overall Rank", f"#{player_rank} of {total_players}")
                else:
                    st.metric("Overall Rank", "N/A")
            with phone_col4:
                if not player_calls.empty and 'Recommendation' in player_calls.columns:
                    latest_recommendation = player_calls.iloc[-1]['Recommendation']
                    st.metric("Latest Recommendation", latest_recommendation)
                else:
                    st.metric("Latest Recommendation", "N/A")
            
            if not player_calls.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### Average Ratings")
                rating_cols = ['Communication', 'Maturity', 'Coachability', 'Leadership', 'Work Ethic', 'Confidence', 'Tactical Knowledge', 'Team Fit']
                # Filter to only include columns that exist in the dataframe
                rating_cols = [col for col in rating_cols if col in player_calls.columns]
                if rating_cols:
                    avg_ratings = player_calls[rating_cols].mean()
                    # Create bar chart with Portland Red color (#8B0000) using Altair
                    import altair as alt
                    
                    chart_data = pd.DataFrame({
                        'Metric': avg_ratings.index,
                        'Average Rating': avg_ratings.values
                    })
                    
                    chart = alt.Chart(chart_data).mark_bar(
                        color='#8B0000',  # Portland Red
                        cornerRadiusTopLeft=4,
                        cornerRadiusTopRight=4
                    ).encode(
                        x=alt.X('Metric', axis=alt.Axis(labelAngle=0, labelColor='white', title=None)),
                        y=alt.Y('Average Rating', axis=alt.Axis(labelColor='white', titleColor='white'), scale=alt.Scale(domain=[0, 10], padding=0.15)),
                        tooltip=['Metric', 'Average Rating']
                    ).properties(
                        width=600,
                        height=450,
                        padding={'top': 50, 'bottom': 40, 'left': 40, 'right': 40}
                    ).configure(
                        background='#1e1e1e',
                        view=alt.ViewConfig(stroke=None)
                    ).configure_axis(
                        gridColor='#4a4a4a',  # More subtle gray instead of white
                        domainColor='#8B0000',
                        gridOpacity=0.4
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No phone call data available for this player.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # All Calls Table
            if not player_calls.empty:
                st.markdown("### All Calls")
                
                # Format date columns before creating table data
                player_calls_display = player_calls.copy()
                if 'Call Date' in player_calls_display.columns:
                    try:
                        player_calls_display['Call Date'] = pd.to_datetime(player_calls_display['Call Date'], errors='coerce')
                        player_calls_display['Call Date'] = player_calls_display['Call Date'].dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                if 'Follow-up Date' in player_calls_display.columns:
                    try:
                        player_calls_display['Follow-up Date'] = pd.to_datetime(player_calls_display['Follow-up Date'], errors='coerce')
                        player_calls_display['Follow-up Date'] = player_calls_display['Follow-up Date'].dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                # Define text-heavy columns that should be expandable
                text_heavy_columns = [
                    'Call Notes',
                    'Preparation Notes',
                    'How They View Themselves',
                    'What Is Important To Them',
                    'Mindset Towards Growth',
                    'Agent Notes',
                    'Player Notes',
                    'Key Talking Points',
                    'Summary Notes',
                    'Red Flags',
                    'Action Items',
                    'Other Opportunities',
                    'Injury Periods',
                    'Personality Traits',
                    'Other Traits',
                    'Agent Expectations',
                    'Agent Negotiation Style',
                    'How They Carry Themselves'
                ]
                
                # Prepare data for custom HTML table
                table_data = player_calls_display.to_dict('records')
                table_columns = list(player_calls_display.columns)
                
                # Build header row
                header_cells = []
                for col in table_columns:
                    header_cells.append(f'<th>{col}</th>')
                header_row = ' '.join(header_cells)
                
                # Create HTML/JavaScript component for interactive table
                html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: transparent;
                        color: #fafafa;
                        -webkit-font-smoothing: antialiased;
                        -moz-osx-font-smoothing: grayscale;
                    }}
                    .table-wrapper {{
                        background: #1e1e1e;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                        margin-bottom: 0 !important;
                        padding-bottom: 0 !important;
                    }}
                    .table-container {{
                        overflow-x: auto;
                        max-height: 500px;
                        overflow-y: auto;
                        position: relative;
                    }}
                    .table-container::-webkit-scrollbar {{
                        width: 8px;
                        height: 8px;
                    }}
                    .table-container::-webkit-scrollbar-track {{
                        background: #1e1e1e;
                    }}
                    .table-container::-webkit-scrollbar-thumb {{
                        background: #3a3a3a;
                        border-radius: 4px;
                    }}
                    .table-container::-webkit-scrollbar-thumb:hover {{
                        background: #4a4a4a;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: separate;
                        border-spacing: 0;
                        background-color: transparent;
                        margin: 0;
                    }}
                    thead {{
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }}
                    th {{
                        background: linear-gradient(180deg, #2d2d2d 0%, #1e1e1e 100%);
                        color: #ffffff;
                        padding: 8px 12px;
                        text-align: left;
                        border-bottom: 2px solid #8B0000;
                        font-weight: 600;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        white-space: nowrap;
                        position: relative;
                        transition: background-color 0.2s ease;
                    }}
                    th:hover {{
                        background: linear-gradient(180deg, #3a3a3a 0%, #2d2d2d 100%);
                    }}
                    th::after {{
                        content: '';
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        right: 0;
                        height: 1px;
                        background: linear-gradient(90deg, transparent, #8B0000, transparent);
                    }}
                    td {{
                        padding: 8px 12px;
                        border-bottom: 1px solid rgba(58, 58, 58, 0.5);
                        max-width: 200px;
                        word-wrap: break-word;
                        font-size: 0.8125rem;
                        line-height: 1.4;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                        color: #e0e0e0;
                        font-weight: 700 !important;
                    }}
                    tbody td {{
                        font-weight: 700 !important;
                    }}
                    tbody tr {{
                        background-color: #000000;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                        border-left: 3px solid transparent;
                    }}
                    tbody tr:nth-child(even) {{
                        background-color: #2a2a2a;
                    }}
                    tbody tr:hover {{
                        background-color: rgba(139, 0, 0, 0.3) !important;
                        border-left-color: #8B0000;
                        transform: translateX(2px);
                    }}
                    tbody tr:last-child td {{
                        border-bottom: none;
                    }}
                    .expandable-cell {{
                        cursor: pointer;
                        color: #8B0000;
                        text-decoration: underline;
                        text-decoration-color: #8B0000;
                        text-underline-offset: 2px;
                        position: relative;
                        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                        font-weight: 600;
                        font-size: 0.875rem;
                    }}
                    .expandable-cell::before {{
                        content: '▶';
                        margin-right: 4px;
                        font-size: 0.75rem;
                        display: inline-block;
                        transition: transform 0.2s ease;
                    }}
                    .expandable-cell:hover {{
                        color: #D10023;
                        background-color: rgba(139, 0, 0, 0.2) !important;
                        text-decoration-color: #D10023;
                        transform: translateX(2px);
                    }}
                    .expandable-cell:hover::before {{
                        transform: translateX(2px);
                    }}
                    .modal {{
                        display: none;
                        position: fixed;
                        z-index: 1000;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0,0,0,0.85);
                        backdrop-filter: blur(4px);
                        animation: fadeIn 0.2s ease;
                    }}
                    @keyframes fadeIn {{
                        from {{ opacity: 0; }}
                        to {{ opacity: 1; }}
                    }}
                    .modal-content {{
                        background-color: #1e1e1e;
                        margin: 5% auto;
                        padding: 0;
                        border: none;
                        border-radius: 12px;
                        width: 80%;
                        max-width: 800px;
                        max-height: 80vh;
                        overflow: hidden;
                        color: #fafafa;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                        animation: slideDown 0.3s ease;
                    }}
                    @keyframes slideDown {{
                        from {{
                            transform: translateY(-20px);
                            opacity: 0;
                        }}
                        to {{
                            transform: translateY(0);
                            opacity: 1;
                        }}
                    }}
                    .modal-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 20px 24px;
                        border-bottom: 1px solid #3a3a3a;
                        background: linear-gradient(180deg, #2a2a2a 0%, #1e1e1e 100%);
                    }}
                    .modal-title {{
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: #8B0000;
                        letter-spacing: 0.3px;
                    }}
                    .close {{
                        color: #aaa;
                        font-size: 24px;
                        font-weight: 300;
                        cursor: pointer;
                        width: 32px;
                        height: 32px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 50%;
                        transition: all 0.2s ease;
                    }}
                    .close:hover {{
                        background-color: #3a3a3a;
                        color: #fafafa;
                    }}
                    .modal-body {{
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        line-height: 1.3;
                        padding: 24px;
                        background-color: #1e1e1e;
                        max-height: calc(80vh - 100px);
                        overflow-y: auto;
                    }}
                    .modal-body::-webkit-scrollbar {{
                        width: 1px;
                    }}
                    .modal-body::-webkit-scrollbar-track {{
                        background: #1e1e1e;
                    }}
                    .modal-body::-webkit-scrollbar-thumb {{
                        background: #3a3a3a;
                        border-radius: 1px;
                    }}
                    .modal-body::-webkit-scrollbar-thumb:hover {{
                        background: #4a4a4a;
                    }}
                </style>
            </head>
            <body>
                <div class="table-wrapper">
                    <div class="table-container">
                        <table id="dataTable">
                        <thead>
                            <tr>
                                {header_row}
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add table rows
            for row_idx, row in enumerate(table_data):
                html_code += "<tr>"
                for col in table_columns:
                        raw_value = row.get(col, '')
                        
                        # Convert to string (dates are already formatted above)
                        if pd.notna(raw_value):
                            cell_value = str(raw_value)
                        else:
                            cell_value = ''
                        
                        # Check if this column should be expandable
                        if col in text_heavy_columns and cell_value and len(str(cell_value).strip()) > 0:
                            # Escape quotes for JavaScript
                            escaped_value = str(cell_value).replace('"', '&quot;').replace("'", "&#39;").replace('\n', '\\n')
                            html_code += f'''
                            <td class="expandable-cell" 
                                onclick="showModal('{col}', `{escaped_value}`)"
                                title="Click to view full text">
                                Expand
                            </td>
                            '''
                        else:
                            # Escape HTML
                            escaped_cell = str(cell_value).replace('<', '&lt;').replace('>', '&gt;')
                            html_code += f"<td>{escaped_cell}</td>"
                html_code += "</tr>"
            
            html_code += """
                        </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Modal for expanded text -->
                <div id="textModal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <div class="modal-title" id="modalTitle"></div>
                            <span class="close" onclick="closeModal()">&times;</span>
                        </div>
                        <div class="modal-body" id="modalBody"></div>
                    </div>
                </div>
                
                <script>
                    function showModal(columnName, fullText) {{
                        document.getElementById('modalTitle').textContent = columnName;
                        document.getElementById('modalBody').textContent = fullText;
                        document.getElementById('textModal').style.display = 'block';
                    }}
                    
                    function closeModal() {{
                        document.getElementById('textModal').style.display = 'none';
                    }}
                    
                    // Close modal when clicking outside of it
                    window.onclick = function(event) {{
                        const modal = document.getElementById('textModal');
                        if (event.target == modal) {{
                            closeModal();
                        }}
                    }}
                    
                    // Close modal with Escape key
                    document.addEventListener('keydown', function(event) {{
                        if (event.key === 'Escape') {{
                            closeModal();
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            
            # Display the custom HTML table with aggressive spacing reduction
            st.markdown("""
                <style>
                    /* Very aggressive negative margins for iframe container */
                    div[data-testid="stIFrame"] {
                        margin-bottom: -5rem !important;
                        padding-bottom: 0 !important;
                    }
                    /* Target element-container wrapper */
                    .element-container:has([data-testid="stIFrame"]) {
                        margin-bottom: -5rem !important;
                        padding-bottom: 0 !important;
                    }
                    /* Target block container div */
                    .block-container > div:has([data-testid="stIFrame"]) {
                        margin-bottom: -5rem !important;
                        padding-bottom: 0 !important;
                    }
                    /* Target divider container with negative margins */
                    .block-container > div:has(hr) {
                        margin-top: -4rem !important;
                        margin-bottom: -3rem !important;
                        padding: 0 !important;
                    }
                    /* Target radar chart section */
                    .block-container > div:has(hr) + div {
                        margin-top: -3rem !important;
                        padding-top: 0 !important;
                    }
                    /* Target all divs between iframe and radar chart */
                    .block-container > div:has([data-testid="stIFrame"]) ~ div {
                        margin-top: -2rem !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            components.html(html_code, height=550, scrolling=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Call Review Details
            if not player_calls.empty:
                st.markdown("### Call Review Details")
                for idx, row in player_calls.iterrows():
                    call_date = row.get('Call Date', 'N/A')
                    call_number = row.get('Call Number', 'N/A')
                    call_type = row.get('Call Type', 'N/A')
                    with st.expander(f"Call #{call_number} - {call_date} ({call_type})"):
                        col_c1, col_c2 = st.columns(2)
                        with col_c1:
                            if 'Overall Rating' in row:
                                st.metric("Overall Rating", f"{row.get('Overall Rating', 'N/A')}/10")
                            if 'Assessment Grade' in row:
                                st.metric("Grade", row.get('Assessment Grade', 'N/A'))
                            if 'Recommendation' in row:
                                st.metric("Recommendation", row.get('Recommendation', 'N/A'))
                        with col_c2:
                            if 'Call Type' in row:
                                st.metric("Call Type", row.get('Call Type', 'N/A'))
                            if 'Agent Name' in row:
                                st.metric("Agent", row.get('Agent Name', 'N/A'))
                            if 'Interest Level' in row:
                                st.metric("Interest Level", row.get('Interest Level', 'N/A'))
                        
                        # Performance metrics
                        call_metrics = ['Communication', 'Maturity', 'Coachability', 'Leadership', 
                                      'Work Ethic', 'Confidence', 'Tactical Knowledge', 'Team Fit', 'Overall Rating']
                        call_metrics_data = {metric: row.get(metric, 'N/A') for metric in call_metrics if metric in row}
                        if call_metrics_data:
                            st.markdown("**Performance Metrics:**")
                            call_metrics_df = pd.DataFrame([call_metrics_data])
                            st.dataframe(call_metrics_df.T, use_container_width=True, hide_index=False)
                        
                        # Call details
                        if row.get('Call Notes'):
                            st.markdown("**Call Notes:**")
                            st.info(row.get('Call Notes', ''))
                        if row.get('Preparation Notes'):
                            st.markdown("**Preparation Notes:**")
                            st.text(row.get('Preparation Notes', ''))
                        if row.get('Summary Notes'):
                            st.markdown("**Summary Notes:**")
                            st.text(row.get('Summary Notes', ''))
                        if row.get('Red Flags'):
                            st.markdown("**Red Flags:**")
                            st.error(row.get('Red Flags', ''))
                        if row.get('Action Items'):
                            st.markdown("**Action Items:**")
                            st.warning(row.get('Action Items', ''))
                        
                        # Display call recording if available
                        if 'Call Recording' in row and pd.notna(row.get('Call Recording')) and row.get('Call Recording'):
                            recording_path = row.get('Call Recording', '')
                            if recording_path and Path(recording_path).exists():
                                st.markdown("**Call Recording:**")
                                try:
                                    recording_file = Path(recording_path)
                                    file_ext = recording_file.suffix.lower()
                                    with open(recording_file, 'rb') as f:
                                        recording_bytes = f.read()
                                    if file_ext in ['.mp3', '.wav', '.m4a']:
                                        st.audio(recording_bytes)
                                    elif file_ext in ['.mp4', '.mov', '.avi']:
                                        st.video(recording_bytes)
                                    else:
                                        st.info(f"Recording file: {recording_file.name}")
                                except Exception as e:
                                    st.error(f"Error loading recording: {e}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Radar Chart - Player's Call Metrics vs Call Log Average
            if not player_calls.empty:
                st.markdown("### Performance Comparison Radar Chart")
                
                # Define call log metrics
                call_metrics = ['Communication', 'Maturity', 'Coachability', 'Leadership', 'Work Ethic', 
                              'Confidence', 'Tactical Knowledge', 'Team Fit', 'Overall Rating']
                
                # Filter to only include metrics that exist in both player calls and call log
                available_call_metrics = [col for col in call_metrics if col in player_calls.columns]
                call_log_available_metrics = [col for col in call_metrics if col in st.session_state.call_log.columns] if not st.session_state.call_log.empty else []
                
                # Find intersection
                available_metrics = [m for m in available_call_metrics if m in call_log_available_metrics]
                
                if available_metrics and len(st.session_state.call_log) > 0:
                    # Calculate player's average for each metric
                    player_avg = player_calls[available_metrics].mean()
                    
                    # Calculate average across all players for each metric (from call log)
                    all_players_avg = st.session_state.call_log[available_metrics].mean()
                    
                    # Create radar chart using matplotlib
                    import matplotlib.pyplot as plt
                    import matplotlib
                    import numpy as np
                    matplotlib.use('Agg')  # Use non-interactive backend
                    
                    # Number of metrics
                    N = len(available_metrics)
                    
                    # Compute angle for each metric (radar chart is circular)
                    angles = [n / float(N) * 2 * np.pi for n in range(N)]
                    angles += angles[:1]  # Complete the circle
                    
                    # Prepare data
                    player_values = [player_avg[metric] for metric in available_metrics]
                    player_values += player_values[:1]  # Complete the circle
                    
                    all_players_values = [all_players_avg[metric] for metric in available_metrics]
                    all_players_values += all_players_values[:1]  # Complete the circle
                    
                    # Create figure - slightly larger to accommodate labels outside
                    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
                    fig.patch.set_facecolor('#1e1e1e')
                    ax.set_facecolor('#1e1e1e')
                    
                    # Set y-axis (ratings from 0 to 10) - extend beyond 10 to make room for labels
                    ax.set_ylim(0, 12)
                    ax.set_yticks([2, 4, 6, 8, 10])
                    ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#fafafa', fontsize=7)
                    ax.grid(True, color='#4a4a4a', linestyle='--', linewidth=0.5)
                    
                    # Plot player data
                    ax.plot(angles, player_values, 'o-', linewidth=2, label=selected_player, color='#8B0000', markersize=6)
                    ax.fill(angles, player_values, alpha=0.25, color='#8B0000')
                    
                    # Plot call log average
                    ax.plot(angles, all_players_values, 'o-', linewidth=2, label='Call Log Average', color='#4a4a4a', markersize=6)
                    ax.fill(angles, all_players_values, alpha=0.15, color='#4a4a4a')
                    
                    # Set labels - position them at the end of each axis
                    ax.set_xticks(angles[:-1])
                    # First, set empty labels to avoid duplicates
                    ax.set_xticklabels([''] * len(available_metrics))
                    
                    # Now manually place all labels at the end of their axes
                    labels_to_move_inward = ['Team Fit', 'Tactical Knowledge', 'Leadership', 'Coachability', 'Maturity']
                    
                    for i, metric in enumerate(available_metrics):
                        angle_rad = angles[i]
                        # Position most labels at radius 11.5 (at the end of the axis)
                        # Position specific labels slightly inward at radius 11.0
                        if metric in labels_to_move_inward:
                            radius_for_label = 11.0
                        else:
                            radius_for_label = 11.5
                        
                        # Place label at the end of the axis using polar coordinates
                        ax.text(angle_rad, radius_for_label, metric, 
                               ha='center', va='center',
                               color='#fafafa', fontsize=9, fontweight='bold')
                    
                    # Add title - dynamic based on selected player
                    ax.set_title(f'{selected_player} vs Call Log Average', size=11, color='#fafafa', fontweight='bold', pad=20)
                    
                    # Add legend
                    legend = ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), 
                                      facecolor='#2a2a2a', edgecolor='#4a4a4a', 
                                      labelcolor='#fafafa', fontsize=8)
                    legend.get_frame().set_alpha(0.9)
                    
                    # Tight layout to reduce padding
                    fig.tight_layout(pad=0.5)
                    
                    # Center the chart on the page using columns with minimal spacing
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.pyplot(fig, use_container_width=False)
            else:
                st.info("No phone call data available for radar chart.")
            
            # ========== VIDEO ANALYSIS SECTION ==========
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("## 🎥 Video Analysis")
            
            # Video Analysis Summary Metrics
            video_col1, video_col2, video_col3, video_col4 = st.columns(4)
            with video_col1:
                st.metric("Total Reviews", len(player_video_reviews))
            with video_col2:
                if not player_video_reviews.empty and 'Video Score' in player_video_reviews.columns:
                    avg_video_score = player_video_reviews['Video Score'].mean()
                    st.metric("Avg Video Score", f"{avg_video_score:.1f}/10")
                else:
                    st.metric("Avg Video Score", "N/A")
            with video_col3:
                if not player_video_reviews.empty and 'Overall Video Rating' in player_video_reviews.columns:
                    avg_video_rating = player_video_reviews['Overall Video Rating'].mean()
                    st.metric("Avg Video Rating", f"{avg_video_rating:.1f}/10")
                else:
                    st.metric("Avg Video Rating", "N/A")
            with video_col4:
                if not player_video_reviews.empty and 'Recommendation' in player_video_reviews.columns:
                    latest_video_rec = player_video_reviews.iloc[-1]['Recommendation'] if len(player_video_reviews) > 0 else "N/A"
                    st.metric("Latest Recommendation", latest_video_rec)
                else:
                    st.metric("Latest Recommendation", "N/A")
            
            if not player_video_reviews.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### Average Ratings")
                video_rating_cols = ['Technical Ability', 'Tactical Awareness', 'Decision Making', 'Physical Attributes', 
                                   'Work Rate', 'Communication', 'Leadership', 'Composure', 'Overall Video Rating']
                # Filter to only include columns that exist in the dataframe
                video_rating_cols = [col for col in video_rating_cols if col in player_video_reviews.columns]
                if video_rating_cols:
                    avg_video_ratings = player_video_reviews[video_rating_cols].mean()
                    # Create bar chart with Portland Red color (#8B0000) using Altair
                    import altair as alt
                    
                    video_chart_data = pd.DataFrame({
                        'Metric': avg_video_ratings.index,
                        'Average Rating': avg_video_ratings.values
                    })
                    
                    video_chart = alt.Chart(video_chart_data).mark_bar(
                        color='#8B0000',  # Portland Red
                        cornerRadiusTopLeft=4,
                        cornerRadiusTopRight=4
                    ).encode(
                        x=alt.X('Metric', axis=alt.Axis(labelAngle=0, labelColor='white', title=None)),
                        y=alt.Y('Average Rating', axis=alt.Axis(labelColor='white', titleColor='white'), scale=alt.Scale(domain=[0, 10], padding=0.15)),
                        tooltip=['Metric', 'Average Rating']
                    ).properties(
                        width=600,
                        height=450,
                        padding={'top': 50, 'bottom': 40, 'left': 40, 'right': 40}
                    ).configure(
                        background='#1e1e1e',
                        view=alt.ViewConfig(stroke=None)
                    ).configure_axis(
                        gridColor='#4a4a4a',  # More subtle gray instead of white
                        domainColor='#8B0000',
                        gridOpacity=0.4
                    )
                    
                    st.altair_chart(video_chart, use_container_width=True)
            else:
                st.info("No video analysis data available for this player.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # All Video Reviews Table
            if not player_video_reviews.empty:
                st.markdown("### All Video Reviews")
                
                video_reviews_display = player_video_reviews.copy()
                
                # Format date columns
                if 'Review Date' in video_reviews_display.columns:
                    try:
                        video_reviews_display['Review Date'] = pd.to_datetime(video_reviews_display['Review Date'], errors='coerce')
                        video_reviews_display['Review Date'] = video_reviews_display['Review Date'].dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                # Select key columns to display
                key_video_columns = [
                    'Review Date', 'Video Type', 'Video Source', 'Video Score', 
                    'Overall Video Rating', 'Video Grade', 'Status', 'Recommendation'
                ]
                # Only include columns that exist
                display_video_columns = [col for col in key_video_columns if col in video_reviews_display.columns]
                
                if display_video_columns:
                    st.dataframe(
                        video_reviews_display[display_video_columns].sort_values('Review Date', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show full video review details in expanders
                st.markdown("### Video Review Details")
                for idx, row in player_video_reviews.iterrows():
                    review_date = row.get('Review Date', 'N/A')
                    video_type = row.get('Video Type', 'N/A')
                    with st.expander(f"Review: {review_date} - {video_type}"):
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            if 'Video Score' in row:
                                st.metric("Video Score", f"{row.get('Video Score', 'N/A')}/10")
                            if 'Overall Video Rating' in row:
                                st.metric("Overall Rating", f"{row.get('Overall Video Rating', 'N/A')}/10")
                            if 'Video Grade' in row:
                                st.metric("Grade", row.get('Video Grade', 'N/A'))
                        with col_v2:
                            if 'Status' in row:
                                st.metric("Status", row.get('Status', 'N/A'))
                            if 'Recommendation' in row:
                                st.metric("Recommendation", row.get('Recommendation', 'N/A'))
                            if 'Quantitative Match' in row:
                                st.metric("Quantitative Match", row.get('Quantitative Match', 'N/A'))
                        
                        # Performance metrics
                        if any(col in row for col in ['Technical Ability', 'Tactical Awareness', 'Decision Making']):
                            st.markdown("**Performance Metrics:**")
                            perf_metrics = ['Technical Ability', 'Tactical Awareness', 'Decision Making', 
                                          'Physical Attributes', 'Work Rate', 'Communication', 
                                          'Leadership', 'Composure', 'Overall Video Rating']
                            perf_data = {metric: row.get(metric, 'N/A') for metric in perf_metrics if metric in row}
                            if perf_data:
                                perf_df = pd.DataFrame([perf_data])
                                st.dataframe(perf_df.T, use_container_width=True, hide_index=False)
                        
                        # Observations
                        if row.get('Key Observations'):
                            st.markdown("**Key Observations:**")
                            st.info(row.get('Key Observations', ''))
                        if row.get('Strengths Identified'):
                            st.markdown("**Strengths:**")
                            st.success(row.get('Strengths Identified', ''))
                        if row.get('Weaknesses Identified'):
                            st.markdown("**Weaknesses:**")
                            st.warning(row.get('Weaknesses Identified', ''))
                        if row.get('Red Flags'):
                            st.markdown("**Red Flags:**")
                            st.error(row.get('Red Flags', ''))
                        if row.get('Additional Notes'):
                            st.markdown("**Additional Notes:**")
                            st.text(row.get('Additional Notes', ''))
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Radar Chart - Player's Video Metrics vs Video Analysis Average
            if not player_video_reviews.empty:
                st.markdown("### Performance Comparison Radar Chart")
                
                # Define video review metrics
                video_metrics = ['Technical Ability', 'Tactical Awareness', 'Decision Making', 'Physical Attributes', 
                               'Work Rate', 'Communication', 'Leadership', 'Composure', 'Overall Video Rating']
                
                # Filter to only include metrics that exist in both player reviews and all video reviews
                available_video_metrics = [col for col in video_metrics if col in player_video_reviews.columns]
                all_video_reviews_available_metrics = [col for col in video_metrics if col in st.session_state.video_reviews.columns] if not st.session_state.video_reviews.empty else []
                
                # Find intersection
                available_metrics = [m for m in available_video_metrics if m in all_video_reviews_available_metrics]
                
                if available_metrics and len(st.session_state.video_reviews) > 0:
                    # Calculate player's average for each metric
                    player_video_avg = player_video_reviews[available_metrics].mean()
                    
                    # Calculate average across all players for each metric (from all video reviews)
                    all_players_video_avg = st.session_state.video_reviews[available_metrics].mean()
                    
                    # Create radar chart using matplotlib
                    import matplotlib.pyplot as plt
                    import matplotlib
                    import numpy as np
                    matplotlib.use('Agg')  # Use non-interactive backend
                    
                    # Number of metrics
                    N = len(available_metrics)
                    
                    # Compute angle for each metric (radar chart is circular)
                    angles = [n / float(N) * 2 * np.pi for n in range(N)]
                    angles += angles[:1]  # Complete the circle
                    
                    # Prepare data
                    player_values = [player_video_avg[metric] for metric in available_metrics]
                    player_values += player_values[:1]  # Complete the circle
                    
                    all_players_values = [all_players_video_avg[metric] for metric in available_metrics]
                    all_players_values += all_players_values[:1]  # Complete the circle
                    
                    # Create figure - slightly larger to accommodate labels outside
                    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
                    fig.patch.set_facecolor('#1e1e1e')
                    ax.set_facecolor('#1e1e1e')
                    
                    # Set y-axis (ratings from 0 to 10) - extend beyond 10 to make room for labels
                    ax.set_ylim(0, 12)
                    ax.set_yticks([2, 4, 6, 8, 10])
                    ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#fafafa', fontsize=7)
                    ax.grid(True, color='#4a4a4a', linestyle='--', linewidth=0.5)
                    
                    # Plot player data
                    ax.plot(angles, player_values, 'o-', linewidth=2, label=selected_player, color='#8B0000', markersize=6)
                    ax.fill(angles, player_values, alpha=0.25, color='#8B0000')
                    
                    # Plot video analysis average
                    ax.plot(angles, all_players_values, 'o-', linewidth=2, label='Video Analysis Average', color='#4a4a4a', markersize=6)
                    ax.fill(angles, all_players_values, alpha=0.15, color='#4a4a4a')
                    
                    # Set labels - position them at the end of each axis
                    ax.set_xticks(angles[:-1])
                    # First, set empty labels to avoid duplicates
                    ax.set_xticklabels([''] * len(available_metrics))
                    
                    # Now manually place all labels at the end of their axes
                    labels_to_move_inward = ['Overall Video Rating', 'Tactical Awareness', 'Physical Attributes', 'Decision Making']
                    
                    for i, metric in enumerate(available_metrics):
                        angle_rad = angles[i]
                        # Position most labels at radius 11.5 (at the end of the axis)
                        # Position specific labels slightly inward at radius 11.0
                        if metric in labels_to_move_inward:
                            radius_for_label = 11.0
                        else:
                            radius_for_label = 11.5
                        
                        # Place label at the end of the axis using polar coordinates
                        ax.text(angle_rad, radius_for_label, metric, 
                               ha='center', va='center',
                               color='#fafafa', fontsize=9, fontweight='bold')
                    
                    # Add title - dynamic based on selected player
                    ax.set_title(f'{selected_player} vs Video Analysis Average', size=11, color='#fafafa', fontweight='bold', pad=20)
                    
                    # Add legend
                    legend = ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), 
                                      facecolor='#2a2a2a', edgecolor='#4a4a4a', 
                                      labelcolor='#fafafa', fontsize=8)
                    legend.get_frame().set_alpha(0.9)
                    
                    # Tight layout to reduce padding
                    fig.tight_layout(pad=0.5)
                    
                    # Center the chart on the page using columns with minimal spacing
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.pyplot(fig, use_container_width=False)
            else:
                st.info("No video analysis data available for radar chart.")
            
            # ========== SHARED ELEMENTS ==========
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download Player Summary PDF
            st.markdown("### Download Player Summary")
            
            if PDF_AVAILABLE:
                def generate_player_summary_pdf(player_name, player_calls_df, player_rank, player_percentile, total_players, player_video_reviews_df=None):
                    """Generate comprehensive player summary PDF."""
                    try:
                        pdf_buffer = BytesIO()
                        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                                              rightMargin=0.3*inch, leftMargin=0.3*inch,
                                              topMargin=0.3*inch, bottomMargin=0.3*inch)
                        
                        elements = []
                        styles = getSampleStyleSheet()
                        
                        # Define styles
                        title_style = ParagraphStyle(
                            'PlayerTitle',
                            parent=styles['Heading1'],
                            fontSize=16,
                            textColor=colors.HexColor('#8B0000'),
                            spaceAfter=10,
                        )
                        heading_style = ParagraphStyle(
                            'PlayerHeading',
                            parent=styles['Heading2'],
                            fontSize=10,
                            textColor=colors.HexColor('#333333'),
                            spaceAfter=6,
                            spaceBefore=8,
                        )
                        normal_style = ParagraphStyle(
                            'PlayerNormal',
                            parent=styles['Normal'],
                            fontSize=8,
                            spaceAfter=3,
                        )
                        small_style = ParagraphStyle(
                            'PlayerSmall',
                            parent=styles['Normal'],
                            fontSize=7,
                            textColor=colors.HexColor('#666666'),
                        )
                        
                        # Helper function
                        def get_value(key, default='N/A'):
                            val = player_calls_df.iloc[-1].get(key, default) if len(player_calls_df) > 0 else default
                            if val is None or val == '' or (isinstance(val, str) and str(val).strip() == ''):
                                return default
                            return str(val)
                        
                        # Title
                        title = Paragraph(f"Player Summary - {escape_text(player_name)}", title_style)
                        elements.append(title)
                        elements.append(Spacer(1, 0.1*inch))
                        
                        # Summary Metrics
                        elements.append(Paragraph("Summary Metrics", heading_style))
                        avg_rating_str = f"{player_calls_df['Overall Rating'].mean():.1f}/10" if not player_calls_df.empty and 'Overall Rating' in player_calls_df.columns else "N/A"
                        summary_data = [
                            ['Total Calls:', str(len(player_calls_df)),
                             'Overall Rank:', f"#{player_rank} of {total_players}" if player_rank else "N/A"],
                            ['Percentile:', f"{player_percentile:.1f}th" if player_percentile else "N/A",
                             'Avg Overall Rating:', avg_rating_str],
                            ['Latest Recommendation:', escape_text(get_value('Recommendation')),
                             'Team:', escape_text(get_value('Team'))],
                            ['Conference:', escape_text(get_value('Conference')),
                             'Position:', escape_text(get_value('Position Profile'))],
                        ]
                        summary_table = Table(summary_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
                        summary_table.setStyle(TableStyle([
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
                        elements.append(summary_table)
                        elements.append(Spacer(1, 0.15*inch))
                        
                        # Average Ratings
                        elements.append(Paragraph("Average Assessment Ratings", heading_style))
                        rating_cols = ['Communication', 'Maturity', 'Coachability', 'Leadership', 
                                      'Work Ethic', 'Confidence', 'Tactical Knowledge', 'Team Fit']
                        rating_cols = [col for col in rating_cols if col in player_calls_df.columns]
                        
                        if rating_cols:
                            avg_ratings = player_calls_df[rating_cols].mean()
                            rating_data = []
                            for i in range(0, len(rating_cols), 2):
                                col1 = rating_cols[i]
                                val1 = f"{avg_ratings[col1]:.1f}/10"
                                if i + 1 < len(rating_cols):
                                    col2 = rating_cols[i + 1]
                                    val2 = f"{avg_ratings[col2]:.1f}/10"
                                    rating_data.append([f"{col1}:", val1, f"{col2}:", val2])
                                else:
                                    rating_data.append([f"{col1}:", val1, '', ''])
                            
                            rating_table = Table(rating_data, colWidths=[1.3*inch, 0.7*inch, 1.3*inch, 0.7*inch])
                            rating_table.setStyle(TableStyle([
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
                            elements.append(rating_table)
                            elements.append(Spacer(1, 0.15*inch))
                        
                        # Assessment Grade Distribution
                        if 'Assessment Grade' in player_calls_df.columns:
                            elements.append(Paragraph("Assessment Grade Distribution", heading_style))
                            grade_counts = player_calls_df['Assessment Grade'].value_counts().sort_index()
                            grade_data = []
                            for grade, count in grade_counts.items():
                                grade_data.append([f"Grade {grade}:", f"{count} call(s)"])
                            
                            grade_table = Table(grade_data, colWidths=[1.2*inch, 1.8*inch])
                            grade_table.setStyle(TableStyle([
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
                            elements.append(grade_table)
                            elements.append(Spacer(1, 0.15*inch))
                        
                        # Key Information from Latest Call
                        elements.append(Paragraph("Key Information (Latest Call)", heading_style))
                        key_info = [
                            ['Agent:', escape_text(get_value('Agent Name'))],
                            ['Interest Level:', escape_text(get_value('Interest Level'))],
                            ['Salary Expectations:', escape_text(truncate_text(get_value('Salary Expectations'), 60))],
                            ['Red Flags:', escape_text(truncate_text(get_value('Red Flags'), 80))],
                        ]
                        key_table = Table(key_info, colWidths=[1.2*inch, 5.8*inch])
                        key_table.setStyle(TableStyle([
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
                        elements.append(key_table)
                        elements.append(Spacer(1, 0.15*inch))
                        
                        # Call History Summary
                        elements.append(Paragraph("Call History", heading_style))
                        call_history_data = [['Call Date', 'Call Type', 'Assessment Grade', 'Recommendation']]
                        for _, call in player_calls_df.iterrows():
                            call_date = str(call.get('Call Date', 'N/A'))[:10] if pd.notna(call.get('Call Date')) else 'N/A'
                            call_type = escape_text(str(call.get('Call Type', 'N/A')))
                            grade = escape_text(str(call.get('Assessment Grade', 'N/A')))
                            rec = escape_text(str(call.get('Recommendation', 'N/A')))
                            call_history_data.append([call_date, call_type, grade, rec])
                        
                        call_history_table = Table(call_history_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2.5*inch])
                        call_history_table.setStyle(TableStyle([
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 7),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 3),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ]))
                        elements.append(call_history_table)
                        elements.append(Spacer(1, 0.15*inch))
                        
                        # Video Reviews Section
                        if player_video_reviews_df is not None and not player_video_reviews_df.empty:
                            elements.append(Paragraph("Video Reviews", heading_style))
                            
                            # Video Reviews Summary
                            video_summary_data = [
                                ['Total Reviews:', str(len(player_video_reviews_df)),
                                 'Avg Video Score:', f"{player_video_reviews_df['Video Score'].mean():.1f}/10" if 'Video Score' in player_video_reviews_df.columns else "N/A"],
                                ['Avg Video Rating:', f"{player_video_reviews_df['Overall Video Rating'].mean():.1f}/10" if 'Overall Video Rating' in player_video_reviews_df.columns else "N/A",
                                 'Latest Recommendation:', escape_text(str(player_video_reviews_df.iloc[-1].get('Recommendation', 'N/A'))) if 'Recommendation' in player_video_reviews_df.columns else "N/A"],
                            ]
                            video_summary_table = Table(video_summary_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
                            video_summary_table.setStyle(TableStyle([
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
                            elements.append(video_summary_table)
                            elements.append(Spacer(1, 0.15*inch))
                            
                            # Video Reviews History
                            video_history_data = [['Review Date', 'Video Type', 'Video Score', 'Grade', 'Recommendation']]
                            for _, review in player_video_reviews_df.iterrows():
                                review_date = str(review.get('Review Date', 'N/A'))[:10] if pd.notna(review.get('Review Date')) else 'N/A'
                                video_type = escape_text(str(review.get('Video Type', 'N/A')))
                                video_score = escape_text(str(review.get('Video Score', 'N/A')))
                                grade = escape_text(str(review.get('Video Grade', 'N/A')))
                                rec = escape_text(str(review.get('Recommendation', 'N/A')))
                                video_history_data.append([review_date, video_type, video_score, grade, rec])
                            
                            video_history_table = Table(video_history_data, colWidths=[1.2*inch, 1.2*inch, 1.0*inch, 0.8*inch, 1.8*inch])
                            video_history_table.setStyle(TableStyle([
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 7),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                                ('TOPPADDING', (0, 0), (-1, -1), 3),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                            ]))
                            elements.append(video_history_table)
                            elements.append(Spacer(1, 0.15*inch))
                            
                            # Latest Video Review Details
                            if len(player_video_reviews_df) > 0:
                                latest_review = player_video_reviews_df.iloc[-1]
                                elements.append(Paragraph("Latest Video Review Details", heading_style))
                                
                                video_details = []
                                if pd.notna(latest_review.get('Key Observations')):
                                    video_details.append(['Key Observations:', escape_text(truncate_text(str(latest_review.get('Key Observations', '')), 100))])
                                if pd.notna(latest_review.get('Strengths Identified')):
                                    video_details.append(['Strengths:', escape_text(truncate_text(str(latest_review.get('Strengths Identified', '')), 100))])
                                if pd.notna(latest_review.get('Weaknesses Identified')):
                                    video_details.append(['Weaknesses:', escape_text(truncate_text(str(latest_review.get('Weaknesses Identified', '')), 100))])
                                if pd.notna(latest_review.get('Red Flags')):
                                    video_details.append(['Red Flags:', escape_text(truncate_text(str(latest_review.get('Red Flags', '')), 100))])
                                
                                if video_details:
                                    video_details_table = Table(video_details, colWidths=[1.2*inch, 5.8*inch])
                                    video_details_table.setStyle(TableStyle([
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
                                    elements.append(video_details_table)
                                    elements.append(Spacer(1, 0.15*inch))
                        
                        # Build PDF
                        doc.build(elements)
                        pdf_buffer.seek(0)
                        return pdf_buffer.getvalue()
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")
                        return None
                
                if st.button("Download Player Summary PDF", use_container_width=True):
                    pdf_bytes = generate_player_summary_pdf(
                        selected_player, 
                        player_calls, 
                        player_rank, 
                        player_percentile, 
                        total_players,
                        player_video_reviews
                    )
                    if pdf_bytes:
                        pdf_filename = f"player_summary_{selected_player.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        st.download_button(
                            "Download PDF",
                            data=pdf_bytes,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
            # All Calls Table
            if not player_calls.empty:
                st.markdown("### All Calls")
            
            # Format date columns before creating table data
            player_calls_display = player_calls.copy()
            if 'Call Date' in player_calls_display.columns:
                try:
                    player_calls_display['Call Date'] = pd.to_datetime(player_calls_display['Call Date'], errors='coerce')
                    player_calls_display['Call Date'] = player_calls_display['Call Date'].dt.strftime('%Y-%m-%d')
                except:
                    pass
            
            if 'Follow-up Date' in player_calls_display.columns:
                try:
                    player_calls_display['Follow-up Date'] = pd.to_datetime(player_calls_display['Follow-up Date'], errors='coerce')
                    player_calls_display['Follow-up Date'] = player_calls_display['Follow-up Date'].dt.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Define text-heavy columns that should be expandable
            text_heavy_columns = [
                'Call Notes',
                'Preparation Notes',
                'How They View Themselves',
                'What Is Important To Them',
                'Mindset Towards Growth',
                'Agent Notes',
                'Player Notes',
                'Key Talking Points',
                'Summary Notes',
                'Red Flags',
                'Action Items',
                'Other Opportunities',
                'Injury Periods',
                'Personality Traits',
                'Other Traits',
                'Agent Expectations',
                'Agent Negotiation Style',
                'How They Carry Themselves'
            ]
            
            # Prepare data for custom HTML table
            table_data = player_calls_display.to_dict('records')
            table_columns = list(player_calls_display.columns)
            
            # Build header row
            header_cells = []
            for col in table_columns:
                header_cells.append(f'<th>{col}</th>')
            header_row = ' '.join(header_cells)
            
            # Create HTML/JavaScript component for interactive table
            html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: transparent;
                        color: #fafafa;
                        -webkit-font-smoothing: antialiased;
                        -moz-osx-font-smoothing: grayscale;
                    }}
                    .table-wrapper {{
                        background: #1e1e1e;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                        margin-bottom: 0 !important;
                        padding-bottom: 0 !important;
                    }}
                    .table-container {{
                        overflow-x: auto;
                        max-height: 500px;
                        overflow-y: auto;
                        position: relative;
                    }}
                    .table-container::-webkit-scrollbar {{
                        width: 8px;
                        height: 8px;
                    }}
                    .table-container::-webkit-scrollbar-track {{
                        background: #1e1e1e;
                    }}
                    .table-container::-webkit-scrollbar-thumb {{
                        background: #3a3a3a;
                        border-radius: 4px;
                    }}
                    .table-container::-webkit-scrollbar-thumb:hover {{
                        background: #4a4a4a;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: separate;
                        border-spacing: 0;
                        background-color: transparent;
                        margin: 0;
                    }}
                    thead {{
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }}
                    th {{
                        background: linear-gradient(180deg, #2d2d2d 0%, #1e1e1e 100%);
                        color: #ffffff;
                        padding: 8px 12px;
                        text-align: left;
                        border-bottom: 2px solid #8B0000;
                        font-weight: 600;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        white-space: nowrap;
                        position: relative;
                        transition: background-color 0.2s ease;
                    }}
                    th:hover {{
                        background: linear-gradient(180deg, #3a3a3a 0%, #2d2d2d 100%);
                    }}
                    th::after {{
                        content: '';
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        right: 0;
                        height: 1px;
                        background: linear-gradient(90deg, transparent, #8B0000, transparent);
                    }}
                    td {{
                        padding: 8px 12px;
                        border-bottom: 1px solid rgba(58, 58, 58, 0.5);
                        max-width: 200px;
                        word-wrap: break-word;
                        font-size: 0.8125rem;
                        line-height: 1.4;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                        color: #e0e0e0;
                        font-weight: 700 !important;
                    }}
                    tbody td {{
                        font-weight: 700 !important;
                    }}
                    tbody tr {{
                        background-color: #000000;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                        border-left: 3px solid transparent;
                    }}
                    tbody tr:nth-child(even) {{
                        background-color: #2a2a2a;
                    }}
                    tbody tr:hover {{
                        background-color: rgba(139, 0, 0, 0.3) !important;
                        border-left-color: #8B0000;
                        transform: translateX(2px);
                    }}
                    tbody tr:last-child td {{
                        border-bottom: none;
                    }}
                    .expandable-cell {{
                        cursor: pointer;
                        color: #8B0000;
                        text-decoration: underline;
                        text-decoration-color: #8B0000;
                        text-underline-offset: 2px;
                        position: relative;
                        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                        font-weight: 600;
                        font-size: 0.875rem;
                    }}
                    .expandable-cell::before {{
                        content: '▶';
                        margin-right: 4px;
                        font-size: 0.75rem;
                        display: inline-block;
                        transition: transform 0.2s ease;
                    }}
                    .expandable-cell:hover {{
                        color: #D10023;
                        background-color: rgba(139, 0, 0, 0.2) !important;
                        text-decoration-color: #D10023;
                        transform: translateX(2px);
                    }}
                    .expandable-cell:hover::before {{
                        transform: translateX(2px);
                    }}
                    .modal {{
                        display: none;
                        position: fixed;
                        z-index: 1000;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0,0,0,0.85);
                        backdrop-filter: blur(4px);
                        animation: fadeIn 0.2s ease;
                    }}
                    @keyframes fadeIn {{
                        from {{ opacity: 0; }}
                        to {{ opacity: 1; }}
                    }}
                    .modal-content {{
                        background-color: #1e1e1e;
                        margin: 5% auto;
                        padding: 0;
                        border: none;
                        border-radius: 12px;
                        width: 80%;
                        max-width: 800px;
                        max-height: 80vh;
                        overflow: hidden;
                        color: #fafafa;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                        animation: slideDown 0.3s ease;
                    }}
                    @keyframes slideDown {{
                        from {{
                            transform: translateY(-20px);
                            opacity: 0;
                        }}
                        to {{
                            transform: translateY(0);
                            opacity: 1;
                        }}
                    }}
                    .modal-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 20px 24px;
                        border-bottom: 1px solid #3a3a3a;
                        background: linear-gradient(180deg, #2a2a2a 0%, #1e1e1e 100%);
                    }}
                    .modal-title {{
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: #8B0000;
                        letter-spacing: 0.3px;
                    }}
                    .close {{
                        color: #aaa;
                        font-size: 24px;
                        font-weight: 300;
                        cursor: pointer;
                        width: 32px;
                        height: 32px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 50%;
                        transition: all 0.2s ease;
                    }}
                    .close:hover {{
                        background-color: #3a3a3a;
                        color: #fafafa;
                    }}
                    .modal-body {{
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        line-height: 1.3;
                        padding: 24px;
                        background-color: #1e1e1e;
                        max-height: calc(80vh - 100px);
                        overflow-y: auto;
                    }}
                    .modal-body::-webkit-scrollbar {{
                        width: 1px;
                    }}
                    .modal-body::-webkit-scrollbar-track {{
                        background: #1e1e1e;
                    }}
                    .modal-body::-webkit-scrollbar-thumb {{
                        background: #3a3a3a;
                        border-radius: 1px;
                    }}
                    .modal-body::-webkit-scrollbar-thumb:hover {{
                        background: #4a4a4a;
                    }}
                </style>
            </head>
            <body>
                <div class="table-wrapper">
                    <div class="table-container">
                        <table id="dataTable">
                        <thead>
                            <tr>
                                {header_row}
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add table rows
            for row_idx, row in enumerate(table_data):
                html_code += "<tr>"
                for col in table_columns:
                        raw_value = row.get(col, '')
                        
                        # Convert to string (dates are already formatted above)
                        if pd.notna(raw_value):
                            cell_value = str(raw_value)
                        else:
                            cell_value = ''
                        
                        # Check if this column should be expandable
                        if col in text_heavy_columns and cell_value and len(str(cell_value).strip()) > 0:
                            # Escape quotes for JavaScript
                            escaped_value = str(cell_value).replace('"', '&quot;').replace("'", "&#39;").replace('\n', '\\n')
                            html_code += f'''
                            <td class="expandable-cell" 
                                onclick="showModal('{col}', `{escaped_value}`)"
                                title="Click to view full text">
                                Expand
                            </td>
                            '''
                        else:
                            # Escape HTML
                            escaped_cell = str(cell_value).replace('<', '&lt;').replace('>', '&gt;')
                            html_code += f"<td>{escaped_cell}</td>"
                html_code += "</tr>"
            
            html_code += """
                        </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Modal for expanded text -->
                <div id="textModal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <div class="modal-title" id="modalTitle"></div>
                            <span class="close" onclick="closeModal()">&times;</span>
                        </div>
                        <div class="modal-body" id="modalBody"></div>
                    </div>
                </div>
                
                <script>
                    function showModal(columnName, fullText) {{
                        document.getElementById('modalTitle').textContent = columnName;
                        document.getElementById('modalBody').textContent = fullText;
                        document.getElementById('textModal').style.display = 'block';
                    }}
                    
                    function closeModal() {{
                        document.getElementById('textModal').style.display = 'none';
                    }}
                    
                    // Close modal when clicking outside of it
                    window.onclick = function(event) {{
                        const modal = document.getElementById('textModal');
                        if (event.target == modal) {{
                            closeModal();
                        }}
                    }}
                    
                    // Close modal with Escape key
                    document.addEventListener('keydown', function(event) {{
                        if (event.key === 'Escape') {{
                            closeModal();
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            
            # Display the custom HTML table with aggressive spacing reduction
            st.markdown("""
            <style>
                    /* Very aggressive negative margins for iframe container */
                    div[data-testid="stIFrame"] {
                        margin-bottom: -5rem !important;
                        padding-bottom: 0 !important;
                    }
                    /* Target element-container wrapper */
                    .element-container:has([data-testid="stIFrame"]) {
                        margin-bottom: -5rem !important;
                        padding-bottom: 0 !important;
                    }
                    /* Target block container div */
                    .block-container > div:has([data-testid="stIFrame"]) {
                        margin-bottom: -5rem !important;
                        padding-bottom: 0 !important;
                    }
                    /* Target divider container with negative margins */
                    .block-container > div:has(hr) {
                        margin-top: -4rem !important;
                        margin-bottom: -3rem !important;
                        padding: 0 !important;
                    }
                    /* Target radar chart section */
                    .block-container > div:has(hr) + div {
                        margin-top: -3rem !important;
                        padding-top: 0 !important;
                    }
                    /* Target all divs between iframe and radar chart */
                    .block-container > div:has([data-testid="stIFrame"]) ~ div {
                        margin-top: -2rem !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            components.html(html_code, height=550, scrolling=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Call Review Details
            if not player_calls.empty:
                st.markdown("### Call Review Details")
                for idx, row in player_calls.iterrows():
                    call_date = row.get('Call Date', 'N/A')
                    call_number = row.get('Call Number', 'N/A')
                    call_type = row.get('Call Type', 'N/A')
                    with st.expander(f"Call #{call_number} - {call_date} ({call_type})"):
                        col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if 'Overall Rating' in row:
                            st.metric("Overall Rating", f"{row.get('Overall Rating', 'N/A')}/10")
                        if 'Assessment Grade' in row:
                            st.metric("Grade", row.get('Assessment Grade', 'N/A'))
                        if 'Recommendation' in row:
                            st.metric("Recommendation", row.get('Recommendation', 'N/A'))
                    with col_c2:
                        if 'Call Type' in row:
                            st.metric("Call Type", row.get('Call Type', 'N/A'))
                        if 'Agent Name' in row:
                            st.metric("Agent", row.get('Agent Name', 'N/A'))
                        if 'Interest Level' in row:
                            st.metric("Interest Level", row.get('Interest Level', 'N/A'))
                    
                    # Performance metrics
                    call_metrics = ['Communication', 'Maturity', 'Coachability', 'Leadership', 
                                  'Work Ethic', 'Confidence', 'Tactical Knowledge', 'Team Fit', 'Overall Rating']
                    call_metrics_data = {metric: row.get(metric, 'N/A') for metric in call_metrics if metric in row}
                    if call_metrics_data:
                        st.markdown("**Performance Metrics:**")
                        call_metrics_df = pd.DataFrame([call_metrics_data])
                        st.dataframe(call_metrics_df.T, use_container_width=True, hide_index=False)
                    
                    # Call details
                    if row.get('Call Notes'):
                        st.markdown("**Call Notes:**")
                        st.info(row.get('Call Notes', ''))
                    if row.get('Preparation Notes'):
                        st.markdown("**Preparation Notes:**")
                        st.text(row.get('Preparation Notes', ''))
                    if row.get('Summary Notes'):
                        st.markdown("**Summary Notes:**")
                        st.text(row.get('Summary Notes', ''))
                    if row.get('Red Flags'):
                        st.markdown("**Red Flags:**")
                        st.error(row.get('Red Flags', ''))
                    if row.get('Action Items'):
                        st.markdown("**Action Items:**")
                        st.warning(row.get('Action Items', ''))
                    
                    # Display call recording if available
                    if 'Call Recording' in row and pd.notna(row.get('Call Recording')) and row.get('Call Recording'):
                        recording_path = row.get('Call Recording', '')
                        if recording_path and Path(recording_path).exists():
                            st.markdown("**Call Recording:**")
                            try:
                                recording_file = Path(recording_path)
                                file_ext = recording_file.suffix.lower()
                                with open(recording_file, 'rb') as f:
                                    recording_bytes = f.read()
                                if file_ext in ['.mp3', '.wav', '.m4a']:
                                    st.audio(recording_bytes)
                                elif file_ext in ['.mp4', '.mov', '.avi']:
                                    st.video(recording_bytes)
                                else:
                                    st.info(f"Recording file: {recording_file.name}")
                            except Exception as e:
                                st.error(f"Error loading recording: {e}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Radar Chart - Player's Call Metrics vs Call Log Average
            if not player_calls.empty:
                st.markdown("### Performance Comparison Radar Chart")
                
                # Define call log metrics
                call_metrics = ['Communication', 'Maturity', 'Coachability', 'Leadership', 'Work Ethic', 
                              'Confidence', 'Tactical Knowledge', 'Team Fit', 'Overall Rating']
                
                # Filter to only include metrics that exist in both player calls and call log
                available_call_metrics = [col for col in call_metrics if col in player_calls.columns]
                call_log_available_metrics = [col for col in call_metrics if col in st.session_state.call_log.columns] if not st.session_state.call_log.empty else []
                
                # Find intersection
                available_metrics = [m for m in available_call_metrics if m in call_log_available_metrics]
                
                if available_metrics and len(st.session_state.call_log) > 0:
                    # Calculate player's average for each metric
                    player_avg = player_calls[available_metrics].mean()
                    
                    # Calculate average across all players for each metric (from call log)
                    all_players_avg = st.session_state.call_log[available_metrics].mean()
                    
                    # Create radar chart using matplotlib
                    import matplotlib.pyplot as plt
                    import matplotlib
                    import numpy as np
                    matplotlib.use('Agg')  # Use non-interactive backend
                    
                    # Number of metrics
                    N = len(available_metrics)
                    
                    # Compute angle for each metric (radar chart is circular)
                    angles = [n / float(N) * 2 * np.pi for n in range(N)]
                    angles += angles[:1]  # Complete the circle
                    
                    # Prepare data
                    player_values = [player_avg[metric] for metric in available_metrics]
                    player_values += player_values[:1]  # Complete the circle
                    
                    all_players_values = [all_players_avg[metric] for metric in available_metrics]
                    all_players_values += all_players_values[:1]  # Complete the circle
                    
                    # Create figure - slightly larger to accommodate labels outside
                    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
                    fig.patch.set_facecolor('#1e1e1e')
                    ax.set_facecolor('#1e1e1e')
                    
                    # Set y-axis (ratings from 0 to 10) - extend beyond 10 to make room for labels
                    ax.set_ylim(0, 12)
                    ax.set_yticks([2, 4, 6, 8, 10])
                    ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#fafafa', fontsize=7)
                    ax.grid(True, color='#4a4a4a', linestyle='--', linewidth=0.5)
                    
                    # Plot player data
                    ax.plot(angles, player_values, 'o-', linewidth=2, label=selected_player, color='#8B0000', markersize=6)
                    ax.fill(angles, player_values, alpha=0.25, color='#8B0000')
                    
                    # Plot call log average
                    ax.plot(angles, all_players_values, 'o-', linewidth=2, label='Call Log Average', color='#4a4a4a', markersize=6)
                    ax.fill(angles, all_players_values, alpha=0.15, color='#4a4a4a')
                    
                    # Set labels - position them at the end of each axis
                    ax.set_xticks(angles[:-1])
                    # First, set empty labels to avoid duplicates
                    ax.set_xticklabels([''] * len(available_metrics))
                    
                    # Now manually place all labels at the end of their axes
                    labels_to_move_inward = ['Team Fit', 'Tactical Knowledge', 'Leadership', 'Coachability', 'Maturity']
                    
                    for i, metric in enumerate(available_metrics):
                        angle_rad = angles[i]
                        # Position most labels at radius 11.5 (at the end of the axis)
                        # Position specific labels slightly inward at radius 11.0
                        if metric in labels_to_move_inward:
                            radius_for_label = 11.0
                        else:
                            radius_for_label = 11.5
                        
                        # Place label at the end of the axis using polar coordinates
                        ax.text(angle_rad, radius_for_label, metric, 
                               ha='center', va='center',
                               color='#fafafa', fontsize=9, fontweight='bold')
                    
                    # Add title - dynamic based on selected player
                    ax.set_title(f'{selected_player} vs Call Log Average', size=11, color='#fafafa', fontweight='bold', pad=20)
                    
                    # Add legend
                    legend = ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), 
                                      facecolor='#2a2a2a', edgecolor='#4a4a4a', 
                                      labelcolor='#fafafa', fontsize=8)
                    legend.get_frame().set_alpha(0.9)
                    
                    # Tight layout to reduce padding
                    fig.tight_layout(pad=0.5)
                    
                    # Center the chart on the page using columns with minimal spacing
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.pyplot(fig, use_container_width=False)
            else:
                st.info("No phone call data available for radar chart.")
            
            # ========== VIDEO ANALYSIS SECTION ==========
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("## 🎥 Video Analysis")
            
            # Video Analysis Summary Metrics
            video_col1, video_col2, video_col3, video_col4 = st.columns(4)
            with video_col1:
                st.metric("Total Reviews", len(player_video_reviews))
            with video_col2:
                if not player_video_reviews.empty and 'Video Score' in player_video_reviews.columns:
                    avg_video_score = player_video_reviews['Video Score'].mean()
                    st.metric("Avg Video Score", f"{avg_video_score:.1f}/10")
                else:
                    st.metric("Avg Video Score", "N/A")
            with video_col3:
                if not player_video_reviews.empty and 'Overall Video Rating' in player_video_reviews.columns:
                    avg_video_rating = player_video_reviews['Overall Video Rating'].mean()
                    st.metric("Avg Video Rating", f"{avg_video_rating:.1f}/10")
                else:
                    st.metric("Avg Video Rating", "N/A")
            with video_col4:
                if not player_video_reviews.empty and 'Recommendation' in player_video_reviews.columns:
                    latest_video_rec = player_video_reviews.iloc[-1]['Recommendation'] if len(player_video_reviews) > 0 else "N/A"
                    st.metric("Latest Recommendation", latest_video_rec)
                else:
                    st.metric("Latest Recommendation", "N/A")
            
            if not player_video_reviews.empty:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### Average Ratings")
                video_rating_cols = ['Technical Ability', 'Tactical Awareness', 'Decision Making', 'Physical Attributes', 
                                   'Work Rate', 'Communication', 'Leadership', 'Composure', 'Overall Video Rating']
                # Filter to only include columns that exist in the dataframe
                video_rating_cols = [col for col in video_rating_cols if col in player_video_reviews.columns]
                if video_rating_cols:
                    avg_video_ratings = player_video_reviews[video_rating_cols].mean()
                    # Create bar chart with Portland Red color (#8B0000) using Altair
                    import altair as alt
                    
                    video_chart_data = pd.DataFrame({
                        'Metric': avg_video_ratings.index,
                        'Average Rating': avg_video_ratings.values
                    })
                    
                    video_chart = alt.Chart(video_chart_data).mark_bar(
                        color='#8B0000',  # Portland Red
                        cornerRadiusTopLeft=4,
                        cornerRadiusTopRight=4
                    ).encode(
                        x=alt.X('Metric', axis=alt.Axis(labelAngle=0, labelColor='white', title=None)),
                        y=alt.Y('Average Rating', axis=alt.Axis(labelColor='white', titleColor='white'), scale=alt.Scale(domain=[0, 10], padding=0.15)),
                        tooltip=['Metric', 'Average Rating']
                    ).properties(
                        width=600,
                        height=450,
                        padding={'top': 50, 'bottom': 40, 'left': 40, 'right': 40}
                    ).configure(
                        background='#1e1e1e',
                        view=alt.ViewConfig(stroke=None)
                    ).configure_axis(
                        gridColor='#4a4a4a',  # More subtle gray instead of white
                        domainColor='#8B0000',
                        gridOpacity=0.4
                    )
                    
                    st.altair_chart(video_chart, use_container_width=True)
            else:
                st.info("No video analysis data available for this player.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # All Video Reviews Table
            if not player_video_reviews.empty:
                st.markdown("### All Video Reviews")
                
                video_reviews_display = player_video_reviews.copy()
                
                # Format date columns
                if 'Review Date' in video_reviews_display.columns:
                    try:
                        video_reviews_display['Review Date'] = pd.to_datetime(video_reviews_display['Review Date'], errors='coerce')
                        video_reviews_display['Review Date'] = video_reviews_display['Review Date'].dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                # Select key columns to display
                key_video_columns = [
                    'Review Date', 'Video Type', 'Video Source', 'Video Score', 
                    'Overall Video Rating', 'Video Grade', 'Status', 'Recommendation'
                ]
                # Only include columns that exist
                display_video_columns = [col for col in key_video_columns if col in video_reviews_display.columns]
                
                if display_video_columns:
                    st.dataframe(
                        video_reviews_display[display_video_columns].sort_values('Review Date', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show full video review details in expanders
                st.markdown("### Video Review Details")
                for idx, row in player_video_reviews.iterrows():
                    review_date = row.get('Review Date', 'N/A')
                    video_type = row.get('Video Type', 'N/A')
                    with st.expander(f"Review: {review_date} - {video_type}"):
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            if 'Video Score' in row:
                                st.metric("Video Score", f"{row.get('Video Score', 'N/A')}/10")
                            if 'Overall Video Rating' in row:
                                st.metric("Overall Rating", f"{row.get('Overall Video Rating', 'N/A')}/10")
                            if 'Video Grade' in row:
                                st.metric("Grade", row.get('Video Grade', 'N/A'))
                        with col_v2:
                            if 'Status' in row:
                                st.metric("Status", row.get('Status', 'N/A'))
                            if 'Recommendation' in row:
                                st.metric("Recommendation", row.get('Recommendation', 'N/A'))
                            if 'Quantitative Match' in row:
                                st.metric("Quantitative Match", row.get('Quantitative Match', 'N/A'))
                        
                        # Performance metrics
                        if any(col in row for col in ['Technical Ability', 'Tactical Awareness', 'Decision Making']):
                            st.markdown("**Performance Metrics:**")
                            perf_metrics = ['Technical Ability', 'Tactical Awareness', 'Decision Making', 
                                          'Physical Attributes', 'Work Rate', 'Communication', 
                                          'Leadership', 'Composure', 'Overall Video Rating']
                            perf_data = {metric: row.get(metric, 'N/A') for metric in perf_metrics if metric in row}
                            if perf_data:
                                perf_df = pd.DataFrame([perf_data])
                                st.dataframe(perf_df.T, use_container_width=True, hide_index=False)
                        
                        # Observations
                        if row.get('Key Observations'):
                            st.markdown("**Key Observations:**")
                            st.info(row.get('Key Observations', ''))
                        if row.get('Strengths Identified'):
                            st.markdown("**Strengths:**")
                            st.success(row.get('Strengths Identified', ''))
                        if row.get('Weaknesses Identified'):
                            st.markdown("**Weaknesses:**")
                            st.warning(row.get('Weaknesses Identified', ''))
                        if row.get('Red Flags'):
                            st.markdown("**Red Flags:**")
                            st.error(row.get('Red Flags', ''))
                        if row.get('Additional Notes'):
                            st.markdown("**Additional Notes:**")
                            st.text(row.get('Additional Notes', ''))
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Radar Chart - Player's Video Metrics vs Video Analysis Average
            if not player_video_reviews.empty:
                st.markdown("### Performance Comparison Radar Chart")
                
                # Define video review metrics
                video_metrics = ['Technical Ability', 'Tactical Awareness', 'Decision Making', 'Physical Attributes', 
                               'Work Rate', 'Communication', 'Leadership', 'Composure', 'Overall Video Rating']
                
                # Filter to only include metrics that exist in both player reviews and all video reviews
                available_video_metrics = [col for col in video_metrics if col in player_video_reviews.columns]
                all_video_reviews_available_metrics = [col for col in video_metrics if col in st.session_state.video_reviews.columns] if not st.session_state.video_reviews.empty else []
                
                # Find intersection
                available_metrics = [m for m in available_video_metrics if m in all_video_reviews_available_metrics]
                
                if available_metrics and len(st.session_state.video_reviews) > 0:
                    # Calculate player's average for each metric
                    player_video_avg = player_video_reviews[available_metrics].mean()
                    
                    # Calculate average across all players for each metric (from all video reviews)
                    all_players_video_avg = st.session_state.video_reviews[available_metrics].mean()
                    
                    # Create radar chart using matplotlib
                    import matplotlib.pyplot as plt
                    import matplotlib
                    import numpy as np
                    matplotlib.use('Agg')  # Use non-interactive backend
                    
                    # Number of metrics
                    N = len(available_metrics)
                    
                    # Compute angle for each metric (radar chart is circular)
                    angles = [n / float(N) * 2 * np.pi for n in range(N)]
                    angles += angles[:1]  # Complete the circle
                    
                    # Prepare data
                    player_values = [player_video_avg[metric] for metric in available_metrics]
                    player_values += player_values[:1]  # Complete the circle
                    
                    all_players_values = [all_players_video_avg[metric] for metric in available_metrics]
                    all_players_values += all_players_values[:1]  # Complete the circle
                    
                    # Create figure - slightly larger to accommodate labels outside
                    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
                    fig.patch.set_facecolor('#1e1e1e')
                    ax.set_facecolor('#1e1e1e')
                    
                    # Set y-axis (ratings from 0 to 10) - extend beyond 10 to make room for labels
                    ax.set_ylim(0, 12)
                    ax.set_yticks([2, 4, 6, 8, 10])
                    ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#fafafa', fontsize=7)
                    ax.grid(True, color='#4a4a4a', linestyle='--', linewidth=0.5)
                    
                    # Plot player data
                    ax.plot(angles, player_values, 'o-', linewidth=2, label=selected_player, color='#8B0000', markersize=6)
                    ax.fill(angles, player_values, alpha=0.25, color='#8B0000')
                    
                    # Plot video analysis average
                    ax.plot(angles, all_players_values, 'o-', linewidth=2, label='Video Analysis Average', color='#4a4a4a', markersize=6)
                    ax.fill(angles, all_players_values, alpha=0.15, color='#4a4a4a')
                    
                    # Set labels - position them at the end of each axis
                    ax.set_xticks(angles[:-1])
                    # First, set empty labels to avoid duplicates
                    ax.set_xticklabels([''] * len(available_metrics))
                    
                    # Now manually place all labels at the end of their axes
                    labels_to_move_inward = ['Overall Video Rating', 'Tactical Awareness', 'Physical Attributes', 'Decision Making']
                    
                    for i, metric in enumerate(available_metrics):
                        angle_rad = angles[i]
                        # Position most labels at radius 11.5 (at the end of the axis)
                        # Position specific labels slightly inward at radius 11.0
                        if metric in labels_to_move_inward:
                            radius_for_label = 11.0
                        else:
                            radius_for_label = 11.5
                        
                        # Place label at the end of the axis using polar coordinates
                        ax.text(angle_rad, radius_for_label, metric, 
                               ha='center', va='center',
                               color='#fafafa', fontsize=9, fontweight='bold')
                    
                    # Add title - dynamic based on selected player
                    ax.set_title(f'{selected_player} vs Video Analysis Average', size=11, color='#fafafa', fontweight='bold', pad=20)
                    
                    # Add legend
                    legend = ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), 
                                      facecolor='#2a2a2a', edgecolor='#4a4a4a', 
                                      labelcolor='#fafafa', fontsize=8)
                    legend.get_frame().set_alpha(0.9)
                    
                    # Tight layout to reduce padding
                    fig.tight_layout(pad=0.5)
                    
                    # Center the chart on the page using columns with minimal spacing
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.pyplot(fig, use_container_width=False)
            else:
                st.info("No video analysis data available for radar chart.")
            
            # ========== SHARED ELEMENTS ==========
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
elif page == "Performance Metrics":
    st.header("Performance Metrics")
    st.markdown("Comprehensive performance analysis and visualization from the long shortlist database.")
    
    # Load position-specific metrics from JSON config
    @st.cache_data
    def load_position_metrics_config():
        """Load position-specific metrics from JSON config file."""
        import json
        config_path = Path(__file__).parent / "position_metrics_config.json"
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config
        except Exception as e:
            st.warning(f"Could not load position metrics config: {e}")
        return {}
    
    def get_metrics_for_position(position_profile, config, available_columns):
        """Get position-specific metrics from config, matching available columns."""
        if not config or 'position_profiles' not in config:
            return []
        
        # Map position profile names to JSON keys
        position_map = {
            'DM Box-To-Box': 'Centre Midfielder',
            'AM Advanced Playmaker': 'Attacking Midfielder',
            'Right Touchline Winger': 'Winger',
            'Hybrid CB': 'Center Back',
            'Hybrid Ball-Playing/Winning': 'Center Back',
            'Touchline Winger (Right-Sided)': 'Winger',
            'Defensive-Minded Box-to-Box': 'Centre Midfielder',
            'Advanced Playmaker': 'Attacking Midfielder'
        }
        
        # Find matching position in config
        config_key = position_map.get(position_profile, position_profile)
        if config_key not in config['position_profiles']:
            # Try direct match
            config_key = position_profile
        
        if config_key not in config['position_profiles']:
            return []
        
        position_config = config['position_profiles'][config_key]
        metrics_list = []
        
        # Extract all metric names from Core and Specific sections
        for section in ['Core', 'Specific']:
            if section in position_config.get('metrics', {}):
                section_metrics = position_config['metrics'][section]
                for metric_key, metric_value in section_metrics.items():
                    if isinstance(metric_value, dict) and 'components' in metric_value:
                        # Composite metric - add all components
                        for component in metric_value['components'].keys():
                            metrics_list.append(component)
                    elif isinstance(metric_value, (int, float)):
                        # Simple metric
                        metrics_list.append(metric_key)
        
        # Match metrics to available columns (fuzzy matching)
        matched_metrics = []
        for metric in metrics_list:
            # Try exact match first
            if metric in available_columns:
                matched_metrics.append(metric)
            else:
                # Try fuzzy matching
                for col in available_columns:
                    # Check if metric name is contained in column name or vice versa
                    metric_lower = metric.lower()
                    col_lower = str(col).lower()
                    if metric_lower in col_lower or col_lower in metric_lower:
                        if col not in matched_metrics:
                            matched_metrics.append(col)
                            break
        
        return matched_metrics[:8]  # Limit to 8 metrics for radar chart
    
    # Load position metrics config
    position_config = load_position_metrics_config()
    
    # Load full player data from shortlist (reusing existing PLAYER_DB_FILE)
    @st.cache_data
    def load_full_shortlist_data():
        """Load complete player data with all metrics from shortlist Excel file."""
        try:
            if PLAYER_DB_FILE and PLAYER_DB_FILE.exists():
                # Try different header rows (same approach as existing load functions)
                for header_row in [2, 1, 0]:
                    try:
                        df_dict = pd.read_excel(PLAYER_DB_FILE, sheet_name=None, header=header_row)
                        all_data = []
                        
                        for sheet_name, sheet_df in df_dict.items():
                            # Skip non-data sheets (same logic as existing functions)
                            if sheet_name.startswith('Sheet') or 'Summary' in sheet_name or 'Notes' in sheet_name:
                                continue
                            
                            # Check if this sheet has player data (same check as existing functions)
                            if 'Player' in sheet_df.columns:
                                # Add position profile column
                                sheet_df['Position Profile'] = sheet_name
                                all_data.append(sheet_df)
                        
                        if all_data:
                            combined_df = pd.concat(all_data, ignore_index=True)
                            
                            # Handle duplicate column names by renaming them
                            if combined_df.columns.duplicated().any():
                                cols = pd.Series(combined_df.columns)
                                for dup in cols[cols.duplicated()].unique():
                                    dup_indices = cols[cols == dup].index.values.tolist()
                                    cols[dup_indices] = [dup if i == 0 else f"{dup}_{i}" 
                                                         for i in range(len(dup_indices))]
                                combined_df.columns = cols
                            
                            return combined_df
                    except Exception as e:
                        continue
        except Exception as e:
            st.error(f"Error loading shortlist data: {e}")
        
        return pd.DataFrame()
    
    # Load data (reusing the same file that's already loaded elsewhere)
    shortlist_df = load_full_shortlist_data()
    
    if shortlist_df.empty:
        st.warning("No shortlist data found. Please upload a player database file in the sidebar.")
        st.info("The Performance Metrics page requires the long shortlist Excel file with player statistics.")
    else:
        # Find player name column (use 'Player' like existing functions)
        player_col = 'Player' if 'Player' in shortlist_df.columns else None
        
        # Find conference column
        conf_col = None
        if 'Conference' in shortlist_df.columns:
            conf_col = 'Conference'
        else:
            # Try to find conference column with variations
            for col in shortlist_df.columns:
                if 'conference' in str(col).lower():
                    conf_col = col
                    break
        
        # Find team column
        team_col = None
        if 'Team' in shortlist_df.columns:
            team_col = 'Team'
        else:
            for col in shortlist_df.columns:
                if 'team' in str(col).lower() and col != 'Position Profile':
                    team_col = col
                    break
        
        if not player_col:
            st.error("Could not find 'Player' column in the data. Please ensure your Excel file has a 'Player' column.")
            st.info(f"Available columns: {', '.join(shortlist_df.columns.tolist()[:10])}...")
        else:
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs([
                "Position Metrics Comparison", 
                "Player Profile", 
                "Player Comparison", 
                "Scatter Plot Analysis"
            ])
            
            # Common filters
            st.sidebar.markdown("### Filters")
            
            # Conference filter
            if conf_col:
                conferences = sorted(shortlist_df[conf_col].dropna().unique().tolist())
                selected_conferences = st.sidebar.multiselect(
                    "Conferences",
                    conferences,
                    default=conferences if len(conferences) <= 5 else []
                )
            else:
                selected_conferences = []
                st.sidebar.info("Conference column not found")
            
            # Position filter
            if 'Position Profile' in shortlist_df.columns:
                positions = ['All'] + sorted(shortlist_df['Position Profile'].dropna().unique().tolist())
                selected_position = st.sidebar.selectbox("Position Profile", positions)
            else:
                selected_position = 'All'
                st.sidebar.info("Position Profile column not found")
            
            # Team filter
            if team_col:
                teams = ['All'] + sorted(shortlist_df[team_col].dropna().unique().tolist())
                selected_team = st.sidebar.selectbox("Team", teams)
            else:
                selected_team = 'All'
                st.sidebar.info("Team column not found")
            
            # Apply filters
            filtered_df = shortlist_df.copy()
            if selected_conferences and conf_col:
                filtered_df = filtered_df[filtered_df[conf_col].isin(selected_conferences)]
            if selected_position != 'All' and 'Position Profile' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Position Profile'] == selected_position]
            if selected_team != 'All' and team_col:
                filtered_df = filtered_df[filtered_df[team_col] == selected_team]
            
            # TAB 1: Position Metrics Comparison
            with tab1:
                st.subheader("Key Metrics Comparison")
                
                # Add filter dropdowns on the page
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                with filter_col1:
                    if conf_col:
                        page_conferences = ['All'] + sorted(shortlist_df[conf_col].dropna().unique().tolist())
                        page_selected_conference = st.selectbox("Filter by Conference", page_conferences, key="page_conf_filter")
                    else:
                        page_selected_conference = 'All'
                
                with filter_col2:
                    if 'Position Profile' in shortlist_df.columns:
                        page_positions = ['All'] + sorted(shortlist_df['Position Profile'].dropna().unique().tolist())
                        page_selected_position = st.selectbox("Filter by Position Profile", page_positions, key="page_pos_filter")
                    else:
                        page_selected_position = 'All'
                
                with filter_col3:
                    if team_col:
                        # Filter teams based on selected conference
                        if page_selected_conference != 'All' and conf_col:
                            conference_teams = sorted(shortlist_df[shortlist_df[conf_col] == page_selected_conference][team_col].dropna().unique().tolist())
                            page_teams = ['All'] + conference_teams
                        else:
                            page_teams = ['All'] + sorted(shortlist_df[team_col].dropna().unique().tolist())
                        page_selected_team = st.selectbox("Filter by Team", page_teams, key="page_team_filter")
                    else:
                        page_selected_team = 'All'
                
                # Apply page filters
                page_filtered_df = shortlist_df.copy()
                if page_selected_conference != 'All' and conf_col:
                    page_filtered_df = page_filtered_df[page_filtered_df[conf_col] == page_selected_conference]
                if page_selected_position != 'All' and 'Position Profile' in page_filtered_df.columns:
                    page_filtered_df = page_filtered_df[page_filtered_df['Position Profile'] == page_selected_position]
                if page_selected_team != 'All' and team_col:
                    page_filtered_df = page_filtered_df[page_filtered_df[team_col] == page_selected_team]
                
                if page_filtered_df.empty:
                    st.info("No data available for the selected filters.")
                else:
                    # Get numeric columns (metrics)
                    numeric_cols = page_filtered_df.select_dtypes(include=[np.number]).columns.tolist()
                    
                    # Get position-specific metrics if a position is selected
                    position_metrics = []
                    if page_selected_position != 'All' and position_config:
                        position_metrics = get_metrics_for_position(page_selected_position, position_config, numeric_cols)
                    
                    # Display table with styling - reorder to show position metrics first
                    display_cols = [player_col]
                    if team_col:
                        display_cols.append(team_col)
                    if conf_col:
                        display_cols.append(conf_col)
                    if 'Minutes played' in page_filtered_df.columns:
                        display_cols.append('Minutes played')
                    elif 'Minutes' in page_filtered_df.columns:
                        display_cols.append('Minutes')
                    
                    # Add Index column if it exists
                    index_cols = [c for c in page_filtered_df.columns if 'Index' in str(c) and c not in display_cols]
                    if index_cols:
                        display_cols.append(index_cols[0])
                    
                    # Add Grade column if it exists
                    grade_cols = [c for c in page_filtered_df.columns if 'Grade' in str(c) and c not in display_cols]
                    if grade_cols:
                        display_cols.append(grade_cols[0])
                    
                    # Add Rank column if it exists
                    rank_cols = [c for c in page_filtered_df.columns if 'Rank' in str(c) and c not in display_cols and 'Index' not in str(c)]
                    if rank_cols:
                        display_cols.append(rank_cols[0])
                    
                    # Add position-specific metrics FIRST (if available)
                    if position_metrics:
                        # Filter to only include metrics that exist in the dataframe
                        position_metrics = [m for m in position_metrics if m in page_filtered_df.columns and m not in display_cols]
                        display_cols.extend(position_metrics)
                    
                    # Add other key metrics (show all numeric columns, but limit display if too many)
                    # Filter out non-metric columns and already-added metrics
                    metric_cols = [c for c in numeric_cols if c not in display_cols and 'Unnamed' not in str(c)]
                    
                    # Show up to 15 additional metrics to avoid overwhelming the table
                    if len(metric_cols) > 15:
                        # Prioritize columns with 'PAdj' or common metric names
                        priority_metrics = [c for c in metric_cols if 'PAdj' in str(c) or any(term in str(c) for term in ['per 90', 'won (%)', 'accurate'])]
                        other_metrics = [c for c in metric_cols if c not in priority_metrics]
                        display_metrics = priority_metrics[:10] + other_metrics[:5]
                    else:
                        display_metrics = metric_cols
                    
                    display_cols.extend(display_metrics)
                    
                    # Only include columns that actually exist
                    display_cols = [c for c in display_cols if c in page_filtered_df.columns]
                    
                    display_df = page_filtered_df[display_cols].copy()
                    
                    # Sort by Index if available, otherwise by player name
                    if index_cols and index_cols[0] in display_df.columns:
                        display_df = display_df.sort_values(index_cols[0], ascending=False)
                    elif player_col in display_df.columns:
                        display_df = display_df.sort_values(player_col, ascending=True)
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=600,
                        hide_index=True
                    )
        
        # TAB 2: Player Profile
        with tab2:
            st.subheader("Player Profile")
            
            if player_col:
                player_list = sorted(shortlist_df[player_col].dropna().unique().tolist())
                selected_player_profile = st.selectbox("Select Player", player_list)
                
                if selected_player_profile:
                    player_data = shortlist_df[shortlist_df[player_col] == selected_player_profile].iloc[0]
                    
                    # Display player info with Grade and Rank
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        if team_col:
                            st.metric("Team", player_data.get(team_col, 'N/A'))
                    with col2:
                        if conf_col:
                            st.metric("Conference", player_data.get(conf_col, 'N/A'))
                    with col3:
                        if 'Position Profile' in player_data:
                            st.metric("Position", player_data.get('Position Profile', 'N/A'))
                    with col4:
                        # Find Grade column
                        grade_col = None
                        for col in shortlist_df.columns:
                            if 'Grade' in str(col):
                                grade_col = col
                                break
                        if grade_col:
                            st.metric("Grade", player_data.get(grade_col, 'N/A'))
                        else:
                            st.metric("Grade", "N/A")
                    with col5:
                        # Find Rank column (Position Profile rank)
                        rank_col = None
                        for col in shortlist_df.columns:
                            if 'Rank' in str(col) and 'Index' not in str(col):
                                rank_col = col
                                break
                        if rank_col:
                            rank_value = player_data.get(rank_col, 'N/A')
                            st.metric("Position Rank", rank_value if rank_value != 'N/A' else 'N/A')
                        else:
                            st.metric("Position Rank", "N/A")
                    
                    st.markdown("---")
                    
                    # Get position-specific metrics
                    player_position = player_data.get('Position Profile', '')
                    numeric_cols = shortlist_df.select_dtypes(include=[np.number]).columns.tolist()
                    
                    if player_position and position_config:
                        # Get position-specific metrics
                        top_metrics = get_metrics_for_position(player_position, position_config, numeric_cols)
                        # If no position-specific metrics found, fall back to first 8 numeric columns
                        if not top_metrics:
                            top_metrics = numeric_cols[:8]
                    else:
                        # Fall back to first 8 metrics
                        top_metrics = numeric_cols[:8] if len(numeric_cols) > 0 else []
                    
                    if len(top_metrics) > 0:
                        player_values = [player_data.get(m, 0) for m in top_metrics]
                        avg_values = [shortlist_df[m].mean() for m in top_metrics]
                        
                        # Create radar chart (smaller, centered)
                        import matplotlib.pyplot as plt
                        import matplotlib
                        matplotlib.use('Agg')
                        import numpy as np
                        
                        N = len(top_metrics)
                        angles = [n / float(N) * 2 * np.pi for n in range(N)]
                        angles += angles[:1]
                        
                        player_values += player_values[:1]
                        avg_values += avg_values[:1]
                        
                        # Smaller figure size (half of original)
                        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(projection='polar'))
                        fig.patch.set_facecolor('#1e1e1e')
                        ax.set_facecolor('#1e1e1e')
                        
                        ax.plot(angles, player_values, 'o-', linewidth=2, label=selected_player_profile, color='#8B0000', markersize=4)
                        ax.fill(angles, player_values, alpha=0.25, color='#8B0000')
                        ax.plot(angles, avg_values, 'o-', linewidth=2, label='Average', color='#4a4a4a', markersize=4)
                        ax.fill(angles, avg_values, alpha=0.15, color='#4a4a4a')
                        
                        ax.set_xticks(angles[:-1])
                        ax.set_xticklabels([m.replace('PAdj ', '').replace(' per 90', '')[:12] for m in top_metrics], 
                                          color='#fafafa', fontsize=7)
                        ax.tick_params(axis='x', pad=20, labelsize=7)
                        
                        ax.set_ylim(0, max(max(player_values), max(avg_values)) * 1.2)
                        ax.set_title(f'{selected_player_profile} Profile', size=11, color='#fafafa', fontweight='bold', pad=15)
                        
                        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), 
                                 facecolor='#2a2a2a', edgecolor='#4a4a4a', 
                                 labelcolor='#fafafa', fontsize=7)
                        
                        # Center the chart
                        col_left, col_chart, col_right = st.columns([1, 2, 1])
                        with col_chart:
                            st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
            else:
                st.info("Player data not available.")
        
        # TAB 3: Player Comparison
        with tab3:
            st.subheader("Player Comparison")
            
            if player_col:
                # Add filter dropdowns to help find players
                st.markdown("### Filters")
                comp_filter_col1, comp_filter_col2, comp_filter_col3 = st.columns(3)
                with comp_filter_col1:
                    if 'Position Profile' in shortlist_df.columns:
                        comp_positions = ['All'] + sorted(shortlist_df['Position Profile'].dropna().unique().tolist())
                        comp_selected_position = st.selectbox("Filter by Position Profile", comp_positions, key="comp_pos_filter")
                    else:
                        comp_selected_position = 'All'
                
                with comp_filter_col2:
                    if conf_col:
                        comp_conferences = ['All'] + sorted(shortlist_df[conf_col].dropna().unique().tolist())
                        comp_selected_conference = st.selectbox("Filter by Conference", comp_conferences, key="comp_conf_filter")
                    else:
                        comp_selected_conference = 'All'
                
                with comp_filter_col3:
                    if team_col:
                        # Filter teams based on selected conference
                        if comp_selected_conference != 'All' and conf_col:
                            comp_conference_teams = sorted(shortlist_df[shortlist_df[conf_col] == comp_selected_conference][team_col].dropna().unique().tolist())
                            comp_teams = ['All'] + comp_conference_teams
                        else:
                            comp_teams = ['All'] + sorted(shortlist_df[team_col].dropna().unique().tolist())
                        comp_selected_team = st.selectbox("Filter by Team", comp_teams, key="comp_team_filter")
                    else:
                        comp_selected_team = 'All'
                
                # Apply filters to player list
                comp_filtered_df = shortlist_df.copy()
                if comp_selected_position != 'All' and 'Position Profile' in comp_filtered_df.columns:
                    comp_filtered_df = comp_filtered_df[comp_filtered_df['Position Profile'] == comp_selected_position]
                if comp_selected_conference != 'All' and conf_col:
                    comp_filtered_df = comp_filtered_df[comp_filtered_df[conf_col] == comp_selected_conference]
                if comp_selected_team != 'All' and team_col:
                    comp_filtered_df = comp_filtered_df[comp_filtered_df[team_col] == comp_selected_team]
                
                # Only show players from the filtered dataset
                player_list = sorted(comp_filtered_df[player_col].dropna().unique().tolist())
                
                # If position profile is selected, ensure only players from that position are shown
                if comp_selected_position != 'All':
                    # This is already handled by the filter above, but we'll make it explicit
                    pass
                
                st.markdown("### Select Players")
                col1, col2 = st.columns(2)
                with col1:
                    player1 = st.selectbox("Player 1", player_list, key="comp_player1")
                with col2:
                    player2 = st.selectbox("Player 2", player_list, key="comp_player2")
                
                if player1 and player2:
                    p1_data = shortlist_df[shortlist_df[player_col] == player1].iloc[0]
                    p2_data = shortlist_df[shortlist_df[player_col] == player2].iloc[0]
                    
                    # Get position for metrics (use player1's position, or player2's if different)
                    p1_position = p1_data.get('Position Profile', '')
                    p2_position = p2_data.get('Position Profile', '')
                    comparison_position = p1_position if p1_position else p2_position
                    
                    # Comparison radar chart
                    numeric_cols = shortlist_df.select_dtypes(include=[np.number]).columns.tolist()
                    if len(numeric_cols) > 0:
                        # Get position-specific metrics
                        if comparison_position and position_config:
                            top_metrics = get_metrics_for_position(comparison_position, position_config, numeric_cols)
                            if not top_metrics:
                                top_metrics = numeric_cols[:8]
                        else:
                            top_metrics = numeric_cols[:8]
                        
                        p1_values = [p1_data.get(m, 0) for m in top_metrics]
                        p2_values = [p2_data.get(m, 0) for m in top_metrics]
                        
                        import matplotlib.pyplot as plt
                        import matplotlib
                        matplotlib.use('Agg')
                        import numpy as np
                        
                        N = len(top_metrics)
                        angles = [n / float(N) * 2 * np.pi for n in range(N)]
                        angles += angles[:1]
                        
                        p1_values += p1_values[:1]
                        p2_values += p2_values[:1]
                        
                        # Smaller figure size (half of original)
                        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(projection='polar'))
                        fig.patch.set_facecolor('#1e1e1e')
                        ax.set_facecolor('#1e1e1e')
                        
                        ax.plot(angles, p1_values, 'o-', linewidth=2, label=player1, color='#8B0000', markersize=4)
                        ax.fill(angles, p1_values, alpha=0.25, color='#8B0000')
                        ax.plot(angles, p2_values, 'o-', linewidth=2, label=player2, color='#4a4a4a', markersize=4)
                        ax.fill(angles, p2_values, alpha=0.15, color='#4a4a4a')
                        
                        ax.set_xticks(angles[:-1])
                        ax.set_xticklabels([m.replace('PAdj ', '').replace(' per 90', '')[:12] for m in top_metrics], 
                                          color='#fafafa', fontsize=7)
                        ax.tick_params(axis='x', pad=20, labelsize=7)
                        
                        max_val = max(max(p1_values), max(p2_values))
                        ax.set_ylim(0, max_val * 1.2)
                        ax.set_title(f'{player1} vs {player2}', size=11, color='#fafafa', fontweight='bold', pad=15)
                        
                        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), 
                                 facecolor='#2a2a2a', edgecolor='#4a4a4a', 
                                 labelcolor='#fafafa', fontsize=7)
                        
                        # Center the chart
                        col_left, col_chart, col_right = st.columns([1, 2, 1])
                        with col_chart:
                            st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
                        
                        # Comparison table
                        st.markdown("### Metric Comparison")
                        comparison_data = []
                        for metric in top_metrics:
                            p1_val = p1_data.get(metric, 0)
                            p2_val = p2_data.get(metric, 0)
                            comparison_data.append({
                                'Metric': metric,
                                player1: p1_val,
                                player2: p2_val,
                                'Difference': p1_val - p2_val
                            })
                        
                        comp_df = pd.DataFrame(comparison_data)
                        st.dataframe(comp_df, use_container_width=True, hide_index=True)
            else:
                st.info("Player data not available.")
        
        # TAB 4: Scatter Plot Analysis
        with tab4:
            st.subheader("Scatter Plot Analysis")
            
            numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_metric = st.selectbox("X-Axis Metric", numeric_cols, key="scatter_x")
                with col2:
                    y_metric = st.selectbox("Y-Axis Metric", numeric_cols, key="scatter_y")
                
                # Position filter for scatter
                if 'Position Profile' in filtered_df.columns:
                    scatter_positions = ['All'] + sorted(filtered_df['Position Profile'].dropna().unique().tolist())
                    scatter_position = st.selectbox("Filter by Position", scatter_positions, key="scatter_pos")
                    
                    scatter_df = filtered_df.copy()
                    if scatter_position != 'All':
                        scatter_df = scatter_df[scatter_df['Position Profile'] == scatter_position]
                else:
                    scatter_df = filtered_df
                
                if not scatter_df.empty and player_col:
                    # Create scatter plot
                    import altair as alt
                    
                    # Handle duplicate column names by renaming them BEFORE selecting columns
                    scatter_df_clean = scatter_df.copy()
                    if scatter_df_clean.columns.duplicated().any():
                        # Rename duplicate columns
                        cols = pd.Series(scatter_df_clean.columns)
                        for dup in cols[cols.duplicated()].unique():
                            dup_indices = cols[cols == dup].index.values.tolist()
                            cols[dup_indices] = [dup if i == 0 else f"{dup}_{i}" 
                                                 for i in range(len(dup_indices))]
                        scatter_df_clean.columns = cols
                    
                    # Ensure the columns we need exist and are unique
                    required_cols = [player_col, x_metric, y_metric]
                    available_cols = []
                    for col in required_cols:
                        if col in scatter_df_clean.columns:
                            available_cols.append(col)
                        else:
                            # Try to find a matching column (handle renamed duplicates)
                            matching = [c for c in scatter_df_clean.columns if c == col or c.startswith(f"{col}_")]
                            if matching:
                                available_cols.append(matching[0])
                    
                    if len(available_cols) == 3:
                        # Create a clean dataframe with only the columns we need
                        # Use iloc to select by position to avoid any column name issues
                        col_indices = [scatter_df_clean.columns.get_loc(col) for col in available_cols]
                        chart_data = scatter_df_clean.iloc[:, col_indices].copy()
                        
                        # Rename columns to ensure they're unique and match what we expect
                        chart_data.columns = ['Player', 'X_Metric', 'Y_Metric']
                        
                        chart_data = chart_data.dropna()
                        
                        if not chart_data.empty:
                            chart = alt.Chart(chart_data).mark_circle(size=100, opacity=0.6).encode(
                                x=alt.X('X_Metric', title=x_metric),
                                y=alt.Y('Y_Metric', title=y_metric),
                                tooltip=['Player', 'X_Metric', 'Y_Metric'],
                                color=alt.value('#8B0000')
                            ).properties(
                                width=800,
                                height=600
                            ).configure(
                                background='#1e1e1e'
                            ).configure_axis(
                                labelColor='#fafafa',
                                titleColor='#fafafa',
                                gridColor='#4a4a4a'
                            )
                            
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.info("No data available for the selected metrics.")
                    else:
                        st.error(f"Could not find required columns. Available: {list(scatter_df_clean.columns)[:10]}")
                else:
                    st.info("No data available for scatter plot.")
            else:
                st.info("Need at least 2 numeric metrics for scatter plot analysis.")

elif page == "Player Database":
    st.header("👥 Player Database")
    st.markdown("Browse and search all players in the shortlist database.")
    
    if not players_list:
        st.info("No players loaded. Please check that the shortlist file exists.")
    else:
        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("Search Player", "")
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
                                    st.success(f"{len(player_calls)} call(s) logged")
                                    latest_rec = player_calls.iloc[-1]['Recommendation']
                                    st.caption(f"Latest: {latest_rec}")
                            else:
                                st.caption("No calls logged yet")
        else:
            st.info("No players found matching your search criteria.")

elif page == "Scouting Requests":
    st.header("Scouting Requests")
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
            
            submitted = st.form_submit_button("Create Request", use_container_width=True)
            
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
                st.success(f"Request created: {new_request['Request ID']}")
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
                "Download Requests (CSV)",
                filtered_requests.to_csv(index=False),
                file_name=f"scouting_requests_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

elif page == "Video Analysis":
    st.header("Video Analysis")
    st.markdown("Track video review progress for shortlisted players (complements SAP Performance Insights).")
    
    # Create videos directory if it doesn't exist
    videos_dir = DATA_DIR / 'video_uploads'
    videos_dir.mkdir(exist_ok=True)
    
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
    
    tab1, tab2 = st.tabs(["Add Review", "Review Status"])
    
    with tab1:
        st.subheader("Add Video Review")
        st.markdown("Track your analysis of player videos and film. This complements your quantitative scouting data.")
        
        # MP4 File Upload - OUTSIDE FORM so it triggers immediate rerun
        st.markdown("#### Video File Upload")
        st.markdown("Upload MP4 video files downloaded from Wyscout or other sources. Files are stored locally and can be downloaded later.")
        uploaded_video = st.file_uploader(
            "Upload Video File (MP4)",
            type=['mp4'],
            help="Upload MP4 video files. Maximum file size depends on your system settings.",
            key="video_uploader"
        )
        
        # Store uploaded video path in session state (will be saved when form is submitted)
        if uploaded_video is not None:
            # Generate unique filename to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # We'll use a placeholder for player name since it's selected later
            file_extension = uploaded_video.name.split('.')[-1] if '.' in uploaded_video.name else 'mp4'
            video_filename = f"video_{timestamp}.{file_extension}"
            video_file_path = videos_dir / video_filename
            
            # Save the uploaded file immediately (before form submission)
            try:
                uploaded_video_bytes = uploaded_video.getbuffer()
                with open(video_file_path, 'wb') as f:
                    f.write(uploaded_video_bytes)
                st.success(f"Video uploaded: {uploaded_video.name} ({uploaded_video.size / (1024*1024):.2f} MB)")
                # Store path in session state for form submission
                st.session_state['pending_video_path'] = str(video_file_path)
                st.session_state['pending_video_filename'] = uploaded_video.name
            except Exception as e:
                st.error(f"Error saving video file: {e}")
                st.session_state['pending_video_path'] = None
        
        # Video Preview - Show uploaded video immediately so user can watch while filling form
        if uploaded_video is not None:
            st.markdown("---")
            st.markdown("#### Video Preview")
            st.markdown("Watch the video below while filling out the form details.")
            try:
                st.video(uploaded_video)
            except Exception as e:
                st.error(f"Error displaying video preview: {e}")
        elif 'pending_video_path' in st.session_state and st.session_state['pending_video_path']:
            # Show video from previously uploaded file (persists across form interactions)
            st.markdown("---")
            st.markdown("#### Video Preview")
            st.markdown("Watch the video below while filling out the form details.")
            try:
                video_file = Path(st.session_state['pending_video_path'])
                if video_file.exists():
                    with open(video_file, 'rb') as f:
                        video_bytes = f.read()
                    st.video(video_bytes)
                else:
                    st.warning("Video file not found. Please upload again.")
            except Exception as e:
                st.error(f"Error displaying video preview: {e}")
        
        st.markdown("---")
        
        # Player Selection with Filters - MOVED OUTSIDE FORM for reactive updates
        st.markdown("#### Player Selection")
        
        # Get unique conferences, teams, and positions from player_info_dict
        all_conferences = set()
        all_teams = set()
        all_positions = set()
        
        for player_info in player_info_dict.values():
            if player_info.get('conference'):
                all_conferences.add(player_info['conference'])
            if player_info.get('team'):
                all_teams.add(player_info['team'])
            if player_info.get('position'):
                all_positions.add(player_info['position'])
        
        # Filter dropdowns with cascading logic - OUTSIDE FORM so they update reactively
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            filter_conference_video = st.selectbox(
                "Filter by Conference",
                [""] + sorted(list(all_conferences)),
                key="video_filter_conf"
            )
        
        with filter_col2:
            # Team dropdown (filtered by conference) - EXACT same logic as Phone Calls
            if filter_conference_video:
                teams_list = get_teams_by_conference(filter_conference_video)
                # Reset team filter if conference changed and current team not in new list
                current_team = st.session_state.get('video_filter_team', '')
                if current_team and current_team not in teams_list:
                    st.session_state['video_filter_team'] = ''
                    current_team = ''
                
                filter_team_video = st.selectbox(
                    "Filter by Team",
                    [""] + teams_list,
                    key="video_filter_team",
                    index=0 if not current_team else (teams_list.index(current_team) + 1 if current_team in teams_list else 0)
                )
            else:
                st.selectbox("Filter by Team", [""], key="video_filter_team_disabled", disabled=True)
                st.session_state['video_filter_team'] = ''
                filter_team_video = ''
        
        with filter_col3:
            filter_position_video = st.selectbox(
                "Filter by Position Profile",
                [""] + sorted(list(all_positions)),
                key="video_filter_pos"
            )
        
        # Filter players based on selections (cascading: conference -> team -> position)
        filtered_players = players_list.copy()
        if filter_conference_video:
            filtered_players = [p for p in filtered_players if player_info_dict.get(p, {}).get('conference') == filter_conference_video]
        if filter_team_video:
            # Team filter only applies if conference is selected (or if no conference selected, show all teams)
            if filter_conference_video:
                # Team must match AND be in the selected conference
                filtered_players = [p for p in filtered_players if player_info_dict.get(p, {}).get('team') == filter_team_video]
            else:
                # If no conference selected, team filter works independently
                filtered_players = [p for p in filtered_players if player_info_dict.get(p, {}).get('team') == filter_team_video]
        if filter_position_video:
            filtered_players = [p for p in filtered_players if player_info_dict.get(p, {}).get('position') == filter_position_video]
        
        # Player Name dropdown (now shows all filtered players, no limit) - OUTSIDE FORM
        player_name = st.selectbox("Player Name", [""] + sorted(filtered_players), key="video_player_select")
        
        # If player is selected, show their info
        if player_name and player_name in player_info_dict:
            player_info = player_info_dict[player_name]
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                if player_info.get('team'):
                    st.caption(f"**Team:** {player_info['team']}")
            with info_col2:
                if player_info.get('conference'):
                    st.caption(f"**Conference:** {player_info['conference']}")
            with info_col3:
                if player_info.get('position'):
                    st.caption(f"**Position:** {player_info['position']}")
        
        st.markdown("---")
        
        st.markdown("---")
        
        # Performance Assessment - OUTSIDE FORM for reactive updates (like call log)
        st.markdown("#### Performance Assessment")
        st.markdown("Rate the player's performance attributes based on the video review.")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            technical_ability = st.slider("Technical Ability (1-10)", 1, 10, st.session_state.get('video_technical_ability', 5), key="video_technical_slider", help="Ball control, passing, dribbling, shooting technique")
            tactical_awareness = st.slider("Tactical Awareness (1-10)", 1, 10, st.session_state.get('video_tactical_awareness', 5), key="video_tactical_awareness_slider", help="Positioning, reading the game, tactical understanding")
            decision_making = st.slider("Decision Making (1-10)", 1, 10, st.session_state.get('video_decision_making', 5), key="video_decision_slider", help="Speed and quality of decisions under pressure")
        
        with perf_col2:
            physical_attributes = st.slider("Physical Attributes (1-10)", 1, 10, st.session_state.get('video_physical', 5), key="video_physical_slider", help="Speed, strength, endurance, athleticism")
            work_rate = st.slider("Work Rate (1-10)", 1, 10, st.session_state.get('video_work_rate', 5), key="video_work_rate_slider", help="Effort, intensity, off-the-ball movement")
            communication_video = st.slider("Communication (1-10)", 1, 10, st.session_state.get('video_communication', 5), key="video_communication_slider", help="On-field communication, leadership presence")
        
        with perf_col3:
            leadership_video = st.slider("Leadership (1-10)", 1, 10, st.session_state.get('video_leadership', 5), key="video_leadership_slider", help="Leadership on the field, organizing teammates")
            composure = st.slider("Composure (1-10)", 1, 10, st.session_state.get('video_composure', 5), key="video_composure_slider", help="Calmness under pressure, handling mistakes")
            overall_video_rating = st.slider("Overall Video Rating (1-10)", 1, 10, st.session_state.get('video_overall_rating', 5), key="video_overall_rating_slider", help="Overall assessment from video review")
        
        # Store performance values in session state
        st.session_state.video_technical_ability = technical_ability
        st.session_state.video_tactical_awareness = tactical_awareness
        st.session_state.video_decision_making = decision_making
        st.session_state.video_physical = physical_attributes
        st.session_state.video_work_rate = work_rate
        st.session_state.video_communication = communication_video
        st.session_state.video_leadership = leadership_video
        st.session_state.video_composure = composure
        st.session_state.video_overall_rating = overall_video_rating
        
        # Calculate total video score (reactive - updates immediately as sliders change)
        total_video_score = (
            technical_ability + tactical_awareness + decision_making +
            physical_attributes + work_rate + communication_video +
            leadership_video + composure + overall_video_rating
        )
        max_possible = 9 * 10  # 9 metrics * 10 points each
        video_percentage = (total_video_score / max_possible) * 100
        
        # Calculate grade based on percentage (same scale as call log)
        def assign_video_grade_from_percentile(pct):
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
        
        video_grade = assign_video_grade_from_percentile(video_percentage)
        
        # Store video assessment totals in session state for form submission
        st.session_state.video_total_score = total_video_score
        st.session_state.video_percentage = video_percentage
        st.session_state.video_grade = video_grade
        
        # Display score summary (reactive - updates as sliders change)
        st.markdown("#### Video Assessment Summary")
        score_col1, score_col2, score_col3 = st.columns(3)
        with score_col1:
            st.metric("Total Score", f"{total_video_score}/{max_possible}")
        with score_col2:
            st.metric("Percentage", f"{video_percentage:.1f}%")
        with score_col3:
            st.metric("Grade", video_grade)
        
        st.markdown("---")
        
        # Form for review details - filters and performance assessment are now outside
        with st.form("video_review_form"):
            
            # Video Details
            st.markdown("#### Video Details")
            col_vid1, col_vid2 = st.columns(2)
            with col_vid1:
                review_date = st.date_input("Review Date", value=datetime.now().date())
                video_type = st.selectbox("Video Type", ["Game Film", "Highlights", "Training Footage", "Match Replay", "Other"])
            with col_vid2:
                video_source = st.text_input("Video Source", placeholder="e.g., 'Hudl', 'YouTube', 'Team Website', 'Wyscout'")
                video_url = st.text_input("Video URL (Optional)", placeholder="https://...")
            
            games_reviewed = st.text_input("Games/Matches Reviewed", placeholder="e.g., 'vs Duke, vs UNC, vs Stanford'")
            
            st.markdown("#### Analysis")
            col_analysis1, col_analysis2 = st.columns(2)
            with col_analysis1:
                video_score = st.slider("Overall Video Score (1-10)", 1, 10, st.session_state.get('video_score', 5), key="video_score_slider", help="Your overall assessment from watching the video")
                status = st.selectbox("Review Status", ["Not Started", "In Progress", "Complete"])
            with col_analysis2:
                quantitative_match = st.selectbox("Quantitative Match", ["Strong Match", "Mostly Match", "Some Discrepancies", "Significant Discrepancies"], help="How well does the video match the player's stats?")
            
            # Store video_score in session state
            st.session_state.video_score = video_score
            
            st.markdown("#### Observations")
            key_observations = st.text_area("Key Observations", placeholder="Main takeaways from video review - what stood out?")
            strengths_video = st.text_area("Strengths Identified", placeholder="What strengths did you observe in the video?")
            weaknesses_video = st.text_area("Weaknesses Identified", placeholder="What weaknesses or areas for improvement did you notice?")
            red_flags_video = st.text_area("Red Flags from Video", placeholder="Any concerns observed (injuries, attitude, etc.)")
            
            st.markdown("#### Assessment")
            recommendation_video = st.selectbox("Recommendation", ["Strong Yes", "Yes", "Maybe", "No", "Strong No"])
            notes = st.text_area("Additional Notes", placeholder="Any other observations or notes about the video review")
            
            submitted = st.form_submit_button("Save Review", use_container_width=True)
            
            if submitted and player_name:
                # Get video file path from session state (saved during upload)
                saved_video_path = st.session_state.get('pending_video_path', None)
                
                # If video was uploaded, rename it with player name now that we know it
                if saved_video_path and player_name:
                    try:
                        old_path = Path(saved_video_path)
                        if old_path.exists():
                            # Rename file to include player name
                            safe_player_name = player_name.replace('/', '_').replace('\\', '_')
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            file_extension = old_path.suffix or '.mp4'
                            new_filename = f"{safe_player_name}_{timestamp}{file_extension}"
                            new_path = videos_dir / new_filename
                            old_path.rename(new_path)
                            saved_video_path = str(new_path)
                            st.session_state['pending_video_path'] = saved_video_path
                    except Exception as e:
                        st.warning(f"Could not rename video file: {e}")
                
                new_review = {
                    'Player Name': player_name,
                    'Review Date': review_date.strftime('%Y-%m-%d'),
                    'Video Type': video_type,
                    'Video Source': video_source,
                    'Video URL': video_url,
                    'Video File Path': saved_video_path if saved_video_path else '',
                    'Games Reviewed': games_reviewed,
                    'Video Score': video_score,
                    'Status': status,
                    'Quantitative Match': quantitative_match,
                    'Technical Ability': technical_ability,
                    'Tactical Awareness': tactical_awareness,
                    'Decision Making': decision_making,
                    'Physical Attributes': physical_attributes,
                    'Work Rate': work_rate,
                    'Communication': communication_video,
                    'Leadership': leadership_video,
                    'Composure': composure,
                    'Overall Video Rating': overall_video_rating,
                    'Total Video Score': st.session_state.get('video_total_score', 45),
                    'Video Percentage': round(st.session_state.get('video_percentage', 50.0), 1),
                    'Video Grade': st.session_state.get('video_grade', 'F'),
                    'Key Observations': key_observations,
                    'Strengths Identified': strengths_video,
                    'Weaknesses Identified': weaknesses_video,
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
                
                # Clear the pending video path after saving
                if 'pending_video_path' in st.session_state:
                    del st.session_state['pending_video_path']
                if 'pending_video_filename' in st.session_state:
                    del st.session_state['pending_video_filename']
                
                st.success(f"Review saved for {player_name}")
                if saved_video_path:
                    st.info(f"Video file saved: {Path(saved_video_path).name}")
    
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
            
            # Add Conference, Team, and Position Profile columns based on Player Name
            reviews_df = st.session_state.video_reviews.copy()
            
            # Enrich with player info - try exact match first, then case-insensitive, then partial match
            if 'Player Name' in reviews_df.columns and player_info_dict:
                def get_player_info(player_name):
                    """Get player info with flexible matching"""
                    if not player_name or pd.isna(player_name):
                        return '', '', ''
                    
                    player_name_str = str(player_name).strip()
                    
                    # Try exact match first
                    if player_name_str in player_info_dict:
                        info = player_info_dict[player_name_str]
                        return (
                            info.get('conference', ''),
                            info.get('team', ''),
                            info.get('position', '')
                        )
                    
                    # Try case-insensitive match
                    for key, info in player_info_dict.items():
                        key_str = str(key).strip()
                        if key_str.lower() == player_name_str.lower():
                            return (
                                info.get('conference', ''),
                                info.get('team', ''),
                                info.get('position', '')
                            )
                    
                    # Try partial match (if player name contains key or vice versa)
                    for key, info in player_info_dict.items():
                        key_str = str(key).strip()
                        if (player_name_str.lower() in key_str.lower() or 
                            key_str.lower() in player_name_str.lower()):
                            return (
                                info.get('conference', ''),
                                info.get('team', ''),
                                info.get('position', '')
                            )
                    
                    return '', '', ''
                
                # Apply enrichment
                enrichment_results = reviews_df['Player Name'].apply(get_player_info)
                reviews_df['Conference'] = enrichment_results.apply(lambda x: x[0])
                reviews_df['Team'] = enrichment_results.apply(lambda x: x[1])
                reviews_df['Position Profile'] = enrichment_results.apply(lambda x: x[2])
                
                # Debug: Show enrichment stats if no matches found
                enriched_count = len(reviews_df[(reviews_df['Conference'] != '') | (reviews_df['Team'] != '') | (reviews_df['Position Profile'] != '')])
                if enriched_count == 0 and len(reviews_df) > 0:
                    # Show debug info if no matches found
                    with st.expander("🔍 Debug: Player Name Matching", expanded=False):
                        st.write(f"Total reviews: {len(reviews_df)}")
                        st.write(f"Reviews with player info: {enriched_count}")
                        st.write(f"player_info_dict size: {len(player_info_dict) if player_info_dict else 0}")
                        st.write("Sample player names from reviews:")
                        sample_names = reviews_df['Player Name'].head(5).tolist()
                        for name in sample_names:
                            st.write(f"  - '{name}' (type: {type(name).__name__})")
                        if player_info_dict:
                            st.write("Sample player names from player_info_dict:")
                            sample_dict_names = list(player_info_dict.keys())[:5]
                            for name in sample_dict_names:
                                st.write(f"  - '{name}' (type: {type(name).__name__})")
                        else:
                            st.warning("⚠️ player_info_dict is empty or not loaded! Please upload the player database in the sidebar.")
            elif 'Player Name' in reviews_df.columns and not player_info_dict:
                # Initialize empty columns if player_info_dict is not loaded
                reviews_df['Conference'] = ''
                reviews_df['Team'] = ''
                reviews_df['Position Profile'] = ''
                st.warning("⚠️ Player database not loaded. Please upload the player database in the sidebar to enable filtering by Conference, Team, and Position Profile.")
            
            # Filter dropdowns
            st.markdown("### Filters")
            filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
            
            with filter_col1:
                # Status filter
                status_options = ['All'] + sorted([s for s in reviews_df['Status'].unique() if pd.notna(s) and str(s).strip()])
                selected_status = st.selectbox(
                    "Status",
                    status_options,
                    key="review_status_filter"
                )
            
            with filter_col2:
                # Conference filter
                conference_options = ['All'] + sorted([c for c in reviews_df['Conference'].unique() if pd.notna(c) and str(c).strip()])
                selected_conference = st.selectbox(
                    "Conference",
                    conference_options,
                    key="review_conference_filter"
                )
            
            with filter_col3:
                # Team filter (cascading from conference)
                if selected_conference and selected_conference != 'All':
                    available_teams = sorted([t for t in reviews_df[reviews_df['Conference'] == selected_conference]['Team'].unique() if pd.notna(t) and str(t).strip()])
                else:
                    available_teams = sorted([t for t in reviews_df['Team'].unique() if pd.notna(t) and str(t).strip()])
                team_options = ['All'] + available_teams
                selected_team = st.selectbox(
                    "Team",
                    team_options,
                    key="review_team_filter"
                )
            
            with filter_col4:
                # Position Profile filter
                position_options = ['All'] + sorted([p for p in reviews_df['Position Profile'].unique() if pd.notna(p) and str(p).strip()])
                selected_position = st.selectbox(
                    "Position Profile",
                    position_options,
                    key="review_position_filter"
                )
            
            with filter_col5:
                # Player filter
                player_options = ['All'] + sorted([p for p in reviews_df['Player Name'].unique() if pd.notna(p) and str(p).strip()])
                selected_player = st.selectbox(
                    "Player",
                    player_options,
                    key="review_player_filter"
                )
            
            # Apply filters
            filtered_reviews = reviews_df.copy()
            
            if selected_status and selected_status != 'All':
                filtered_reviews = filtered_reviews[filtered_reviews['Status'] == selected_status]
            
            if selected_conference and selected_conference != 'All':
                filtered_reviews = filtered_reviews[filtered_reviews['Conference'] == selected_conference]
            
            if selected_team and selected_team != 'All':
                filtered_reviews = filtered_reviews[filtered_reviews['Team'] == selected_team]
            
            if selected_position and selected_position != 'All':
                filtered_reviews = filtered_reviews[filtered_reviews['Position Profile'] == selected_position]
            
            if selected_player and selected_player != 'All':
                filtered_reviews = filtered_reviews[filtered_reviews['Player Name'] == selected_player]
            
            # Update summary metrics based on filtered data
            filtered_total = len(filtered_reviews)
            filtered_complete = len(filtered_reviews[filtered_reviews['Status'] == 'Complete'])
            filtered_in_progress = len(filtered_reviews[filtered_reviews['Status'] == 'In Progress'])
            filtered_avg_score = filtered_reviews['Video Score'].mean() if 'Video Score' in filtered_reviews.columns and not filtered_reviews.empty else 0
            
            # Show filtered count
            if filtered_total != total_reviews:
                st.info(f"Showing {filtered_total} of {total_reviews} reviews")
            
            # Reviews table with color-coded rows by status
            st.markdown("### All Reviews")
            
            if filtered_reviews.empty:
                st.warning("No reviews match the selected filters.")
            else:
                # Format date columns
                if 'Review Date' in filtered_reviews.columns:
                    try:
                        filtered_reviews['Review Date'] = pd.to_datetime(filtered_reviews['Review Date'], errors='coerce')
                        filtered_reviews['Review Date'] = filtered_reviews['Review Date'].dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                if 'Created At' in filtered_reviews.columns:
                    try:
                        filtered_reviews['Created At'] = pd.to_datetime(filtered_reviews['Created At'], errors='coerce')
                        filtered_reviews['Created At'] = filtered_reviews['Created At'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
            
                # Prepare table data
                table_data = filtered_reviews.to_dict('records')
                table_columns = list(filtered_reviews.columns)
            
                # Build HTML table with color-coded rows
                html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: transparent;
                        color: #fafafa;
                    }}
                    .table-wrapper {{
                        background: #1e1e1e;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                    }}
                    .table-container {{
                        overflow-x: auto;
                        max-height: 500px;
                        overflow-y: auto;
                    }}
                    .table-container::-webkit-scrollbar {{
                        width: 8px;
                        height: 8px;
                    }}
                    .table-container::-webkit-scrollbar-track {{
                        background: #1e1e1e;
                    }}
                    .table-container::-webkit-scrollbar-thumb {{
                        background: #3a3a3a;
                        border-radius: 4px;
                    }}
                    .table-container::-webkit-scrollbar-thumb:hover {{
                        background: #4a4a4a;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: separate;
                        border-spacing: 0;
                        background-color: transparent;
                    }}
                    thead {{
                        position: sticky;
                        top: 0;
                        z-index: 100;
                    }}
                    th {{
                        background: linear-gradient(180deg, #2d2d2d 0%, #1e1e1e 100%);
                        color: #ffffff;
                        padding: 8px 12px;
                        text-align: left;
                        border-bottom: 2px solid #8B0000;
                        font-weight: 600;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        white-space: nowrap;
                    }}
                    tbody tr {{
                        background-color: #000000;
                        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
                    }}
                    tbody tr.status-complete {{
                        background-color: rgba(34, 139, 34, 0.2) !important;
                        border-left: 3px solid #228B22;
                    }}
                    tbody tr.status-complete:hover {{
                        background-color: rgba(34, 139, 34, 0.3) !important;
                        transform: translateX(2px);
                    }}
                    tbody tr.status-in-progress {{
                        background-color: rgba(255, 193, 7, 0.2) !important;
                        border-left: 3px solid #FFC107;
                    }}
                    tbody tr.status-in-progress:hover {{
                        background-color: rgba(255, 193, 7, 0.3) !important;
                        transform: translateX(2px);
                    }}
                    tbody tr.status-not-started {{
                        background-color: rgba(220, 53, 69, 0.2) !important;
                        border-left: 3px solid #DC3545;
                    }}
                    tbody tr.status-not-started:hover {{
                        background-color: rgba(220, 53, 69, 0.3) !important;
                        transform: translateX(2px);
                    }}
                    tbody tr:nth-child(even) {{
                        opacity: 0.95;
                    }}
                    td {{
                        padding: 8px 12px;
                        border-bottom: 1px solid rgba(58, 58, 58, 0.5);
                        max-width: 200px;
                        word-wrap: break-word;
                        color: #e0e0e0;
                        font-size: 0.8125rem;
                    }}
                    tbody td {{
                        font-weight: 700 !important;
                    }}
                    tbody tr:last-child td {{
                        border-bottom: none;
                    }}
                    .url-cell {{
                        position: relative;
                        cursor: pointer;
                    }}
                    .url-cell .url-text {{
                        color: #ffffff;
                        text-decoration: underline;
                        cursor: pointer;
                        white-space: nowrap;
                    }}
                    .url-cell .url-text:hover {{
                        color: #D10023;
                        text-decoration-color: #D10023;
                    }}
                    .url-cell .url-text:active {{
                        opacity: 0.7;
                    }}
                </style>
                <script>
                    function copyUrlToClipboard(text, element) {{
                        navigator.clipboard.writeText(text).then(function() {{
                            // Show temporary feedback
                            const originalColor = element.style.color;
                            element.style.color = '#228B22';
                            element.textContent = 'Copied!';
                            setTimeout(function() {{
                                element.style.color = originalColor;
                                element.textContent = 'Copy';
                            }}, 1500);
                        }}, function(err) {{
                            console.error('Failed to copy: ', err);
                            element.style.color = '#DC3545';
                            element.textContent = 'Copy failed';
                            setTimeout(function() {{
                                element.style.color = '#ffffff';
                                element.textContent = 'Copy';
                            }}, 2000);
                        }});
                    }}
                </script>
            </head>
            <body>
                <div class="table-wrapper">
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    {' '.join([f'<th>{col}</th>' for col in table_columns])}
                                </tr>
                            </thead>
                            <tbody>
            """
            
                # Add table rows with status-based classes
                for row in table_data:
                    status = str(row.get('Status', '')).lower().replace(' ', '-')
                    status_class = f"status-{status}" if status else ""
                    html_code += f'<tr class="{status_class}">'
                    for col in table_columns:
                        cell_value = row.get(col, '')
                        if pd.isna(cell_value):
                            cell_value = ''
                        else:
                            cell_value = str(cell_value)
                        
                        # Check if this is a Video URL column and contains a URL
                        is_url_column = 'url' in col.lower() and ('http' in str(cell_value).lower() or 'www.' in str(cell_value).lower())
                        
                        # Check if this is a Video File Path column
                        is_file_path_column = 'file path' in col.lower() or 'filepath' in col.lower()
                        
                        if (is_url_column or is_file_path_column) and cell_value and str(cell_value).strip():
                            # Make URL/File Path clickable to copy (no hyperlink)
                            path_value = str(cell_value).strip()
                            # Escape for JavaScript (but display "Copy" instead of the full path)
                            escaped_js = path_value.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                            html_code += f'<td class="url-cell"><span class="url-text" onclick="copyUrlToClipboard(\'{escaped_js}\', this)">Copy</span></td>'
                        else:
                            # Regular cell
                            escaped_cell = str(cell_value).replace('<', '&lt;').replace('>', '&gt;')
                            html_code += f"<td>{escaped_cell}</td>"
                html_code += "</tr>"
            
            html_code += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </body>
                </html>
                """
                
            components.html(html_code, height=550, scrolling=True)
            
            # Display videos in expandable sections
            if not filtered_reviews.empty and 'Video File Path' in filtered_reviews.columns:
                    st.markdown("### Uploaded Video Files")
                    st.markdown("View and download uploaded video files below.")
                    
                    for idx, row in filtered_reviews.iterrows():
                        video_path = row.get('Video File Path', '')
                        if video_path and pd.notna(video_path) and str(video_path).strip():
                            video_file = Path(video_path)
                            if video_file.exists():
                                with st.expander(f"📹 {row.get('Player Name', 'Unknown')} - {row.get('Review Date', 'Unknown')} ({row.get('Video Type', 'N/A')})", expanded=False):
                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.markdown(f"**Player:** {row.get('Player Name', 'N/A')}")
                                        st.markdown(f"**Review Date:** {row.get('Review Date', 'N/A')}")
                                        st.markdown(f"**Video Type:** {row.get('Video Type', 'N/A')}")
                                        st.markdown(f"**Source:** {row.get('Video Source', 'N/A')}")
                                        if row.get('Games Reviewed'):
                                            st.markdown(f"**Games Reviewed:** {row.get('Games Reviewed', 'N/A')}")
                                    
                                    with col2:
                                        # Video download button
                                        try:
                                            with open(video_file, 'rb') as f:
                                                video_bytes = f.read()
                                            file_size_mb = len(video_bytes) / (1024 * 1024)
                                            st.download_button(
                                                "⬇️ Download Video",
                                                video_bytes,
                                                file_name=video_file.name,
                                                mime="video/mp4",
                                                key=f"download_video_{idx}",
                                                use_container_width=True
                                            )
                                            st.caption(f"File size: {file_size_mb:.2f} MB")
                                        except Exception as e:
                                            st.error(f"Error loading video: {e}")
                                    
                                    # Video player
                                    st.markdown("---")
                                    st.markdown("**Video Preview:**")
                                    try:
                                        with open(video_file, 'rb') as f:
                                            video_bytes = f.read()
                                        st.video(video_bytes)
                                    except Exception as e:
                                        st.error(f"Error displaying video: {e}")
                                    
                                    # Show review details if available
                                    if row.get('Key Observations'):
                                        st.markdown("---")
                                        st.markdown("**Key Observations:**")
                                        st.info(row.get('Key Observations', ''))
    
elif page == "To Do List":
    st.header("To Do List")
    
    # Refresh call log from file
    st.session_state.call_log = load_call_log()
    
    # Initialize todo list in session state
    if "todo_list" not in st.session_state:
        st.session_state.todo_list = []
    
    # Auto-gather tasks from "Follow-up Needed" calls
    if not st.session_state.call_log.empty and 'Follow-up Needed' in st.session_state.call_log.columns:
        followup_calls = st.session_state.call_log[st.session_state.call_log['Follow-up Needed'] == True]
        
        auto_tasks = []
        for idx, row in followup_calls.iterrows():
            player_name = row.get('Player Name', 'Unknown')
            call_date = row.get('Call Date', 'Unknown')
            action_items = row.get('Action Items', '')
            followup_date = row.get('Follow-up Date', '')
            
            task_text = f"Follow-up with {player_name}"
            if action_items and pd.notna(action_items) and str(action_items).strip():
                task_text += f": {str(action_items)[:100]}"
            
            task_id = f"auto_{idx}"
            auto_tasks.append({
                'id': task_id,
                'text': task_text,
                'player': player_name,
                'call_date': call_date,
                'followup_date': followup_date,
                'source': 'auto',
                'completed': False
            })
        
        # Merge auto tasks with existing todos (avoid duplicates)
        existing_auto_ids = [t.get('id', '') for t in st.session_state.todo_list if t.get('source') == 'auto']
        new_auto_tasks = [t for t in auto_tasks if t['id'] not in existing_auto_ids]
        st.session_state.todo_list.extend(new_auto_tasks)
    
    # Display todos
    st.markdown("### Your Tasks")
    
    # Filter options
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        show_completed = st.checkbox("Show Completed", value=False)
    with filter_col2:
        filter_source = st.selectbox("Filter by Source", ["All", "Auto-generated", "Manual"])
    
    # Filter todos
    filtered_todos = st.session_state.todo_list.copy()
    if not show_completed:
        filtered_todos = [t for t in filtered_todos if not t.get('completed', False)]
    if filter_source == "Auto-generated":
        filtered_todos = [t for t in filtered_todos if t.get('source') == 'auto']
    elif filter_source == "Manual":
        filtered_todos = [t for t in filtered_todos if t.get('source') == 'manual']
    
    # Display todos
    if not filtered_todos:
        st.info("No tasks to display. Add a task below or check for follow-up calls.")
    else:
        for i, task in enumerate(filtered_todos):
            with st.container():
                col1, col2, col3 = st.columns([1, 10, 1])
                with col1:
                    task_completed = st.checkbox("", value=task.get('completed', False), key=f"todo_check_{task.get('id', i)}")
                    if task_completed != task.get('completed', False):
                        task['completed'] = task_completed
                        st.rerun()
                with col2:
                    task_text_style = "text-decoration: line-through; opacity: 0.6;" if task.get('completed', False) else ""
                    source_badge = "🤖 Auto" if task.get('source') == 'auto' else "✏️ Manual"
                    st.markdown(f'<p style="{task_text_style}">{source_badge} - {task.get("text", "Task")}</p>', unsafe_allow_html=True)
                    if task.get('player'):
                        st.caption(f"Player: {task.get('player')} | Call Date: {task.get('call_date', 'N/A')}")
                with col3:
                    if st.button("Delete", key=f"delete_{task.get('id', i)}"):
                        st.session_state.todo_list = [t for t in st.session_state.todo_list if t.get('id') != task.get('id')]
                        st.rerun()
                st.markdown("---")
    
    # Add new task
    st.markdown("### Add New Task")
    new_task_text = st.text_input("Task Description", key="new_task_input")
    col_add1, col_add2 = st.columns([3, 1])
    with col_add1:
        new_task_player = st.text_input("Player Name (optional)", key="new_task_player")
    with col_add2:
        if st.button("Add Task", use_container_width=True):
            if new_task_text.strip():
                new_task = {
                    'id': f"manual_{datetime.now().timestamp()}",
                    'text': new_task_text,
                    'player': new_task_player if new_task_player.strip() else None,
                    'call_date': None,
                    'followup_date': None,
                    'source': 'manual',
                    'completed': False
                }
                st.session_state.todo_list.append(new_task)
                st.rerun()
            else:
                st.warning("Please enter a task description.")

# FAQs page removed - now available in sidebar under Tips & Help

elif page == "Export to SAP":
    st.header("Export to SAP")
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
                    "Download SAP Format (CSV)",
                    sap_df.to_csv(index=False),
                    file_name=f"sap_call_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                st.info("This format uses SAP-friendly column names (underscores, no spaces).")
            else:
                st.download_button(
                    f"Download {format_option}",
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
                "Download Player Database (CSV)",
                player_db_df.to_csv(index=False),
                file_name=f"sap_player_database_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif export_type == "Video Reviews":
        if 'video_reviews' in st.session_state and not st.session_state.video_reviews.empty:
            st.subheader("Video Reviews Export")
            st.write(f"**Total Reviews**: {len(st.session_state.video_reviews)}")
            st.download_button(
                "Download Video Reviews (CSV)",
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
                "Download Scouting Requests (CSV)",
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
        
        st.info("Use individual exports above for specific data types, or combine manually in Excel/SAP.")

elif page == "Export Data":
    st.header("Export Data")
    
    if st.session_state.call_log.empty:
        st.info("No data to export.")
    else:
        st.download_button(
            "Download Full Call Log (CSV)",
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
            "Download Full Call Log (Excel)",
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
    st.title("Player Overview PDF Viewer")
    st.markdown("View player overview PDFs generated from the scouting system.")
    
    # PDF uploader
    st.markdown("### Upload Player Overview PDFs")
    uploaded_pdfs = st.file_uploader(
        "Upload player overview PDFs",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more player overview PDF files. They will be saved to the overview directory."
    )
    
    if uploaded_pdfs:
        # Ensure overview directory exists
        OVERVIEW_DIR.mkdir(parents=True, exist_ok=True)
        
        uploaded_count = 0
        for uploaded_pdf in uploaded_pdfs:
            # Save to overview directory (flat structure for uploaded files)
            pdf_path = OVERVIEW_DIR / uploaded_pdf.name
            with open(pdf_path, 'wb') as f:
                f.write(uploaded_pdf.getbuffer())
            uploaded_count += 1
        
        if uploaded_count > 0:
            st.success(f"Uploaded {uploaded_count} PDF file(s)")
            st.rerun()
    
    st.markdown("---")
    
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
        # Also include PDFs directly in OVERVIEW_DIR (uploaded files)
        for pdf_file in OVERVIEW_DIR.glob('*.pdf'):
            pdf_files.append({
                'path': pdf_file,
                'name': pdf_file.stem,
                'position': 'Uploaded',
                'type': 'Direct'
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
                            label="Download PDF",
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
        st.warning("No player overview PDFs found. Please generate overviews first.")
        st.info("PDFs should be located in: `Player Overviews/Top 15/` or `Player Overviews/Other/`")

elif page == "Update Player Overviews":
    st.header("Update Player Overviews with Call Data")
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
            st.success(f"Found {len(players_with_calls)} players with call data")
            
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
            
            if st.button("Regenerate Player Overview(s)", use_container_width=True):
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
                                    st.success(f"Overview regenerated for {selected_player}")
                                    st.info("The overview PDF now includes call notes and assessments")
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
                                        st.success(f"Overview regenerated")
                                        st.info("The overview PDF now includes call notes and assessments")
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
                                    st.success(f"Regenerated player overviews with call data")
                                    st.info("All overview PDFs now include call notes and assessments where available")
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
                                        st.success(f"Regenerated all player overviews")
                                        st.info("All overview PDFs now include call notes and assessments where available")
                                else:
                                    st.error(f"❌ Script not found")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            st.code(str(e))
                else:
                    st.warning("Please select a player or choose 'All Players with Calls'")
            
            st.markdown("---")
            st.markdown("""
            **How it works:**
            1. The script finds all players with call log entries
            2. It regenerates their overview PDFs using the existing generation script
            3. The enhanced PDFs include a new "Call Notes & Assessment" section
            4. All existing quantitative data is preserved
            """)
        else:
            st.warning("No players with call data found. Log some calls first!")
    else:
        st.warning("Call log file not found. Please log some calls first.")

# Player Overview PDF Viewer Page
elif page == "View Player Overview":
    st.title("Player Overview PDF Viewer")
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
                            label="Download PDF",
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
        st.warning("No player overview PDFs found. Please generate overviews first.")
        st.info("PDFs should be located in: `Player Overviews/Top 15/` or `Player Overviews/Other/`")

# Footer
st.markdown("---")
st.caption("Portland Thorns Scouting System | Data stored locally in CSV format")

