#!/usr/bin/env python3
"""
Merge Non-Conference Team Exports
===================================

Merges all individual team Excel files from non-conference exports into 
one consolidated file per position.

Usage:
    python merge_non_conference_teams.py [conference] [position_name]
    
Example:
    python merge_non_conference_teams.py SEC "Attacking Midfielder"
"""

import pandas as pd
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def merge_non_conference_teams(conference, position_name):
    """Merge all non-conference team exports for a given conference and position."""
    
    base_dir = Path(__file__).parent.parent.parent
    
    # Map position names to folder patterns
    position_file_map = {
        'Center Back': 'CB Hybrid',
        'Centre Midfielder': 'DM Box-To-Box',
        'Attacking Midfielder': 'AM Advanced Playmaker',
        'Winger': 'W Touchline Winger'
    }
    
    file_prefix = position_file_map.get(position_name)
    if not file_prefix:
        print(f"❌ Unknown position: {position_name}")
        print(f"   Valid positions: {list(position_file_map.keys())}")
        return
    
    # Define source directory (where team exports will be placed)
    # Assuming structure: Exports/Non-Conference/[Conference]/[Position]/
    source_dir = base_dir / 'Exports' / 'Non-Conference' / conference / position_name
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        print(f"   Please create this directory and place team export files there")
        return
    
    # Find all Excel files
    excel_files = list(source_dir.glob('*.xlsx'))
    
    if not excel_files:
        print(f"⚠️  No Excel files found in {source_dir}")
        return
    
    print(f"🔍 Found {len(excel_files)} team files to merge")
    print(f"   Directory: {source_dir}")
    
    # Load all files
    all_dataframes = []
    teams_processed = []
    
    for file_path in sorted(excel_files):
        try:
            # Read the Excel file (first sheet)
            df = pd.read_excel(file_path, sheet_name=0)
            
            if df.empty:
                print(f"  ⚠️  Skipping empty file: {file_path.name}")
                continue
            
            # Extract team name from filename (remove extension and any prefixes)
            team_name = file_path.stem
            teams_processed.append(team_name)
            
            print(f"  ✅ Loaded {len(df)} rows from {team_name}")
            
            all_dataframes.append(df)
            
        except Exception as e:
            print(f"  ❌ Error reading {file_path.name}: {e}")
            continue
    
    if not all_dataframes:
        print(f"❌ No data to merge!")
        return
    
    # Merge all dataframes
    print(f"\n📊 Merging {len(all_dataframes)} files...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"✅ Merged: {len(merged_df)} total rows")
    print(f"   Teams: {', '.join(teams_processed)}")
    
    # Create output file
    output_dir = base_dir / 'Exports' / 'Non-Conference' / conference
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{file_prefix} {conference} 2025 Non-Conference.xlsx"
    
    # Save to Excel with team breakdown sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main "All Players" sheet
        merged_df.to_excel(writer, sheet_name='All Players', index=False)
        
        # Create team-by-team sheets
        if 'Team' in merged_df.columns:
            for team in sorted(merged_df['Team'].unique()):
                team_df = merged_df[merged_df['Team'] == team]
                sheet_name = str(team)[:31]  # Excel sheet name limit
                team_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"\n💾 Saved consolidated file:")
    print(f"   {output_file}")
    print(f"   Sheets: All Players + {len(teams_processed)} team sheets")
    
    return output_file

def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("❌ Usage: python merge_non_conference_teams.py [conference] [position_name]")
        print("\nExample:")
        print('  python merge_non_conference_teams.py SEC "Attacking Midfielder"')
        print('  python merge_non_conference_teams.py ACC "Center Back"')
        sys.exit(1)
    
    conference = sys.argv[1]
    position_name = sys.argv[2]
    
    print("="*80)
    print(f"MERGING NON-CONFERENCE TEAM EXPORTS")
    print("="*80)
    print(f"\nConference: {conference}")
    print(f"Position: {position_name}")
    print()
    
    merge_non_conference_teams(conference, position_name)

if __name__ == "__main__":
    main()



















