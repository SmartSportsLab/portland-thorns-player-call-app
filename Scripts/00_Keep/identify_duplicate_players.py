#!/usr/bin/env python3
"""
Identify Duplicate Players
==========================

Identifies players who appear more than once in inter-conference and 
non-conference files. Reports duplicates with their game counts and other details.

Usage:
    python identify_duplicate_players.py
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

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

def analyze_duplicates_in_file(file_path, file_type):
    """Analyze duplicates in a single file."""
    if not file_path.exists():
        return []
    
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        
        if 'Player' not in df.columns:
            return []
        
        # Find duplicates
        player_counts = df['Player'].value_counts()
        duplicates = player_counts[player_counts > 1]
        
        if len(duplicates) == 0:
            return []
        
        # Get details for each duplicate player
        duplicate_details = []
        
        for player_name in duplicates.index:
            player_rows = df[df['Player'] == player_name]
            
            details = {
                'file': file_path.name,
                'file_type': file_type,
                'player': player_name,
                'count': len(player_rows),
                'entries': []
            }
            
            # Get details for each entry
            for idx, row in player_rows.iterrows():
                entry = {
                    'matches': row.get('Matches played', 'N/A'),
                    'minutes': row.get('Minutes played', 'N/A'),
                    'goals': row.get('Goals', 'N/A'),
                    'assists': row.get('Assists', 'N/A'),
                    'position': row.get('Position', 'N/A'),
                    'team': row.get('Team', row.get('Team within selected timeframe', 'N/A'))
                }
                details['entries'].append(entry)
            
            duplicate_details.append(details)
        
        return duplicate_details
        
    except Exception as e:
        print(f"  ❌ Error analyzing {file_path.name}: {e}")
        return []

def main():
    """Main function."""
    
    base_dir = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Exports")
    
    conference_dir = base_dir / "Conference"
    non_conference_dir = base_dir / "Non Conference"
    
    print("="*80)
    print("IDENTIFYING DUPLICATE PLAYERS")
    print("="*80)
    
    all_duplicates = {
        'inter_conference': [],
        'non_conference': []
    }
    
    # Analyze inter-conference files
    print("\n" + "="*80)
    print("INTER-CONFERENCE FILES")
    print("="*80)
    
    sec_file = conference_dir / "SEC All Positions 2025.xlsx"
    acc_file = conference_dir / "ACC All Positions 2025.xlsx"
    
    # Process SEC teams
    if sec_file.exists():
        print(f"\n📄 {sec_file.name}")
        df_sec = pd.read_excel(sec_file, sheet_name=0)
        
        for team_key, team_display_name in SEC_TEAMS.items():
            team_variations = [team_display_name, team_key]
            if 'Mississippi' in team_display_name:
                team_variations.append('Mississppi St. Bulldogs')
            
            team_df = None
            for variation in team_variations:
                team_df = find_team_in_dataframe(df_sec, variation)
                if len(team_df) > 0:
                    break
            
            if team_df is not None and len(team_df) > 0:
                # Create temp file for analysis
                temp_file = Path("/tmp") / f"{team_display_name}_inter_temp.xlsx"
                team_df.to_excel(temp_file, index=False)
                
                duplicates = analyze_duplicates_in_file(temp_file, "Inter-Conference")
                if duplicates:
                    # Update file name to show it's from SEC
                    for dup in duplicates:
                        dup['file'] = f"SEC All Positions 2025.xlsx (team: {team_display_name})"
                    all_duplicates['inter_conference'].extend(duplicates)
                    print(f"  📋 {team_display_name}: {len(duplicates)} players with duplicates")
                else:
                    print(f"  ✅ {team_display_name}: No duplicates")
                
                temp_file.unlink()
    
    # Process ACC teams
    if acc_file.exists():
        print(f"\n📄 {acc_file.name}")
        df_acc = pd.read_excel(acc_file, sheet_name=0)
        
        for team_key, team_display_name in ACC_TEAMS.items():
            team_variations = [team_display_name, team_key]
            
            team_df = None
            for variation in team_variations:
                team_df = find_team_in_dataframe(df_acc, variation)
                if len(team_df) > 0:
                    break
            
            if team_df is not None and len(team_df) > 0:
                temp_file = Path("/tmp") / f"{team_display_name}_inter_temp.xlsx"
                team_df.to_excel(temp_file, index=False)
                
                duplicates = analyze_duplicates_in_file(temp_file, "Inter-Conference")
                if duplicates:
                    for dup in duplicates:
                        dup['file'] = f"ACC All Positions 2025.xlsx (team: {team_display_name})"
                    all_duplicates['inter_conference'].extend(duplicates)
                    print(f"  📋 {team_display_name}: {len(duplicates)} players with duplicates")
                else:
                    print(f"  ✅ {team_display_name}: No duplicates")
                
                temp_file.unlink()
    
    # Analyze non-conference files
    print("\n" + "="*80)
    print("NON-CONFERENCE FILES")
    print("="*80)
    
    all_teams = {**SEC_TEAMS, **ACC_TEAMS}
    
    for team_key, team_display_name in all_teams.items():
        # Try different filename patterns
        patterns = [
            f"{team_display_name} Non Conference All Positions 2025.xlsx",
            f"{team_display_name}.xlsx"
        ]
        
        non_conf_file = None
        for pattern in patterns:
            potential_file = non_conference_dir / pattern
            if potential_file.exists():
                non_conf_file = potential_file
                break
        
        if non_conf_file and non_conf_file.exists():
            duplicates = analyze_duplicates_in_file(non_conf_file, "Non-Conference")
            if duplicates:
                all_duplicates['non_conference'].extend(duplicates)
                print(f"  📋 {team_display_name}: {len(duplicates)} players with duplicates")
            else:
                print(f"  ✅ {team_display_name}: No duplicates")
        else:
            print(f"  ⚠️  {team_display_name}: File not found")
    
    # Summary Report
    print("\n" + "="*80)
    print("DUPLICATE PLAYERS SUMMARY")
    print("="*80)
    
    total_inter = len(all_duplicates['inter_conference'])
    total_non = len(all_duplicates['non_conference'])
    
    print(f"\n📊 Inter-Conference: {total_inter} players with duplicates")
    print(f"📊 Non-Conference: {total_non} players with duplicates")
    print(f"📊 Total: {total_inter + total_non} players with duplicates")
    
    # Detailed report
    if total_inter > 0 or total_non > 0:
        print("\n" + "="*80)
        print("DETAILED BREAKDOWN")
        print("="*80)
        
        # Inter-Conference
        if total_inter > 0:
            print("\n📋 INTER-CONFERENCE DUPLICATES:")
            for dup in all_duplicates['inter_conference']:
                print(f"\n  👤 {dup['player']} ({dup['count']} entries)")
                print(f"     File: {dup['file']}")
                for i, entry in enumerate(dup['entries'], 1):
                    print(f"     Entry {i}:")
                    print(f"       Matches: {entry['matches']}")
                    print(f"       Minutes: {entry['minutes']}")
                    print(f"       Goals: {entry['goals']}")
                    print(f"       Assists: {entry['assists']}")
                    print(f"       Position: {entry['position']}")
        
        # Non-Conference
        if total_non > 0:
            print("\n📋 NON-CONFERENCE DUPLICATES:")
            for dup in all_duplicates['non_conference']:
                print(f"\n  👤 {dup['player']} ({dup['count']} entries)")
                print(f"     File: {dup['file']}")
                for i, entry in enumerate(dup['entries'], 1):
                    print(f"     Entry {i}:")
                    print(f"       Matches: {entry['matches']}")
                    print(f"       Minutes: {entry['minutes']}")
                    print(f"       Goals: {entry['goals']}")
                    print(f"       Assists: {entry['assists']}")
                    print(f"       Position: {entry['position']}")
    
    # Save to file
    output_file = base_dir.parent / "Duplicate_Players_Report.txt"
    with open(output_file, 'w') as f:
        f.write("DUPLICATE PLAYERS REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Inter-Conference: {total_inter} players with duplicates\n")
        f.write(f"Non-Conference: {total_non} players with duplicates\n")
        f.write(f"Total: {total_inter + total_non} players with duplicates\n\n")
        
        if total_inter > 0:
            f.write("\nINTER-CONFERENCE DUPLICATES:\n")
            f.write("-"*80 + "\n")
            for dup in all_duplicates['inter_conference']:
                f.write(f"\n{dup['player']} ({dup['count']} entries) - {dup['file']}\n")
                for i, entry in enumerate(dup['entries'], 1):
                    f.write(f"  Entry {i}: {entry['matches']} matches, {entry['minutes']} min, "
                           f"{entry['goals']} goals, {entry['assists']} assists\n")
        
        if total_non > 0:
            f.write("\nNON-CONFERENCE DUPLICATES:\n")
            f.write("-"*80 + "\n")
            for dup in all_duplicates['non_conference']:
                f.write(f"\n{dup['player']} ({dup['count']} entries) - {dup['file']}\n")
                for i, entry in enumerate(dup['entries'], 1):
                    f.write(f"  Entry {i}: {entry['matches']} matches, {entry['minutes']} min, "
                           f"{entry['goals']} goals, {entry['assists']} assists\n")
    
    print(f"\n💾 Detailed report saved to: {output_file}")

if __name__ == "__main__":
    main()



















