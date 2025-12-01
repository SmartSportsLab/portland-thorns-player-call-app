#!/usr/bin/env python3
"""
Merge All Game Types
====================

Merges non-conference and inter-conference (conference) files together,
and creates separate files for all three scenarios:
1. All Games (non-conference + inter-conference combined)
2. Inter-Conference Games Only
3. Non-Conference Games Only

Usage:
    python merge_all_game_types.py [conference] [position_name]
    
Example:
    python merge_all_game_types.py SEC "Attacking Midfielder"
"""

import pandas as pd
import sys
from pathlib import Path
from openpyxl import Workbook

def merge_all_game_types(conference, position_name):
    """Merge non-conference and inter-conference files."""
    
    base_dir = Path(__file__).parent.parent.parent
    
    # Map position names to file prefixes
    position_file_map = {
        'Center Back': 'CB Hybrid',
        'Centre Midfielder': 'DM Box-To-Box',
        'Attacking Midfielder': 'AM Advanced Playmaker',
        'Winger': 'W Touchline Winger'
    }
    
    file_prefix = position_file_map.get(position_name)
    if not file_prefix:
        print(f"❌ Unknown position: {position_name}")
        return
    
    # File paths
    inter_conf_file = base_dir / 'Exports' / 'By Position' / f"{conference} {file_prefix} 2025.xlsx"
    non_conf_file = base_dir / 'Exports' / 'Non-Conference' / conference / f"{file_prefix} {conference} 2025 Non-Conference.xlsx"
    
    # Load inter-conference (conference games)
    if not inter_conf_file.exists():
        print(f"❌ Inter-conference file not found: {inter_conf_file}")
        print(f"   Expected location: Exports/By Position/")
        return
    
    print(f"📄 Loading inter-conference file...")
    df_inter = pd.read_excel(inter_conf_file, sheet_name=0)
    df_inter['Game_Type'] = 'Inter-Conference'
    print(f"   ✅ Loaded {len(df_inter)} rows")
    
    # Load non-conference
    df_non = None
    if non_conf_file.exists():
        print(f"📄 Loading non-conference file...")
        df_non = pd.read_excel(non_conf_file, sheet_name=0)
        df_non['Game_Type'] = 'Non-Conference'
        print(f"   ✅ Loaded {len(df_non)} rows")
    else:
        print(f"⚠️  Non-conference file not found: {non_conf_file}")
        print(f"   Skipping non-conference merge. Only inter-conference will be processed.")
    
    # Output directory
    output_dir = base_dir / 'Exports' / 'Merged' / conference
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Save Inter-Conference Only
    inter_output = output_dir / f"{file_prefix} {conference} 2025 Inter-Conference Only.xlsx"
    with pd.ExcelWriter(inter_output, engine='openpyxl') as writer:
        df_inter.to_excel(writer, sheet_name='All Players', index=False)
        if 'Team' in df_inter.columns:
            for team in sorted(df_inter['Team'].unique()):
                team_df = df_inter[df_inter['Team'] == team]
                sheet_name = str(team)[:31]
                team_df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"\n✅ Saved Inter-Conference Only: {inter_output}")
    
    # 2. Save Non-Conference Only (if exists)
    if df_non is not None:
        non_output = output_dir / f"{file_prefix} {conference} 2025 Non-Conference Only.xlsx"
        with pd.ExcelWriter(non_output, engine='openpyxl') as writer:
            df_non.to_excel(writer, sheet_name='All Players', index=False)
            if 'Team' in df_non.columns:
                for team in sorted(df_non['Team'].unique()):
                    team_df = df_non[df_non['Team'] == team]
                    sheet_name = str(team)[:31]
                    team_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"✅ Saved Non-Conference Only: {non_output}")
    
    # 3. Merge and save All Games
    if df_non is not None:
        # Merge both dataframes
        print(f"\n📊 Merging inter-conference + non-conference...")
        
        # Ensure both have same columns
        common_cols = set(df_inter.columns) & set(df_non.columns)
        df_inter_filtered = df_inter[[col for col in df_inter.columns if col in common_cols]]
        df_non_filtered = df_non[[col for col in df_non.columns if col in common_cols]]
        
        # For players that appear in both, we need to aggregate stats
        # For now, we'll keep separate rows and flag them
        df_all = pd.concat([df_inter_filtered, df_non_filtered], ignore_index=True)
        
        # Add a combined flag for players appearing in both
        if 'Player' in df_all.columns:
            player_counts = df_all['Player'].value_counts()
            df_all['Appears_in_Both'] = df_all['Player'].map(player_counts) > 1
        
        print(f"   ✅ Combined: {len(df_all)} rows")
        
        all_output = output_dir / f"{file_prefix} {conference} 2025 All Games.xlsx"
        with pd.ExcelWriter(all_output, engine='openpyxl') as writer:
            df_all.to_excel(writer, sheet_name='All Players', index=False)
            
            # Create game type breakdown sheets
            if 'Game_Type' in df_all.columns:
                for game_type in df_all['Game_Type'].unique():
                    game_df = df_all[df_all['Game_Type'] == game_type]
                    sheet_name = str(game_type)[:31]
                    game_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Create team-by-team sheets
            if 'Team' in df_all.columns:
                for team in sorted(df_all['Team'].unique()):
                    team_df = df_all[df_all['Team'] == team]
                    sheet_name = str(team)[:31]
                    team_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✅ Saved All Games: {all_output}")
        print(f"\n📊 Summary:")
        print(f"   Inter-Conference: {len(df_inter)} rows")
        print(f"   Non-Conference: {len(df_non)} rows")
        print(f"   All Games (combined): {len(df_all)} rows")
    else:
        print(f"\n⚠️  Only inter-conference data available. All Games file = Inter-Conference Only")
    
    print(f"\n✅ Complete! Files saved to: {output_dir}")

def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("❌ Usage: python merge_all_game_types.py [conference] [position_name]")
        print("\nExample:")
        print('  python merge_all_game_types.py SEC "Attacking Midfielder"')
        sys.exit(1)
    
    conference = sys.argv[1]
    position_name = sys.argv[2]
    
    print("="*80)
    print(f"MERGING ALL GAME TYPES")
    print("="*80)
    print(f"\nConference: {conference}")
    print(f"Position: {position_name}")
    print()
    
    merge_all_game_types(conference, position_name)

if __name__ == "__main__":
    main()



















