#!/usr/bin/env python3
"""
Clean Non-Conference Files
==========================

Removes rows from non-conference export files where the team doesn't match
the expected team name (based on the filename).

Specifically removes errant teams like "UNC Asheville Bulldogs" from files
where they don't belong.

Usage:
    python clean_non_conference_files.py [--dry-run]
    
    --dry-run: Preview changes without saving files
"""

import pandas as pd
import sys
import argparse
from pathlib import Path
from openpyxl import load_workbook
import shutil
from datetime import datetime

def extract_team_name_from_filename(filename):
    """Extract expected team name from filename.
    
    Examples:
        "Georgia Bulldogs Non Conference All Positions 2025.xlsx" -> "Georgia Bulldogs"
        "Alabama Crimson Tide Non Conference All Positions 2025.xlsx" -> "Alabama Crimson Tide"
        "Mississppi St. Bulldogs Non Conference All Positions 2025.xlsx" -> "Mississippi St. Bulldogs"
    """
    # Remove extension
    name = Path(filename).stem
    
    # Remove "Non Conference All Positions 2025" suffix
    name = name.replace(" Non Conference All Positions 2025", "")
    name = name.replace(" Non Conference 2025", "")
    name = name.replace(" Non Conference", "")
    
    # Fix common typos
    name = name.replace("Mississppi", "Mississippi")
    
    return name.strip()

def normalize_team_name(team_name):
    """Normalize team name for comparison (handle common variations)."""
    if pd.isna(team_name):
        return None
    
    team = str(team_name).strip()
    
    # Fix common typos/variations
    team = team.replace("Mississppi", "Mississippi")
    
    return team

def create_backup(file_path):
    """Create a backup copy of the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}_BACKUP_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def clean_non_conference_file(file_path, dry_run=False, create_backups=True):
    """Clean a single non-conference file by removing errant teams."""
    
    expected_team = extract_team_name_from_filename(file_path.name)
    
    print(f"\n📄 {file_path.name}")
    print(f"   Expected team: {expected_team}")
    
    # Create backup if requested and not dry run
    backup_path = None
    if not dry_run and create_backups:
        backup_path = create_backup(file_path)
        print(f"   💾 Backup created: {backup_path.name}")
    
    try:
        # Load the Excel file
        df = pd.read_excel(file_path, sheet_name=0)
        
        original_count = len(df)
        
        # Check which column has team names (prefer "Team within selected timeframe")
        team_col = None
        if 'Team within selected timeframe' in df.columns:
            team_col = 'Team within selected timeframe'
        elif 'Team' in df.columns:
            team_col = 'Team'
        
        if not team_col:
            print(f"   ⚠️  No team column found, skipping")
            return None
        
        # Normalize expected team name
        expected_team_normalized = normalize_team_name(expected_team)
        
        # Show current teams
        teams_before = df[team_col].value_counts()
        print(f"   Teams found ({len(teams_before)} unique):")
        for team, count in teams_before.items():
            print(f"     - {team}: {count} players")
        
        # Filter to only keep rows where team matches expected team
        # Normalize both sides for comparison
        df['_team_normalized'] = df[team_col].apply(normalize_team_name)
        df_cleaned = df[df['_team_normalized'] == expected_team_normalized].copy()
        df_cleaned = df_cleaned.drop(columns=['_team_normalized'])
        
        removed_count = original_count - len(df_cleaned)
        
        if removed_count > 0:
            # Find which teams were removed
            removed_teams_dict = {}
            for team in teams_before.index:
                team_normalized = normalize_team_name(team)
                if team_normalized != expected_team_normalized:
                    removed_teams_dict[team] = teams_before[team]
            
            print(f"\n   🧹 Will remove {removed_count} rows from {len(removed_teams_dict)} errant teams:")
            for team, count in removed_teams_dict.items():
                print(f"     - {team}: {count} players")
            
            if not dry_run:
                # Save cleaned file (overwrite original)
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df_cleaned.to_excel(writer, sheet_name='All Players', index=False)
                    
                    # If original had team sheets, recreate them
                    if 'Team' in df_cleaned.columns:
                        for team in sorted(df_cleaned['Team'].unique()):
                            team_df = df_cleaned[df_cleaned['Team'] == team]
                            sheet_name = str(team)[:31]  # Excel sheet name limit
                            team_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                print(f"   ✅ Saved cleaned file: {len(df_cleaned)} rows remaining")
            else:
                print(f"   🔍 [DRY RUN] Would save: {len(df_cleaned)} rows")
        else:
            print(f"   ✅ File is clean (all rows match expected team)")
        
        return {
            'file': file_path.name,
            'expected_team': expected_team,
            'original_count': original_count,
            'cleaned_count': len(df_cleaned),
            'removed_count': removed_count,
            'removed_teams': list(removed_teams_dict.keys()) if removed_count > 0 else []
        }
        
    except Exception as e:
        print(f"   ❌ Error processing file: {e}")
        return None

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Clean non-conference export files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without saving files')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup copies')
    parser.add_argument('--directory', type=str,
                       default='/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Exports/Non Conference',
                       help='Directory containing non-conference files')
    
    args = parser.parse_args()
    
    source_dir = Path(args.directory)
    
    if not source_dir.exists():
        print(f"❌ Directory not found: {source_dir}")
        sys.exit(1)
    
    print("="*80)
    print("CLEANING NON-CONFERENCE FILES")
    print("="*80)
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified")
    
    # Find all Excel files
    excel_files = list(source_dir.glob("*.xlsx"))
    
    if not excel_files:
        print(f"\n⚠️  No Excel files found in {source_dir}")
        return
    
    print(f"\n📁 Found {len(excel_files)} files to check")
    
    # Process each file
    results = []
    for file_path in sorted(excel_files):
        result = clean_non_conference_file(file_path, dry_run=args.dry_run, create_backups=not args.no_backup)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_removed = sum(r['removed_count'] for r in results)
    files_cleaned = sum(1 for r in results if r['removed_count'] > 0)
    
    print(f"\n📊 Files processed: {len(results)}")
    print(f"📊 Files cleaned: {files_cleaned}")
    print(f"📊 Total rows removed: {total_removed}")
    
    if files_cleaned > 0:
        print(f"\n📋 Files with errant teams removed:")
        for r in results:
            if r['removed_count'] > 0:
                print(f"  • {r['file']}: Removed {r['removed_count']} rows")
                for team in r['removed_teams']:
                    print(f"    - {team}")
    
    if args.dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")

if __name__ == "__main__":
    main()

