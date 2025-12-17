#!/usr/bin/env python3
"""
Generate a CSV file with min/max values for each metric per position profile.
This script loads the player database and calculates ranges for all metrics
defined in radar_chart_metrics_short.json.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Set up paths (same as main app)
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'Qualitative_Data'
CONFIG_PATH = BASE_DIR / 'radar_chart_metrics_short.json'

def find_player_database():
    """Find the player database Excel file."""
    # Check the main directory first (user specified path)
    main_dir = BASE_DIR.parent.parent if BASE_DIR.name == '00_Keep' else BASE_DIR.parent
    main_file = main_dir / 'Portland Thorns 2025 Long Shortlist.xlsx'
    if main_file.exists():
        return main_file
    
    # Check DATA_DIR
    if DATA_DIR.exists():
        for uploaded_file in DATA_DIR.glob('*.xlsx'):
            if uploaded_file.is_file():
                return uploaded_file
        for uploaded_file in DATA_DIR.glob('*.xls'):
            if uploaded_file.is_file():
                return uploaded_file
    return None

def load_player_data(player_db_file):
    """Load player data from Excel file."""
    try:
        # Try different header rows - start with row 2 as that's where the actual headers are
        df_dict = None
        for header_row in [2, 1, 0, 3]:
            try:
                test_df_dict = pd.read_excel(player_db_file, sheet_name=None, header=header_row)
                first_sheet = list(test_df_dict.values())[0] if test_df_dict else None
                if first_sheet is not None and 'Player' in first_sheet.columns:
                    df_dict = test_df_dict
                    break
            except:
                continue
        
        if df_dict is None:
            df_dict = pd.read_excel(player_db_file, sheet_name=None, header=2)
        
        all_data = []
        for sheet_name, sheet_df in df_dict.items():
            # Skip non-data sheets
            if sheet_name.startswith('Sheet') or 'Summary' in sheet_name or 'Notes' in sheet_name:
                continue
            
            if 'Player' in sheet_df.columns:
                # For single-sheet files, Position Profile might already be in the data
                if 'Position Profile' not in sheet_df.columns:
                    sheet_df['Position Profile'] = sheet_name
                all_data.append(sheet_df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Handle duplicate column names
            if combined_df.columns.duplicated().any():
                cols = pd.Series(combined_df.columns)
                for dup in cols[cols.duplicated()].unique():
                    dup_indices = cols[cols == dup].index.values.tolist()
                    cols[dup_indices] = [dup if i == 0 else f"{dup}_{i}" 
                                         for i in range(len(dup_indices))]
                combined_df.columns = cols
            
            return combined_df
    except Exception as e:
        print(f"Error loading player data: {e}")
        return pd.DataFrame()
    
    return pd.DataFrame()

def load_radar_config():
    """Load position-specific metrics from JSON config."""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            return config
    except Exception as e:
        print(f"Error loading radar config: {e}")
    return {}

def find_best_column_match(metric_name, available_cols):
    """Find the best matching column for a metric name."""
    metric_lower = str(metric_name).lower().strip()
    
    # Special mappings for known variations - be more specific
    special_mappings = {
        'padj interceptions': ['interceptions + sliding tackles', 'interceptions per 90', 'padj interceptions'],
        'interceptions per 90': ['interceptions + sliding tackles', 'interceptions per 90', 'padj interceptions'],
        'received passes per 90': ['received passes per 90'],  # Don't match to "Passes per 90" or "Received long passes per 90"
        'received long passes per 90': ['received long passes per 90'],  # Separate metric
        'long passes per 90': ['long passes per 90'],  # Don't match to generic "Passes per 90"
        'short / medium passes per 90': ['short / medium passes per 90'],  # Don't match to generic "Passes per 90"
        'crosses from right flank per 90': ['crosses per 90', 'crosses from right flank per 90'],
        'touches in box per 90': ['touches in box per 90', 'touches in penalty area per 90'],
    }
    
    # Check special mappings first - require exact or very close match
    for key, variations in special_mappings.items():
        if key in metric_lower:
            for variation in variations:
                for col in available_cols:
                    col_lower = str(col).lower()
                    # Require the variation to be the main part of the column name
                    if variation == col_lower or variation in col_lower:
                        # Make sure we're not matching to a more generic column
                        if 'received passes per 90' in metric_lower:
                            # Don't match to generic "Passes per 90"
                            if 'received' not in col_lower:
                                continue
                        if 'long passes per 90' in metric_lower:
                            # Don't match to generic "Passes per 90"
                            if 'long' not in col_lower:
                                continue
                        if 'short / medium passes per 90' in metric_lower or 'short / medium passes per 90' in metric_lower:
                            # Don't match to generic "Passes per 90"
                            if 'short' not in col_lower and 'medium' not in col_lower:
                                continue
                        return col
    
    # Normalize metric name
    metric_normalized = metric_lower.replace(',', '').replace('%', '%').replace('percent', '%')
    metric_normalized = metric_normalized.replace('per 90', 'per90').replace(' per 90', ' per90')
    metric_normalized = metric_normalized.replace('padj ', 'padj').replace('p adj ', 'padj').replace('p.adj ', 'padj')
    metric_normalized = ' '.join(metric_normalized.split())
    
    # Try exact match (case-insensitive)
    for col in available_cols:
        if str(col).lower().strip() == metric_lower:
            return col
    
    # Try normalized match
    for col in available_cols:
        col_normalized = str(col).lower().strip()
        col_normalized = col_normalized.replace(',', '').replace('%', '%').replace('percent', '%')
        col_normalized = col_normalized.replace('per 90', 'per90').replace(' per 90', ' per90')
        col_normalized = col_normalized.replace('padj ', 'padj').replace('p adj ', 'padj').replace('p.adj ', 'padj')
        col_normalized = ' '.join(col_normalized.split())
        if metric_normalized == col_normalized:
            return col
    
    # Try substring match with word boundaries - but be strict about key terms
    metric_words = [w for w in metric_normalized.split() if len(w) >= 3]
    
    # Key terms that must match if present in metric
    key_terms = ['received', 'long', 'short', 'medium', 'progressive', 'run', 'runs', 'interception', 'cross', 'crosses', 'acceleration', 'touches', 'box']
    
    for col in available_cols:
        col_lower = str(col).lower()
        
        # Check if key terms in metric are also in column
        metric_key_terms = [term for term in key_terms if term in metric_normalized]
        if metric_key_terms:
            # All key terms from metric must be in column
            if not all(term in col_lower for term in metric_key_terms):
                continue
        
        # Check if all key words from metric are in column
        if len(metric_words) > 0:
            matching_words = sum(1 for word in metric_words if word in col_lower)
            if matching_words >= len(metric_words) * 0.7:  # 70% of words match
                return col
    
    # Try substring match (fallback) - but still check key terms
    metric_core = metric_normalized.replace(' per90', '').replace(' %', '').replace('padj', '').strip()
    metric_key_terms = [term for term in key_terms if term in metric_normalized]
    
    for col in available_cols:
        col_lower = str(col).lower()
        col_core = col_lower.replace(' per 90', '').replace(' per90', '').replace(' %', '').replace('percent', '').replace('padj', '').strip()
        
        # If metric has key terms, they must be in column
        if metric_key_terms:
            if not all(term in col_lower for term in metric_key_terms):
                continue
        
        if metric_core == col_core:
            return col
        
        # Only do substring match if no key terms (to avoid false matches)
        if not metric_key_terms:
            if metric_lower in col_lower or col_lower in metric_lower:
                return col
    
    return None

def get_metrics_for_position(position_profile, radar_config, available_columns):
    """Get position-specific metrics for a position profile."""
    if not radar_config:
        return []
    
    # Map position profile names to JSON keys
    position_map = {
        'Hybrid CB': 'Center Back',
        'Hybrid Ball-Playing/Winning': 'Center Back',
        'CB': 'Center Back',
        'Center Back': 'Center Back',
        'DM Box-To-Box': 'Centre Midfielder',
        'Defensive-Minded Box-to-Box': 'Centre Midfielder',
        'Centre Midfielder': 'Centre Midfielder',
        'CM': 'Centre Midfielder',
        'AM Advanced Playmaker': 'Attacking Midfielder',
        'Advanced Playmaker': 'Attacking Midfielder',
        'Attacking Midfielder': 'Attacking Midfielder',
        'AM': 'Attacking Midfielder',
        'Right Touchline Winger': 'Winger',
        'Touchline Winger (Right-Sided)': 'Winger',
        'Winger': 'Winger',
        'RW': 'Winger',
        'LW': 'Winger'
    }
    
    # Find matching position in config
    config_key = position_map.get(position_profile, position_profile)
    if config_key not in radar_config:
        config_key = position_profile
    
    if config_key not in radar_config:
        return []
    
    # Get the list of metrics for this position
    metrics_list = radar_config[config_key]
    
    # Match metrics to available columns
    matched_metrics = []
    for metric_name in metrics_list:
        matched_col = find_best_column_match(metric_name, available_columns)
        if matched_col:
            matched_metrics.append(matched_col)
    
    return matched_metrics

def calculate_metric_ranges(player_db_file, radar_config):
    """Calculate min/max values for each metric per position profile by checking each sheet individually."""
    results = []
    
    # Load each sheet separately to get accurate column lists
    xl_file = pd.ExcelFile(player_db_file)
    
    # Map sheet names to config positions
    sheet_to_config = {
        'Hybrid CB': 'Center Back',
        'DM Box-To-Box': 'Centre Midfielder',
        'AM Advanced Playmaker': 'Attacking Midfielder',
        'Right Touchline Winger': 'Winger'
    }
    
    # Map position profiles to config positions
    profile_to_config = {
        'Hybrid CB': 'Center Back',
        'DM Box-To-Box': 'Centre Midfielder',
        'AM Advanced Playmaker': 'Attacking Midfielder',
        'Right Touchline Winger': 'Winger',
        'Center Back': 'Center Back',
        'Centre Midfielder': 'Centre Midfielder',
        'Attacking Midfielder': 'Attacking Midfielder',
        'Winger': 'Winger'
    }
    
    # Check if this is a single-sheet file with Position Profile column
    single_sheet_mode = False
    all_sheets_data = {}
    
    # First, try to load all sheets and check structure
    for sheet_name in xl_file.sheet_names:
        if sheet_name.startswith('Sheet') or 'Summary' in sheet_name or 'Notes' in sheet_name:
            continue
        
        # Try to find the correct header row
        df = None
        for header_row in [2, 1, 0, 3]:
            try:
                test_df = pd.read_excel(player_db_file, sheet_name=sheet_name, header=header_row)
                if 'Player' in test_df.columns:
                    df = test_df
                    break
            except:
                continue
        
        if df is None or df.empty:
            continue
        
        # Check if this sheet has Position Profile column (single-sheet mode)
        if 'Position Profile' in df.columns:
            single_sheet_mode = True
            all_sheets_data[sheet_name] = df
        else:
            # Multi-sheet mode - each sheet is a position profile
            all_sheets_data[sheet_name] = df
    
    # If single sheet mode, process by Position Profile column
    if single_sheet_mode:
        # Combine all sheets if multiple
        combined_df = pd.concat(all_sheets_data.values(), ignore_index=True) if len(all_sheets_data) > 1 else list(all_sheets_data.values())[0]
        
        # Get unique position profiles
        if 'Position Profile' not in combined_df.columns:
            print("Warning: Position Profile column not found in single-sheet mode")
            return results
        
        position_profiles = combined_df['Position Profile'].dropna().unique()
        numeric_cols = combined_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # For each position profile in the data
        for profile in position_profiles:
            profile_df = combined_df[combined_df['Position Profile'] == profile]
            
            # Get config position
            config_position = profile_to_config.get(profile, profile)
            
            # Get metrics for this position from config
            if config_position not in radar_config:
                # Try direct match
                if profile in radar_config:
                    config_position = profile
                else:
                    print(f"Warning: No config found for {profile} (tried {config_position})")
                    continue
            
            metrics_list = radar_config[config_position]
            
            # For each metric in the config
            for metric_name in metrics_list:
                # Find the matching column
                matched_col = find_best_column_match(metric_name, numeric_cols)
                
                if matched_col is None or matched_col not in combined_df.columns:
                    # Metric not found
                    results.append({
                        'Position Profile': profile,
                        'Metric': metric_name,
                        'Column Name': 'NOT FOUND',
                        'Min Value': None,
                        'Max Value': None,
                        'Player Count': 0
                    })
                    continue
                
                # Get values for this metric for this profile
                values = profile_df[matched_col].dropna()
                
                if len(values) > 0:
                    min_val = np.floor(values.min())
                    max_val = np.ceil(values.max())
                    player_count = len(values)
                else:
                    min_val = None
                    max_val = None
                    player_count = 0
                
                results.append({
                    'Position Profile': profile,
                    'Metric': metric_name,
                    'Column Name': matched_col,
                    'Min Value': int(min_val) if min_val is not None else None,
                    'Max Value': int(max_val) if max_val is not None else None,
                    'Player Count': player_count
                })
    
    else:
        # Multi-sheet mode - each sheet is a position profile
        for sheet_name in all_sheets_data.keys():
            df = all_sheets_data[sheet_name]
            
            # Get the config position for this sheet
            config_position = sheet_to_config.get(sheet_name, sheet_name)
            
            # Get metrics for this position from config
            if config_position not in radar_config:
                # Try reverse mapping
                reverse_map = {v: k for k, v in sheet_to_config.items()}
                config_position = reverse_map.get(sheet_name, sheet_name)
            
            if config_position not in radar_config:
                print(f"Warning: No config found for {sheet_name} (tried {config_position})")
                continue
            
            metrics_list = radar_config[config_position]
            
            # Get numeric columns from this sheet
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # For each metric in the config
            for metric_name in metrics_list:
                # Find the matching column in THIS sheet
                matched_col = find_best_column_match(metric_name, numeric_cols)
                
                if matched_col is None or matched_col not in df.columns:
                    # Metric not found in this sheet
                    results.append({
                        'Position Profile': sheet_name,
                        'Metric': metric_name,
                        'Column Name': 'NOT FOUND IN THIS SHEET',
                        'Min Value': None,
                        'Max Value': None,
                        'Player Count': 0
                    })
                    continue
                
                # Get values for this metric
                values = df[matched_col].dropna()
                
                if len(values) > 0:
                    min_val = np.floor(values.min())
                    max_val = np.ceil(values.max())
                    player_count = len(values)
                else:
                    min_val = None
                    max_val = None
                    player_count = 0
                
                results.append({
                    'Position Profile': sheet_name,
                    'Metric': metric_name,
                    'Column Name': matched_col,
                    'Min Value': int(min_val) if min_val is not None else None,
                    'Max Value': int(max_val) if max_val is not None else None,
                    'Player Count': player_count
                })
    
    return results

def main():
    """Main function to generate the CSV file."""
    print("Generating metric ranges CSV...")
    
    # Find player database
    player_db_file = find_player_database()
    if player_db_file is None:
        print(f"Error: No player database file found in {DATA_DIR}")
        print("Please upload a player database Excel file first.")
        return
    
    print(f"Found player database: {player_db_file}")
    
    # Load radar config
    print("Loading radar chart configuration...")
    radar_config = load_radar_config()
    if not radar_config:
        print(f"Error: Could not load radar config from {CONFIG_PATH}")
        return
    
    print(f"Found {len(radar_config)} position profiles in config")
    
    # Calculate ranges (checking each sheet individually)
    print("Calculating min/max values for each metric per profile...")
    print("(Checking each sheet individually for accurate column matching)")
    results = calculate_metric_ranges(player_db_file, radar_config)
    
    if not results:
        print("No results generated. Check your data and config.")
        return
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by Position Profile and Metric
    results_df = results_df.sort_values(['Position Profile', 'Metric'])
    
    # Save to CSV
    output_file = BASE_DIR / 'metric_ranges_by_profile.csv'
    results_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Successfully generated: {output_file}")
    print(f"   Total rows: {len(results_df)}")
    print(f"   Position profiles: {results_df['Position Profile'].nunique()}")
    print(f"   Metrics: {results_df['Metric'].nunique()}")
    
    # Show summary
    print("\nSummary by Position Profile:")
    summary = results_df.groupby('Position Profile').agg({
        'Metric': 'count',
        'Player Count': 'mean'
    }).round(0)
    summary.columns = ['Metric Count', 'Avg Players per Metric']
    print(summary)

if __name__ == '__main__':
    main()

