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
        'log_new_call': 'Log New Call',
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
        'timeline': 'Timeline',
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
# Check if we're in the expected local directory structure
_local_base = _script_dir.parent.parent.parent.parent
if _local_base.exists() and (_local_base / 'Portland Thorns 2025 Long Shortlist.xlsx').exists():
    # Local development - use detected path
    BASE_DIR = _local_base
else:
    # Streamlit Cloud or other environment - use current directory
    BASE_DIR = Path('.')

DATA_DIR = BASE_DIR / 'Qualitative_Data'
# Create directory and parents if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
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

# File uploader for player database (always show, but highlight if file exists)
st.sidebar.markdown("### 📁 Upload Player Database")
uploaded_file = st.sidebar.file_uploader(
    "Upload player database (Excel file)",
    type=['xlsx', 'xls'],
    help="Upload a shortlist or conference report Excel file. Files are saved permanently."
)

if uploaded_file is not None:
    # Save uploaded file to DATA_DIR (persistent storage)
    uploaded_path = DATA_DIR / uploaded_file.name
    with open(uploaded_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    # Clear cache to reload with new file
    load_player_database.clear()
    load_player_info.clear()
    st.sidebar.success(f"✅ Uploaded and saved: {uploaded_file.name}")
    st.rerun()

# Check if uploaded file exists
UPLOADED_PLAYER_FILE = None
if PLAYER_DB_FILE and PLAYER_DB_FILE.exists() and DATA_DIR in PLAYER_DB_FILE.parents:
    UPLOADED_PLAYER_FILE = PLAYER_DB_FILE

# Display loading status in sidebar
if PLAYER_DB_FILE and PLAYER_DB_FILE.exists():
    file_source = "uploaded" if UPLOADED_PLAYER_FILE else "local"
    st.sidebar.success(f"✅ Loaded {len(players_list)} players from:\n`{PLAYER_DB_FILE.name}` ({file_source})")

# Quick Start Guide in Sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown(f"### 🚀 {t('quick_start')}")
    with st.expander(f"📖 {t('how_to_use')}", expanded=False):
        st.markdown(f"""
        **{t('step1')}**
        - {t('step1_desc')}
        
        **{t('step2')}**
        - {t('step2_desc')}
        
        **{t('step3')}**
        - {t('step3_desc')}
        
        **{t('step4')}**
        - {t('step4_desc')}
        """)
    st.markdown("---")

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

# Main app
st.title(f"⚽ {t('title')}")
st.markdown("---")

# Initialize welcome state
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

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
    
    # Show welcome only on Log New Call page
    if st.session_state.show_welcome:
        with st.expander(f"👋 {t('welcome_title')}", expanded=True):
            st.markdown(f"""
            ### {t('what_app_does')}
            
            {t('what_app_does_desc')}
            
            - **📞 {t('log_calls')}**
            - **📊 {t('track_assessments')}**
            - **📄 {t('generate_reports')}**
            - **🔍 {t('view_history')}**
            - **📈 {t('player_overviews')}**
            
            ### {t('first_steps')}
            
            1. **{t('upload_database')}**
               - {t('upload_database_desc')}
            
            2. **{t('log_first_call')}**
               - {t('log_first_call_desc')}
            
            3. **{t('explore_features')}**
               - {t('explore_features_desc')}
            
            ### {t('tips')}
            
            - 💾 {t('save_draft_tip')}
            - 🔍 {t('search_tip')}
            - 📥 {t('download_tip')}
            - 🔄 {t('autopopulate_tip')}
            
            **{t('ready_to_start')}**
            """)
            
            if st.button(t('got_it'), key="hide_welcome_log"):
                st.session_state.show_welcome = False
                st.rerun()
        
        st.markdown("---")
    
    st.header(f"📞 {t('log_new_call')}")
    
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
        col_search, col_select = st.columns([2, 3])
        with col_search:
            player_search = st.text_input(f"🔍 {t('search_player')}", key="player_search")
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
    
    st.markdown("---")
    
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
    red_flags = st.text_area(t('red_flags'), placeholder=t('any_concerns'))
    
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
    
    # Sticky Save Draft button in sidebar (always visible as user scrolls)
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 💾 {t('save_progress')}")
        if st.button(f"💾 {t('save_draft')}", key="save_draft_btn", use_container_width=True, help="Save your progress without submitting. Data will be restored when you return."):
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
        submitted = st.form_submit_button(f"💾 {t('save_call_log')}", use_container_width=True)
        
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
    
    # PDF uploader
    st.markdown("### 📁 Upload Player Overview PDFs")
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
            st.success(f"✅ Uploaded {uploaded_count} PDF file(s)")
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

