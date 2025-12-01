#!/usr/bin/env python3
"""
Deduplicate Players for Mike Norris Report
==========================================

Removes specific duplicate entries from inter-conference and non-conference files
based on the specified criteria. Handles the Perdikis twins separately.

Usage:
    python deduplicate_for_mike_report.py
"""

import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime

# Deduplication rules
DEDUP_RULES = {
    'inter_conference': {
        'C. Silva': {
            'team': 'Alabama Crimson Tide',
            'keep': {'matches': 10, 'minutes': 419, 'goals': 1},
            'remove': {'matches': 4, 'minutes': 188, 'goals': 0}
        },
        'M. Midgley': {
            'team': 'Tennessee Vols',
            'keep': {'matches': 10, 'minutes': 847, 'goals': 1, 'assists': 2},
            'remove': {'matches': 3, 'minutes': 226, 'goals': 1, 'assists': 1}
        },
        'G. Ceballos': {
            'team': 'LSU Tigers',
            'keep': {'matches': 9, 'minutes': 854, 'goals': 1, 'assists': 1},
            'remove': {'matches': 1, 'minutes': 96, 'goals': 0, 'assists': 0}
        }
    },
    'non_conference': {
        'C. Silva': {
            'team': 'Alabama Crimson Tide',
            'keep': {'matches': 8, 'minutes': 528, 'goals': 0, 'assists': 1},
            'remove': {'matches': 8, 'minutes': 528, 'goals': 0, 'assists': 1}  # Identical - keep first
        },
        'N. Bidun': {
            'team': 'Georgia Bulldogs',
            'keep': {'matches': 2, 'minutes': 65},
            'remove': {'matches': 1, 'minutes': 47}
        },
        'M. Midgley': {
            'team': 'Tennessee Vols',
            'keep': {'matches': 6, 'minutes': 360, 'assists': 1},
            'remove': {'matches': 3, 'minutes': 199}
        },
        'J. Travers': {
            'team': 'Duke Blue Devils',
            'keep': {'matches': 4, 'minutes': 208, 'goals': 1},
            'remove': {'matches': 4, 'minutes': 208, 'goals': 1}  # Identical - keep first
        },
        'K. Perdikis': {
            'team': 'Duke Blue Devils',
            'special': 'twins',  # Handle separately
            'kaeden': {'matches': 1, 'minutes': 66, 'position': 'RCB'},
            'kosette': {'matches': 1, 'minutes': 49, 'position': 'LCMF'}
        }
    }
}

def normalize_team_name(name):
    """Normalize team name for matching."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    name = name.replace("Mississppi", "Mississippi")
    return name

def find_team_in_dataframe(df, team_name):
    """Find rows matching a team name in the dataframe."""
    team_cols = ['Team within selected timeframe', 'Team']
    
    for col in team_cols:
        if col in df.columns:
            df['_temp_normalized'] = df[col].apply(normalize_team_name)
            team_normalized = normalize_team_name(team_name)
            mask = df['_temp_normalized'] == team_normalized
            result = df[mask].copy()
            result = result.drop(columns=['_temp_normalized'])
            df = df.drop(columns=['_temp_normalized'])
            if len(result) > 0:
                return result
    
    return pd.DataFrame()

def matches_criteria(row, criteria):
    """Check if a row matches the given criteria."""
    # Map criteria keys to actual column names
    column_map = {
        'matches': 'Matches played',
        'minutes': 'Minutes played',
        'goals': 'Goals',
        'assists': 'Assists',
        'position': 'Position'
    }
    
    for key, value in criteria.items():
        if key == 'position':
            # Check if position string contains the value
            row_value = str(row.get('Position', '')).upper()
            if value.upper() not in row_value:
                return False
        else:
            # Get the actual column name
            col_name = column_map.get(key, key)
            row_value = row.get(col_name, None)
            
            if pd.isna(row_value):
                row_value = None
            else:
                try:
                    row_value = float(row_value)
                    value = float(value)
                except:
                    pass
            
            if row_value != value:
                return False
    return True

def deduplicate_inter_conference(base_dir):
    """Deduplicate inter-conference files."""
    print("\n" + "="*80)
    print("DEDUPLICATING INTER-CONFERENCE FILES")
    print("="*80)
    
    conference_dir = base_dir / "Conference"
    sec_file = conference_dir / "SEC All Positions 2025.xlsx"
    
    if not sec_file.exists():
        print(f"❌ File not found: {sec_file}")
        return
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = sec_file.parent / f"{sec_file.stem}_BACKUP_{timestamp}{sec_file.suffix}"
    shutil.copy2(sec_file, backup_file)
    print(f"💾 Backup created: {backup_file.name}")
    
    # Load file
    df = pd.read_excel(sec_file, sheet_name=0)
    original_count = len(df)
    
    # Process each rule
    for player_name, rule in DEDUP_RULES['inter_conference'].items():
        team_name = rule['team']
        print(f"\n📋 Processing {player_name} ({team_name})")
        
        # Find team data
        team_df = find_team_in_dataframe(df, team_name)
        if len(team_df) == 0:
            print(f"  ⚠️  Team not found")
            continue
        
        # Find player rows
        player_rows = team_df[team_df['Player'] == player_name]
        if len(player_rows) == 0:
            print(f"  ⚠️  Player not found")
            continue
        
        if len(player_rows) < 2:
            print(f"  ✅ No duplicates (only {len(player_rows)} entry)")
            continue
        
        print(f"  Found {len(player_rows)} entries")
        
        # Find rows to keep and remove
        keep_indices = []
        remove_indices = []
        
        for idx, row in player_rows.iterrows():
            if matches_criteria(row, rule['keep']):
                keep_indices.append(idx)
                print(f"    ✅ Keep: {row.get('Matches played', 'N/A')} matches, {row.get('Minutes played', 'N/A')} min")
            elif matches_criteria(row, rule['remove']):
                remove_indices.append(idx)
                print(f"    🗑️  Remove: {row.get('Matches played', 'N/A')} matches, {row.get('Minutes played', 'N/A')} min")
        
        # Remove rows
        if remove_indices:
            df = df.drop(index=remove_indices)
            print(f"  ✅ Removed {len(remove_indices)} duplicate(s)")
        else:
            print(f"  ⚠️  Could not find entry to remove")
    
    # Save cleaned file
    removed_count = original_count - len(df)
    if removed_count > 0:
        df.to_excel(sec_file, index=False)
        print(f"\n✅ Saved cleaned file: Removed {removed_count} rows")
    else:
        print(f"\n✅ No changes needed")

def deduplicate_non_conference(base_dir):
    """Deduplicate non-conference files."""
    print("\n" + "="*80)
    print("DEDUPLICATING NON-CONFERENCE FILES")
    print("="*80)
    
    non_conference_dir = base_dir / "Non Conference"
    
    # Process each rule
    for player_name, rule in DEDUP_RULES['non_conference'].items():
        team_name = rule['team']
        
        # Handle Perdikis twins specially
        if rule.get('special') == 'twins':
            print(f"\n📋 Processing {player_name} ({team_name}) - TWINS")
            handle_perdikis_twins(non_conference_dir, team_name, rule)
            continue
        
        # Find team file
        patterns = [
            f"{team_name} Non Conference All Positions 2025.xlsx",
            f"{team_name}.xlsx"
        ]
        
        team_file = None
        for pattern in patterns:
            potential_file = non_conference_dir / pattern
            if potential_file.exists():
                team_file = potential_file
                break
        
        if not team_file or not team_file.exists():
            print(f"\n📋 {player_name} ({team_name}): File not found")
            continue
        
        print(f"\n📋 Processing {player_name} ({team_name})")
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = team_file.parent / f"{team_file.stem}_BACKUP_{timestamp}{team_file.suffix}"
        shutil.copy2(team_file, backup_file)
        print(f"  💾 Backup created: {backup_file.name}")
        
        # Load file
        df = pd.read_excel(team_file, sheet_name=0)
        original_count = len(df)
        
        # Find player rows
        player_rows = df[df['Player'] == player_name]
        if len(player_rows) < 2:
            print(f"  ✅ No duplicates (only {len(player_rows)} entry)")
            continue
        
        print(f"  Found {len(player_rows)} entries")
        
        # Find rows to keep and remove
        keep_indices = []
        remove_indices = []
        
        for idx, row in player_rows.iterrows():
            if matches_criteria(row, rule['keep']):
                keep_indices.append(idx)
                print(f"    ✅ Keep: {row.get('Matches played', 'N/A')} matches, {row.get('Minutes played', 'N/A')} min")
            elif matches_criteria(row, rule['remove']):
                remove_indices.append(idx)
                print(f"    🗑️  Remove: {row.get('Matches played', 'N/A')} matches, {row.get('Minutes played', 'N/A')} min")
        
        # For identical entries, keep first occurrence
        if len(keep_indices) == 0 and len(remove_indices) == 0:
            # Both are identical - keep first, remove rest
            print(f"  ⚠️  All entries identical - keeping first occurrence")
            keep_indices = [player_rows.index[0]]
            remove_indices = list(player_rows.index[1:])
        
        # Remove rows
        if remove_indices:
            df = df.drop(index=remove_indices)
            print(f"  ✅ Removed {len(remove_indices)} duplicate(s)")
            
            # Save cleaned file
            removed_count = original_count - len(df)
            df.to_excel(team_file, index=False)
            print(f"  💾 Saved cleaned file")
        else:
            print(f"  ⚠️  Could not find entry to remove")

def handle_perdikis_twins(non_conference_dir, team_name, rule):
    """Handle the Perdikis twins by renaming them to their actual names."""
    patterns = [
        f"{team_name} Non Conference All Positions 2025.xlsx",
        f"{team_name}.xlsx"
    ]
    
    team_file = None
    for pattern in patterns:
        potential_file = non_conference_dir / pattern
        if potential_file.exists():
            team_file = potential_file
            break
    
    if not team_file or not team_file.exists():
        print(f"  ⚠️  File not found")
        return
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = team_file.parent / f"{team_file.stem}_BACKUP_{timestamp}{team_file.suffix}"
    shutil.copy2(team_file, backup_file)
    print(f"  💾 Backup created: {backup_file.name}")
    
    # Load file
    df = pd.read_excel(team_file, sheet_name=0)
    
    # Find K. Perdikis rows
    player_rows = df[df['Player'] == 'K. Perdikis']
    
    if len(player_rows) < 2:
        print(f"  ⚠️  Expected 2 entries, found {len(player_rows)}")
        return
    
    print(f"  Found {len(player_rows)} entries")
    
    # Rename based on position
    for idx, row in player_rows.iterrows():
        position = str(row.get('Position', '')).upper()
        matches = row.get('Matches played', 0)
        minutes = row.get('Minutes played', 0)
        
        if 'RCB' in position and matches == 1 and minutes == 66:
            df.at[idx, 'Player'] = 'Kaeden Koons-Perdikis'
            print(f"    ✅ Renamed to: Kaeden Koons-Perdikis (RCB, {matches} matches, {minutes} min)")
        elif 'LCMF' in position and matches == 1 and minutes == 49:
            df.at[idx, 'Player'] = 'Kosette Koons-Perdikis'
            print(f"    ✅ Renamed to: Kosette Koons-Perdikis (LCMF, {matches} matches, {minutes} min)")
        else:
            print(f"    ⚠️  Could not match entry: {position}, {matches} matches, {minutes} min")
    
    # Save file
    df.to_excel(team_file, index=False)
    print(f"  💾 Saved file with renamed twins")

def main():
    """Main function."""
    base_dir = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Exports")
    
    print("="*80)
    print("DEDUPLICATING FILES FOR MIKE NORRIS REPORT")
    print("="*80)
    
    # Process inter-conference
    deduplicate_inter_conference(base_dir)
    
    # Process non-conference
    deduplicate_non_conference(base_dir)
    
    print("\n" + "="*80)
    print("✅ DEDUPLICATION COMPLETE")
    print("="*80)
    print("\n💡 Note: Backup files created with timestamp for safety")

if __name__ == "__main__":
    main()

