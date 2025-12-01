#!/usr/bin/env python3
"""
Merge Conference and Non-Conference Files
===========================================

Merges inter-conference and non-conference data for each championship team.
Creates combined files with all games (conference + non-conference) for each team.

Usage:
    python merge_conference_nonconference.py
"""

import pandas as pd
from pathlib import Path
from openpyxl import Workbook

# Championship teams
SEC_TEAMS = {
    'Vanderbilt': 'Vanderbilt Commodores',
    'Alabama': 'Alabama Crimson Tide',
    'Georgia': 'Georgia Bulldogs',
    'Kentucky': 'Kentucky Wildcats',
    'Arkansas': 'Arkansas Razorbacks',
    'Mississippi State': 'Mississippi St. Bulldogs',
    'Tennessee': 'Tennessee Vols',
    'LSU': 'LSU Tigers'
}

ACC_TEAMS = {
    'Stanford': 'Stanford Cardinal',
    'Virginia': 'Virginia Cavaliers',
    'Notre Dame': 'Notre Dame Fighting Irish',
    'Duke': 'Duke Blue Devils'
}

def normalize_team_name(name):
    """Normalize team name for matching."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    # Handle variations
    name = name.replace("Mississppi", "Mississippi")
    return name

def find_team_in_dataframe(df, team_name):
    """Find rows matching a team name in the dataframe."""
    # Try both Team columns
    team_cols = ['Team within selected timeframe', 'Team']
    
    for col in team_cols:
        if col in df.columns:
            # Normalize for comparison
            df['_temp_normalized'] = df[col].apply(normalize_team_name)
            team_normalized = normalize_team_name(team_name)
            
            mask = df['_temp_normalized'] == team_normalized
            result = df[mask].copy()
            result = result.drop(columns=['_temp_normalized'])
            df = df.drop(columns=['_temp_normalized'])
            
            if len(result) > 0:
                return result
    
    return pd.DataFrame()

def merge_team_data(conference_file, non_conference_dir, team_display_name, team_variations):
    """Merge conference and non-conference data for a team."""
    
    # Load conference data
    if not conference_file.exists():
        print(f"  ⚠️  Conference file not found: {conference_file.name}")
        return None
    
    df_conf = pd.read_excel(conference_file, sheet_name=0)
    df_conf['Game_Type'] = 'Inter-Conference'
    
    # Find team in conference data
    team_conf = None
    for variation in team_variations:
        team_conf = find_team_in_dataframe(df_conf, variation)
        if len(team_conf) > 0:
            break
    
    if len(team_conf) == 0:
        print(f"  ⚠️  Team not found in conference file: {team_display_name}")
        team_conf = pd.DataFrame()
    
    # Load non-conference data
    team_non_conf = pd.DataFrame()
    non_conf_file = None
    
    # Try to find non-conference file
    for variation in team_variations:
        # Try different filename patterns
        patterns = [
            f"{variation} Non Conference All Positions 2025.xlsx",
            f"{variation}.xlsx"
        ]
        
        for pattern in patterns:
            potential_file = non_conference_dir / pattern
            if potential_file.exists():
                non_conf_file = potential_file
                break
        
        if non_conf_file:
            break
    
    if non_conf_file and non_conf_file.exists():
        df_non = pd.read_excel(non_conf_file, sheet_name=0)
        df_non['Game_Type'] = 'Non-Conference'
        team_non_conf = df_non.copy()
    else:
        print(f"  ⚠️  Non-conference file not found for: {team_display_name}")
    
    # Merge both dataframes
    if len(team_conf) > 0 and len(team_non_conf) > 0:
        # Ensure both have same columns
        common_cols = set(team_conf.columns) & set(team_non_conf.columns)
        # Include Game_Type in common cols
        if 'Game_Type' in team_conf.columns:
            common_cols.add('Game_Type')
        if 'Game_Type' in team_non_conf.columns:
            common_cols.add('Game_Type')
        
        team_conf_filtered = team_conf[[col for col in team_conf.columns if col in common_cols]]
        team_non_conf_filtered = team_non_conf[[col for col in team_non_conf.columns if col in common_cols]]
        
        merged = pd.concat([team_conf_filtered, team_non_conf_filtered], ignore_index=True)
        
        print(f"  ✅ Merged: {len(team_conf)} inter-conference + {len(team_non_conf)} non-conference = {len(merged)} total rows")
        
    elif len(team_conf) > 0:
        merged = team_conf.copy()
        print(f"  ✅ Inter-conference only: {len(merged)} rows")
        
    elif len(team_non_conf) > 0:
        merged = team_non_conf.copy()
        print(f"  ✅ Non-conference only: {len(merged)} rows")
        
    else:
        print(f"  ❌ No data found for {team_display_name}")
        return None
    
    return merged

def process_conference(conference_name, teams_dict, conference_dir, non_conference_dir, output_dir):
    """Process all teams in a conference."""
    
    print(f"\n{'='*80}")
    print(f"PROCESSING {conference_name}")
    print(f"{'='*80}")
    
    # Load conference file
    conference_file = conference_dir / f"{conference_name} All Positions 2025.xlsx"
    
    if not conference_file.exists():
        print(f"❌ Conference file not found: {conference_file.name}")
        return
    
    print(f"\n📄 Conference file: {conference_file.name}")
    
    # Process each team
    for team_key, team_display_name in teams_dict.items():
        print(f"\n📋 {team_display_name}")
        
        # Create list of team name variations to try
        team_variations = [team_display_name, team_key]
        
        # Special handling for Mississippi State
        if 'Mississippi' in team_display_name:
            team_variations.append('Mississppi St. Bulldogs')
        
        # Merge data
        merged_df = merge_team_data(
            conference_file, 
            non_conference_dir, 
            team_display_name,
            team_variations
        )
        
        if merged_df is not None and len(merged_df) > 0:
            # Save merged file
            output_file = output_dir / f"{team_display_name} All Games 2025.xlsx"
            
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # All Players sheet
                merged_df.to_excel(writer, sheet_name='All Players', index=False)
                
                # Game Type breakdown
                if 'Game_Type' in merged_df.columns:
                    for game_type in sorted(merged_df['Game_Type'].unique()):
                        game_df = merged_df[merged_df['Game_Type'] == game_type]
                        sheet_name = str(game_type)[:31]
                        game_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"  💾 Saved: {output_file.name}")

def main():
    """Main function."""
    
    base_dir = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Exports")
    
    conference_dir = base_dir / "Conference"
    non_conference_dir = base_dir / "Non Conference"
    output_dir = base_dir / "Merged Conference-NonConference"
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("MERGING CONFERENCE AND NON-CONFERENCE FILES")
    print("="*80)
    print(f"\n📁 Conference directory: {conference_dir}")
    print(f"📁 Non-Conference directory: {non_conference_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # Process SEC
    process_conference("SEC", SEC_TEAMS, conference_dir, non_conference_dir, output_dir)
    
    # Process ACC
    process_conference("ACC", ACC_TEAMS, conference_dir, non_conference_dir, output_dir)
    
    print("\n" + "="*80)
    print("✅ MERGE COMPLETE")
    print("="*80)
    print(f"\n📁 Output location: {output_dir}")

if __name__ == "__main__":
    main()



















