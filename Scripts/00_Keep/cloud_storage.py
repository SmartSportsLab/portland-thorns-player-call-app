#!/usr/bin/env python3
"""
Cloud storage utilities for syncing call logs and PDFs to Google Drive.
Enables multi-device access and team collaboration.
"""

import os
from pathlib import Path
from io import BytesIO
import streamlit as st

# Google Drive API imports (optional - only if credentials are available)
GOOGLE_DRIVE_AVAILABLE = False
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# OAuth 2.0 scopes for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_google_drive_service():
    """Initialize and return Google Drive service."""
    if not GOOGLE_DRIVE_AVAILABLE:
        return None
    
    try:
        # Check for credentials in Streamlit secrets
        if 'google_drive' in st.secrets:
            creds_info = st.secrets['google_drive']
            # Initialize credentials from secrets
            # Note: This is a simplified version - full OAuth flow would be needed for production
            return None  # Placeholder - implement full OAuth flow
        return None
    except Exception as e:
        st.error(f"Error initializing Google Drive service: {e}")
        return None

def upload_file_to_drive(file_path, folder_id=None, service=None):
    """
    Upload a file to Google Drive.
    
    Args:
        file_path: Path to file to upload
        folder_id: Optional Google Drive folder ID
        service: Google Drive service instance
    
    Returns:
        File ID if successful, None otherwise
    """
    if not GOOGLE_DRIVE_AVAILABLE or not service:
        return None
    
    try:
        file_metadata = {
            'name': Path(file_path).name
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except HttpError as e:
        st.error(f"Error uploading to Google Drive: {e}")
        return None

def upload_bytes_to_drive(file_bytes, file_name, folder_id=None, service=None):
    """
    Upload bytes data to Google Drive.
    
    Args:
        file_bytes: BytesIO object or bytes
        file_name: Name for the file in Drive
        folder_id: Optional Google Drive folder ID
        service: Google Drive service instance
    
    Returns:
        File ID if successful, None otherwise
    """
    if not GOOGLE_DRIVE_AVAILABLE or not service:
        return None
    
    try:
        if isinstance(file_bytes, BytesIO):
            file_bytes.seek(0)
        
        file_metadata = {
            'name': file_name
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaIoBaseUpload(file_bytes, mimetype='application/octet-stream', resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except HttpError as e:
        st.error(f"Error uploading to Google Drive: {e}")
        return None

def sync_call_log_to_cloud(call_log_path, service=None):
    """Sync call log CSV to cloud storage."""
    if not service:
        return False
    
    try:
        file_id = upload_file_to_drive(call_log_path, service=service)
        return file_id is not None
    except Exception as e:
        st.error(f"Error syncing call log: {e}")
        return False

def sync_pdf_to_cloud(pdf_path, service=None):
    """Sync PDF file to cloud storage."""
    if not service:
        return False
    
    try:
        file_id = upload_file_to_drive(pdf_path, service=service)
        return file_id is not None
    except Exception as e:
        st.error(f"Error syncing PDF: {e}")
        return False

def check_cloud_sync_status():
    """Check if cloud sync is configured and available."""
    return GOOGLE_DRIVE_AVAILABLE and 'google_drive' in st.secrets

