#!/usr/bin/env python3
"""
Update existing player overview PDFs with call log data.
This script regenerates player overviews for players who have call log entries.
"""

import pandas as pd
from pathlib import Path
import sys

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generate_player_overviews import (
    load_player_data_from_shortlist,
    load_player_data_from_conference_reports,
    load_nwsl_data,
    generate_pdf_overview
)
import json

# Data paths
BASE_DIR = Path('/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search')
CALL_LOG_FILE = BASE_DIR / 'Qualitative_Data' / 'call_log.csv'

# Try multiple possible shortlist files
POSSIBLE_SHORTLIST_FILES = [
    BASE_DIR / 'Portland Thorns 2025 Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Long Shortlist.xlsx',
    BASE_DIR / 'Portland Thorns 2025 Short Shortlist.xlsx',
    BASE_DIR / 'AI Shortlist.xlsx',
]

def find_shortlist_file():
    """Find the first existing shortlist file."""
    for file_path in POSSIBLE_SHORTLIST_FILES:
        if file_path.exists():
            return file_path
    return None

def get_players_with_calls():
    """Get list of players who have call log entries."""
    try:
        if CALL_LOG_FILE.exists():
            call_log_df = pd.read_csv(CALL_LOG_FILE)
            if not call_log_df.empty and 'Player Name' in call_log_df.columns:
                return call_log_df['Player Name'].unique().tolist()
        return []
    except Exception as e:
        print(f"Error loading call log: {e}")
        return []

def main():
    """Main function to update player overviews with call data."""
    print("="*80)
    print("UPDATING PLAYER OVERVIEWS WITH CALL LOG DATA")
    print("="*80)
    
    # Get players with calls
    print("\n📞 Loading call log data...")
    players_with_calls = get_players_with_calls()
    
    if not players_with_calls:
        print("  ⚠️  No players with call data found.")
        print("  💡 Log some calls in the Streamlit app first!")
        return
    
    print(f"  ✅ Found {len(players_with_calls)} players with call data:")
    for player in sorted(players_with_calls):
        print(f"     - {player}")
    
    # Load player data
    print("\n📊 Loading player data from shortlist...")
    shortlist_file = find_shortlist_file()
    if not shortlist_file:
        print(f"  ❌ No shortlist file found. Tried:")
        for f in POSSIBLE_SHORTLIST_FILES:
            print(f"     - {f}")
        return
    
    print(f"  ✅ Using shortlist file: {shortlist_file.name}")
    players_df = load_player_data_from_shortlist(shortlist_file, BASE_DIR)
    print(f"  ✅ Loaded {len(players_df)} players from shortlist")
    
    # Load all players for ranking
    print("\n📊 Loading all players for ranking...")
    all_players_df = load_player_data_from_conference_reports(BASE_DIR)
    print(f"  ✅ Loaded {len(all_players_df)} total players")
    
    # Load NWSL data
    nwsl_dir = BASE_DIR / 'Exports' / 'Team Stats By Conference' / 'NWSL'
    print(f"\n📊 Loading NWSL data...")
    league_df, league_avg, thorns_data, thorns_ranks = load_nwsl_data(nwsl_dir)
    if thorns_ranks:
        print(f"  ✅ Loaded Portland Thorns ranks")
    
    # Load position configs
    print("\n📊 Loading position configurations...")
    position_configs_file = BASE_DIR / 'Scripts' / '00_Keep' / 'position_metrics_config.json'
    full_position_configs = None
    if position_configs_file.exists():
        with open(position_configs_file, 'r') as f:
            full_position_configs = json.load(f)
        print(f"  ✅ Loaded position configurations")
    else:
        print(f"  ⚠️  Position config file not found")
    
    # Output directory
    output_dir = BASE_DIR / 'Player Overviews'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Filter players to only those with calls
    players_to_update_indices = []
    for idx, player_row in players_df.iterrows():
        player_name = str(player_row.get('Player', '')).strip()
        if player_name and player_name.lower() in [p.lower() for p in players_with_calls]:
            players_to_update_indices.append(idx)
    
    if not players_to_update_indices:
        print("\n  ⚠️  No matching players found in shortlist.")
        print("  💡 Make sure player names in call logs match names in shortlist.")
        return
    
    print(f"\n🔄 Updating {len(players_to_update_indices)} player overviews...")
    
    updated_count = 0
    for update_idx, row_idx in enumerate(players_to_update_indices, 1):
        player_row = players_df.loc[row_idx]
        player_name = str(player_row.get('Player', 'Unknown')).strip()
        position_profile = str(player_row.get('Position Profile', '')).strip()
        
        if not position_profile:
            print(f"  ⚠️  Skipping {player_name} - no position profile")
            continue
        
        try:
            # Determine if top 15 (you may need to adjust this logic)
            is_top15 = False  # You can add logic to determine this
            
            filepath = generate_pdf_overview(
                player_row,
                position_profile,
                thorns_ranks,
                full_position_configs,
                output_dir,
                all_players_df=all_players_df,
                is_top15=is_top15
            )
            
            if filepath:
                print(f"  ✅ [{update_idx}/{len(players_to_update_indices)}] Updated: {player_name}")
                updated_count += 1
            else:
                print(f"  ⚠️  [{update_idx}/{len(players_to_update_indices)}] Failed: {player_name}")
                
        except Exception as e:
            print(f"  ❌ [{update_idx}/{len(players_to_update_indices)}] Error updating {player_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Successfully updated {updated_count}/{len(players_to_update_indices)} player overviews")
    print(f"\n💡 The updated PDFs now include:")
    print(f"   - All existing quantitative metrics")
    print(f"   - Call notes and assessments from your conversations")
    print(f"   - Player and agent evaluation scores")
    print(f"   - Key talking points and recommendations")

if __name__ == "__main__":
    main()

