#!/usr/bin/env python3
"""
Calculate consistency ranking for players based on how many metrics fall below position average.
A consistency score measures how well-rounded a player is - players with fewer below-average metrics are more consistent.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from update_mike_norris_reports import load_conference_season_data

# Position profile mapping (same as create_top_15_report.py)
POSITION_PROFILE_MAP = {
    'Hybrid CB': 'Center Back',
    'DM Box-To-Box': 'Centre Midfielder',
    'AM Advanced Playmaker': 'Attacking Midfielder',
    'Right Touchline Winger': 'Winger'
}

def calculate_position_averages(all_players_df, position_profile, metric_headers, metric_column_map):
    """
    Calculate average values for each metric across all Power Five players in this position.
    
    Args:
        all_players_df: DataFrame with all Power Five players for this position
        position_profile: Position profile name (e.g., 'Hybrid CB')
        metric_headers: List of metric header names to check
        metric_column_map: Dictionary mapping metric headers to actual column names
    
    Returns:
        Dictionary mapping metric headers to their average values
    """
    averages = {}
    
    for metric_header in metric_headers:
        # Skip combined metrics - we'll handle them separately
        if metric_header == "Interceptions + Sliding Tackles":
            continue
        
        # Find the actual column name in the dataframe
        # Try metric_column_map first, then try to match by name
        actual_col = metric_column_map.get(metric_header)
        
        # If not found in map, try to find column by matching metric header name
        if not actual_col or actual_col not in all_players_df.columns:
            metric_lower = str(metric_header).lower()
            # Try exact match
            for col in all_players_df.columns:
                if str(col).lower().strip() == metric_lower.strip():
                    actual_col = col
                    break
            
            # Try base name matching if still not found
            if not actual_col or actual_col not in all_players_df.columns:
                base_name = metric_lower.replace(' per 90', '').replace(' per90', '').replace(', %', '').replace(' %', '').replace(' won', '').replace('accurate', '').strip()
                for col in all_players_df.columns:
                    col_lower = str(col).lower()
                    col_base = col_lower.replace(' per 90', '').replace(' per90', '').replace(', %', '').replace(' %', '').replace(' won', '').replace('accurate', '').strip()
                    if base_name == col_base:
                        actual_col = col
                        break
        
        if actual_col and actual_col in all_players_df.columns:
            # Calculate average, excluding NaN values
            values = pd.to_numeric(all_players_df[actual_col], errors='coerce').dropna()
            if len(values) > 0:
                avg = values.mean()
                averages[metric_header] = avg
    
    # Handle combined metric "Interceptions + Sliding Tackles"
    if "Interceptions + Sliding Tackles" in metric_headers:
        interceptions_col = None
        sliding_col = None
        
        # Find the component columns
        for col in all_players_df.columns:
            col_lower = str(col).lower()
            if 'interception' in col_lower and 'per 90' in col_lower:
                interceptions_col = col
            if 'sliding' in col_lower and 'per 90' in col_lower:
                sliding_col = col
        
        if interceptions_col and sliding_col:
            inter_values = pd.to_numeric(all_players_df[interceptions_col], errors='coerce').dropna()
            slide_values = pd.to_numeric(all_players_df[sliding_col], errors='coerce').dropna()
            
            if len(inter_values) > 0 and len(slide_values) > 0:
                # Calculate average of combined metric
                combined_values = []
                for idx in all_players_df.index:
                    inter_val = pd.to_numeric(all_players_df.at[idx, interceptions_col], errors='coerce')
                    slide_val = pd.to_numeric(all_players_df.at[idx, sliding_col], errors='coerce')
                    if pd.notna(inter_val) and pd.notna(slide_val):
                        combined_values.append(inter_val + slide_val)
                
                if len(combined_values) > 0:
                    averages["Interceptions + Sliding Tackles"] = np.mean(combined_values)
    
    return averages


def calculate_consistency_score(player_row, position_averages, metric_headers, metric_column_map, all_players_df=None):
    """
    Calculate consistency score for a single player.
    
    Consistency score measures:
    - How many metrics are above average (higher is better)
    - How many metrics are below average (lower is better)
    - Percentage of metrics above average
    
    Returns:
        Dictionary with:
        - 'metrics_above_avg': Count of metrics above average
        - 'metrics_below_avg': Count of metrics below average
        - 'metrics_at_avg': Count of metrics at average (within 1%)
        - 'total_metrics': Total metrics checked
        - 'consistency_pct': Percentage of metrics above average
        - 'consistency_score': Score from 0-100 (100 = all metrics above average)
        - 'below_avg_metrics': List of metrics that are below average
    """
    metrics_above = 0
    metrics_below = 0
    metrics_at = 0
    total_checked = 0
    below_avg_list = []
    
    for metric_header in metric_headers:
        if metric_header not in position_averages:
            continue
        
        avg_value = position_averages[metric_header]
        if pd.isna(avg_value) or avg_value == 0:
            continue
        
        # Get player's value for this metric
        player_value = None
        
        # Try to get from player_row using metric_column_map
        actual_col = metric_column_map.get(metric_header)
        # Skip if actual_col is a dict (combined metric - handled separately)
        if isinstance(actual_col, dict):
            actual_col = None
        
        if actual_col and hasattr(player_row, 'index') and actual_col in player_row.index:
            try:
                player_value = player_row.get(actual_col)
            except:
                pass
        
        # If not found, try alternative column names
        if player_value is None or (pd.isna(player_value) if hasattr(pd, 'isna') else (player_value == '' or player_value is None)):
            metric_lower = str(metric_header).lower()
            
            # Try with _report suffix
            if actual_col and hasattr(player_row, 'index'):
                report_col = actual_col + '_report'
                if report_col in player_row.index:
                    try:
                        test_val = player_row.get(report_col, '')
                        if test_val is not None and test_val != '' and not (hasattr(pd, 'isna') and pd.isna(test_val)):
                            player_value = test_val
                    except:
                        pass
            
            # Try base name matching
            if player_value is None or (pd.isna(player_value) if hasattr(pd, 'isna') else (player_value == '' or player_value is None)):
                base_name = metric_lower.replace(' per 90', '').replace(' per90', '').replace(', %', '').replace(' %', '').replace(' won', '').replace('accurate', '').strip()
                if hasattr(player_row, 'index'):
                    for col in player_row.index:
                        try:
                            col_lower = str(col).lower()
                            col_base = col_lower.replace(' per 90', '').replace(' per90', '').replace(', %', '').replace(' %', '').replace(' won', '').replace('accurate', '').replace('_report', '').strip()
                            if base_name == col_base and '_vs_' not in col_lower:
                                test_val = player_row.get(col, '')
                                if test_val is not None and test_val != '' and not (hasattr(pd, 'isna') and pd.isna(test_val)):
                                    player_value = test_val
                                    break
                        except:
                            continue
        
        # Handle combined metric
        if metric_header == "Interceptions + Sliding Tackles" and (player_value is None or (hasattr(pd, 'isna') and pd.isna(player_value))):
            interceptions_val = None
            sliding_val = None
            
            if hasattr(player_row, 'index'):
                for col in player_row.index:
                    try:
                        col_lower = str(col).lower()
                        if 'interception' in col_lower and 'per 90' in col_lower:
                            interceptions_val = player_row.get(col)
                        if 'sliding' in col_lower and 'per 90' in col_lower:
                            sliding_val = player_row.get(col)
                    except:
                        continue
            
            if interceptions_val is not None and sliding_val is not None and not (hasattr(pd, 'isna') and (pd.isna(interceptions_val) or pd.isna(sliding_val))):
                try:
                    player_value = float(interceptions_val) + float(sliding_val)
                except:
                    pass
            elif interceptions_val is not None and not (hasattr(pd, 'isna') and pd.isna(interceptions_val)):
                player_value = interceptions_val
            elif sliding_val is not None and not (hasattr(pd, 'isna') and pd.isna(sliding_val)):
                player_value = sliding_val
        
        # Skip if still no value
        if player_value is None or player_value == '' or (hasattr(pd, 'isna') and pd.isna(player_value)):
            continue
        
        try:
            player_val = float(player_value)
            total_checked += 1
            
            # Compare to average (with small tolerance for "at average")
            tolerance = abs(avg_value) * 0.01  # 1% tolerance
            
            if player_val > avg_value + tolerance:
                metrics_above += 1
            elif player_val < avg_value - tolerance:
                metrics_below += 1
                below_avg_list.append(metric_header)
            else:
                metrics_at += 1
        except (ValueError, TypeError):
            continue
    
    # Calculate consistency percentage and score
    if total_checked > 0:
        consistency_pct = (metrics_above / total_checked) * 100
        # Consistency score: 100 if all above average, decreases by points for each below-average metric
        # Formula: 100 - (metrics_below * (100 / total_checked))
        consistency_score = max(0, 100 - (metrics_below * (100 / total_checked)))
    else:
        consistency_pct = 0
        consistency_score = 0
    
    return {
        'metrics_above_avg': metrics_above,
        'metrics_below_avg': metrics_below,
        'metrics_at_avg': metrics_at,
        'total_metrics': total_checked,
        'consistency_pct': round(consistency_pct, 1),
        'consistency_score': round(consistency_score, 1),
        'below_avg_metrics': below_avg_list
    }


def calculate_consistency_for_shortlist(df, position_profile, metric_headers, metric_column_map, base_dir):
    """
    Calculate consistency scores for all players in a shortlist DataFrame.
    
    Args:
        df: DataFrame with players to score
        position_profile: Position profile name
        metric_headers: List of metric headers
        metric_column_map: Dictionary mapping headers to column names
        base_dir: Base directory for loading data
    
    Returns:
        DataFrame with added consistency columns
    """
    print(f"  📊 Calculating consistency rankings for {position_profile}...")
    
    # Load all Power Five players for this position to calculate averages
    position_name = POSITION_PROFILE_MAP.get(position_profile, position_profile)
    
    # Map position profiles to file prefixes
    position_to_prefix = {
        'Hybrid CB': 'CB Hybrid',
        'DM Box-To-Box': 'DM Box-To-Box',
        'AM Advanced Playmaker': 'AM Advanced Playmaker',
        'Right Touchline Winger': 'W Touchline Winger'
    }
    
    file_prefix = position_to_prefix.get(position_profile)
    if not file_prefix:
        print(f"     ⚠️  No file prefix found for {position_profile}")
        df['Consistency Score'] = 0
        df['Metrics Above Avg'] = 0
        df['Metrics Below Avg'] = 0
        df['Consistency %'] = 0
        return df
    
    # Load all Power Five players
    all_players_list = []
    power_five_conferences = ['ACC', 'SEC', 'BIG10', 'BIG12', 'IVY']
    
    # Map position name to file prefix
    position_to_prefix = {
        'Center Back': 'CB Hybrid',
        'Centre Midfielder': 'DM Box-To-Box',
        'Attacking Midfielder': 'AM Advanced Playmaker',
        'Winger': 'W Touchline Winger'
    }
    
    file_prefix = position_to_prefix.get(position_name)
    if not file_prefix:
        print(f"     ⚠️  No file prefix found for {position_name}")
        df['Consistency Score'] = 0
        df['Metrics Above Avg'] = 0
        df['Metrics Below Avg'] = 0
        df['Consistency %'] = 0
        return df
    
    # Load raw data files directly
    raw_dir = base_dir / 'Exports' / 'Players Stats By Position'
    
    for conf in power_five_conferences:
        try:
            raw_file = raw_dir / f'{file_prefix} {conf} 2025.xlsx'
            if raw_file.exists():
                raw_df = pd.read_excel(raw_file)
                if raw_df is not None and not raw_df.empty:
                    all_players_list.append(raw_df)
        except Exception as e:
            print(f"     ⚠️  Could not load {conf} data: {e}")
            continue
    
    if not all_players_list:
        print(f"     ⚠️  No Power Five players loaded for averaging")
        df['Consistency Score'] = 0
        df['Metrics Above Avg'] = 0
        df['Metrics Below Avg'] = 0
        df['Consistency %'] = 0
        return df
    
    all_players_df = pd.concat(all_players_list, ignore_index=True)
    print(f"     ✅ Loaded {len(all_players_df)} Power Five players for averaging")
    
    # Calculate position averages
    position_averages = calculate_position_averages(all_players_df, position_profile, metric_headers, metric_column_map)
    print(f"     ✅ Calculated averages for {len(position_averages)} metrics")
    
    # Calculate consistency for each player
    consistency_results = []
    for idx, player_row in df.iterrows():
        try:
            consistency = calculate_consistency_score(
                player_row, position_averages, metric_headers, metric_column_map, all_players_df
            )
            consistency_results.append(consistency)
        except Exception as e:
            # If calculation fails, return default values
            import traceback
            print(f"     ⚠️  Error calculating consistency for player {player_row.get('Player', 'Unknown')}: {e}")
            traceback.print_exc()
            consistency_results.append({
                'metrics_above_avg': 0,
                'metrics_below_avg': 0,
                'metrics_at_avg': 0,
                'total_metrics': 0,
                'consistency_pct': 0,
                'consistency_score': 0,
                'below_avg_metrics': []
            })
    
    # Add consistency columns to dataframe
    df['Consistency Score'] = [r['consistency_score'] for r in consistency_results]
    df['Metrics Above Avg'] = [r['metrics_above_avg'] for r in consistency_results]
    df['Metrics Below Avg'] = [r['metrics_below_avg'] for r in consistency_results]
    df['Metrics At Avg'] = [r['metrics_at_avg'] for r in consistency_results]
    df['Consistency %'] = [r['consistency_pct'] for r in consistency_results]
    df['Total Metrics Checked'] = [r['total_metrics'] for r in consistency_results]
    
    # Show summary
    avg_consistency = df['Consistency Score'].mean()
    print(f"     ✅ Average consistency score: {avg_consistency:.1f}/100")
    print(f"     ✅ Players with 0 below-average metrics: {(df['Metrics Below Avg'] == 0).sum()}")
    print(f"     ✅ Players with >3 below-average metrics: {(df['Metrics Below Avg'] > 3).sum()}")
    
    return df

