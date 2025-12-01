#!/usr/bin/env python3
"""
Process all conferences (BIG10, BIG12, IVY, SEC) for Center Back scoring
with historical context and team-by-team organization.
"""

import pandas as pd
import json
from pathlib import Path

def main():
    """Process all conferences."""
    
    # Configuration
    base_dir = Path(__file__).parent
    config_file = base_dir / "ACC 2025 CB Hybrid Sample" / "position_metrics_config.json"
    exports_dir = base_dir / "Exports"
    historical_dir = exports_dir / "Past Seasons"
    
    conferences = ['BIG10', 'BIG12', 'IVY', 'SEC']
    
    print("🏈 Processing All Conferences for Center Back Scoring")
    print("=" * 70)
    
    # Load config once
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    cb_config = config['position_profiles']['Center Back']
    
    # Process each conference
    for conference in conferences:
        print(f"\n{'='*70}")
        print(f"📊 Processing {conference}")
        print(f"{'='*70}")
        
        try:
            process_conference(conference, cb_config, exports_dir, historical_dir)
        except Exception as e:
            print(f"❌ Error processing {conference}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"✅ All Conferences Processed!")
    print(f"{'='*70}")

def process_conference(conference, cb_config, exports_dir, historical_dir):
    """Process a single conference."""
    
    # Load historical data
    print(f"\n📚 Loading Historical Data (2021-2024)...")
    historical_years = [2021, 2022, 2023, 2024]
    historical_data = []
    
    for year in historical_years:
        hist_file = historical_dir / f"CB Hybrid {conference} {year}.xlsx"
        if hist_file.exists():
            df_hist = pd.read_excel(hist_file)
            df_hist['Year'] = year
            df_hist['Season'] = str(year)
            historical_data.append(df_hist)
            print(f"  ✅ Loaded {len(df_hist)} players from {year}")
    
    # Combine historical data
    if historical_data:
        df_historical = pd.concat(historical_data, ignore_index=True)
        print(f"  📊 Total historical players: {len(df_historical)}")
    else:
        print(f"  ⚠️  No historical data found")
        df_historical = pd.DataFrame()
    
    # Load 2025 data
    print(f"\n📊 Loading 2025 Data...")
    data_2025 = exports_dir / f"CB Hybrid {conference} 2025.xlsx"
    
    if not data_2025.exists():
        print(f"  ❌ {data_2025.name} not found")
        return
    
    df_2025 = pd.read_excel(data_2025)
    df_2025['Year'] = 2025
    df_2025['Season'] = '2025'
    df_2025['Conference'] = conference
    df_2025['Position'] = 'Center Back'
    print(f"  ✅ Loaded {len(df_2025)} players from 2025")
    
    # Combine for normalization
    if not df_historical.empty:
        df_all = pd.concat([df_historical, df_2025], ignore_index=True)
        print(f"\n🔢 Combined Dataset: {len(df_all)} total players")
    else:
        df_all = df_2025
    
    # Calculate scores for both variants
    variants = [
        ('Intent_Focused', 0.80, 0.20),
        ('Balanced', 0.60, 0.40)
    ]
    
    for variant_name, pass_attempt_weight, pass_accuracy_weight in variants:
        print(f"\n  📋 {variant_name} Variant ({int(pass_attempt_weight*100)}/{int(pass_accuracy_weight*100)})")
        
        df_result = calculate_with_historical_normalization(
            df_2025, df_all, cb_config, pass_attempt_weight, pass_accuracy_weight
        )
        
        # Create team-by-team version
        create_team_tabs(df_result, conference, variant_name)
        
        print(f"  ✅ Complete")

def calculate_with_historical_normalization(df_2025, df_all, config, pass_attempt_weight, pass_accuracy_weight):
    """Calculate scores normalizing against combined historical + current data."""
    
    df_work = df_2025.copy()
    
    # Adjust pass weights
    for metric_name, metric_config in config['metrics']['Specific'].items():
        if isinstance(metric_config, dict) and 'components' in metric_config:
            if any('pass' in k.lower() and 'accurate' in k.lower() for k in metric_config['components'].keys()):
                new_components = {}
                for comp, weight in metric_config['components'].items():
                    if 'accurate' in comp.lower():
                        new_components[comp] = pass_accuracy_weight
                    else:
                        new_components[comp] = pass_attempt_weight
                total = sum(new_components.values())
                metric_config['components'] = {k: v/total for k, v in new_components.items()}
    
    # Calculate scores
    core_score, specific_score = calculate_scores_historical(df_work, df_all, config)
    
    # Calculate total
    total_score = (core_score * config['weightings']['Core']) + (specific_score * config['weightings']['Specific'])
    
    # Add to dataframe
    df_work['Core_Score_Original'] = core_score
    df_work['Specific_Score_Original'] = specific_score
    df_work['Total_Score_Original'] = total_score
    
    # Convert to 1-10 scale
    df_work['Total_Score_1_10'] = convert_to_1_10_scale(total_score)
    df_work['Total_Percentile'] = calculate_percentile(total_score)
    df_work['Total_Grade'] = assign_grade(df_work['Total_Score_1_10'])
    
    # Round all numeric columns
    numeric_cols = df_work.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        df_work[col] = df_work[col].round(2)
    
    return df_work

def create_team_tabs(df, conference, variant_name):
    """Create team-by-team Excel file."""
    
    base_dir = Path(__file__).parent
    output_file = base_dir / f"{conference}_2025_CB_{variant_name}_By_Team.xlsx"
    
    # Remove Age column if exists
    if 'Age' in df.columns:
        df = df.drop(columns=['Age'])
    
    # Reorder columns: Move scoring columns after Team
    cols = df.columns.tolist()
    for col_to_move in ['Total_Score_1_10', 'Total_Percentile', 'Total_Grade']:
        if col_to_move in cols:
            cols.remove(col_to_move)
    
    if 'Team' in cols:
        team_idx = cols.index('Team')
        cols.insert(team_idx + 1, 'Total_Score_1_10')
        cols.insert(team_idx + 2, 'Total_Percentile')
        cols.insert(team_idx + 3, 'Total_Grade')
    
    df = df[cols]
    
    # Get unique teams
    teams = sorted(df['Team'].unique())
    
    # Create Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # All players sheet
        df.to_excel(writer, sheet_name='All Players', index=False)
        
        # Team sheets
        for team in teams:
            team_df = df[df['Team'] == team].sort_values('Total_Score_1_10', ascending=False)
            sheet_name = team[:31] if len(team) > 31 else team
            team_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"    ✅ Saved: {output_file.name} ({len(teams)} teams)")

def calculate_scores_historical(df_2025, df_all, config):
    """Calculate scores normalizing against all historical data."""
    core_score = pd.Series(0.0, index=df_2025.index)
    specific_score = pd.Series(0.0, index=df_2025.index)
    
    for metric_name, metric_config in config['metrics']['Core'].items():
        if isinstance(metric_config, dict):
            weight = metric_config['weight']
            metric_score = calculate_combined_metric_historical(df_2025, df_all, metric_config)
            core_score += metric_score * weight
    
    for metric_name, metric_config in config['metrics']['Specific'].items():
        if isinstance(metric_config, dict):
            weight = metric_config['weight']
            metric_score = calculate_combined_metric_historical(df_2025, df_all, metric_config)
            specific_score += metric_score * weight
    
    return core_score, specific_score

def calculate_combined_metric_historical(df_2025, df_all, metric_config):
    """Calculate metric using historical normalization."""
    total_score = pd.Series(0.0, index=df_2025.index)
    total_weight = 0.0
    
    if 'components' in metric_config:
        for component, weight in metric_config['components'].items():
            if component in df_2025.columns and component in df_all.columns:
                normalized = normalize_metric_historical(df_2025[component], df_all[component])
                total_score += normalized * weight
                total_weight += weight
    
    if total_weight > 0:
        total_score = total_score / total_weight
    
    return total_score

def normalize_metric_historical(series_2025, series_all):
    """Normalize using combined historical + current min/max."""
    if series_all.isna().all():
        return pd.Series([0.1] * len(series_2025), index=series_2025.index)
    
    if series_all.max() <= 100 and series_all.min() >= 0:
        normalized = series_2025 / 100
    else:
        min_val, max_val = series_all.min(), series_all.max()
        if max_val == min_val:
            normalized = pd.Series([0.5] * len(series_2025), index=series_2025.index)
        else:
            normalized = (series_2025 - min_val) / (max_val - min_val)
    
    return normalized.fillna(0.1)

def convert_to_1_10_scale(score_series):
    scaled_scores = pd.Series(index=score_series.index, dtype=float)
    scaled_scores[score_series.isna()] = 1.0
    valid_scores = score_series.dropna()
    if len(valid_scores) == 0:
        return scaled_scores
    percentiles = valid_scores.rank(pct=True) * 100
    for i, percentile in percentiles.items():
        if percentile >= 90:
            scaled_scores[i] = 9 + (percentile - 90) / 10
        elif percentile >= 80:
            scaled_scores[i] = 8 + (percentile - 80) / 10
        elif percentile >= 70:
            scaled_scores[i] = 7 + (percentile - 70) / 10
        elif percentile >= 60:
            scaled_scores[i] = 6 + (percentile - 60) / 10
        elif percentile >= 50:
            scaled_scores[i] = 5 + (percentile - 50) / 10
        elif percentile >= 40:
            scaled_scores[i] = 4 + (percentile - 40) / 10
        elif percentile >= 30:
            scaled_scores[i] = 3 + (percentile - 30) / 10
        elif percentile >= 20:
            scaled_scores[i] = 2 + (percentile - 20) / 10
        elif percentile >= 10:
            scaled_scores[i] = 1 + (percentile - 10) / 10
        else:
            scaled_scores[i] = 1.0
    return scaled_scores

def calculate_percentile(score_series):
    percentiles = pd.Series(index=score_series.index, dtype=float)
    percentiles[score_series.isna()] = 0.0
    valid_scores = score_series.dropna()
    if len(valid_scores) > 0:
        valid_percentiles = valid_scores.rank(pct=True) * 100
        for i, pct in valid_percentiles.items():
            percentiles[i] = pct
    return percentiles

def assign_grade(score_series):
    def grade_function(score):
        if pd.isna(score):
            return 'F'
        elif score >= 9:
            return 'A'
        elif score >= 8:
            return 'B'
        elif score >= 7:
            return 'C'
        elif score >= 6:
            return 'D'
        else:
            return 'F'
    return score_series.apply(grade_function)

if __name__ == "__main__":
    main()
