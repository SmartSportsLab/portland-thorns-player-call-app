#!/usr/bin/env python3
"""
Calendar integration utilities for syncing next call dates with Google Calendar and Outlook.
"""

import streamlit as st
from datetime import datetime, timedelta

# Google Calendar API imports (optional)
GOOGLE_CALENDAR_AVAILABLE = False
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

# Microsoft Graph API imports (optional)
OUTLOOK_AVAILABLE = False
try:
    from msal import ConfidentialClientApplication
    import requests
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

def create_google_calendar_event(player_name, call_date, notes="", service=None):
    """
    Create a Google Calendar event for a player call.
    
    Args:
        player_name: Name of the player
        call_date: datetime object for the call
        notes: Additional notes for the event
        service: Google Calendar service instance
    
    Returns:
        Event ID if successful, None otherwise
    """
    if not GOOGLE_CALENDAR_AVAILABLE or not service:
        return None
    
    try:
        event = {
            'summary': f'Call with {player_name}',
            'description': notes if notes else f'Follow-up call with {player_name}',
            'start': {
                'dateTime': call_date.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': (call_date + timedelta(hours=1)).isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},  # 30 min before
                ],
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event.get('id')
    except HttpError as e:
        st.error(f"Error creating Google Calendar event: {e}")
        return None

def create_outlook_calendar_event(player_name, call_date, notes="", access_token=None):
    """
    Create an Outlook Calendar event for a player call.
    
    Args:
        player_name: Name of the player
        call_date: datetime object for the call
        notes: Additional notes for the event
        access_token: Microsoft Graph API access token
    
    Returns:
        Event ID if successful, None otherwise
    """
    if not OUTLOOK_AVAILABLE or not access_token:
        return None
    
    try:
        url = "https://graph.microsoft.com/v1.0/me/events"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        event = {
            'subject': f'Call with {player_name}',
            'body': {
                'contentType': 'text',
                'content': notes if notes else f'Follow-up call with {player_name}'
            },
            'start': {
                'dateTime': call_date.isoformat(),
                'timeZone': 'America/Los_Angeles'
            },
            'end': {
                'dateTime': (call_date + timedelta(hours=1)).isoformat(),
                'timeZone': 'America/Los_Angeles'
            },
            'isReminderOn': True,
            'reminderMinutesBeforeStart': 30
        }
        
        response = requests.post(url, headers=headers, json=event)
        if response.status_code == 201:
            return response.json().get('id')
        else:
            st.error(f"Error creating Outlook event: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error creating Outlook Calendar event: {e}")
        return None

def check_calendar_available():
    """Check if calendar integration is available."""
    return {
        'google': GOOGLE_CALENDAR_AVAILABLE,
        'outlook': OUTLOOK_AVAILABLE
    }

