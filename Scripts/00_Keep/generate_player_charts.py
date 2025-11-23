#!/usr/bin/env python3
"""
Generate visualization charts for player overview PDFs.
Creates radar charts, bar charts, and other visualizations to complement player data.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for PDF generation
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
import pandas as pd
from pathlib import Path

# Set style for professional-looking charts
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('default')
matplotlib.rcParams['font.size'] = 8
matplotlib.rcParams['axes.labelsize'] = 8
matplotlib.rcParams['xtick.labelsize'] = 7
matplotlib.rcParams['ytick.labelsize'] = 7
matplotlib.rcParams['legend.fontsize'] = 7
matplotlib.rcParams['figure.titlesize'] = 9

def generate_performance_radar_charts(player_row, position_config, all_players_df=None, position_profile=None, shortlist_df=None):
    """
    Generate two radar charts: one for intensity metrics (per 90) and one for success/accuracy metrics (%).
    Shows player's metrics vs conference average and Power Five average.
    Includes ALL metrics from the position profile JSON config.
    
    Args:
        player_row: Player data row
        position_config: Position-specific metrics configuration
        all_players_df: DataFrame with all players for calculating averages
        position_profile: Player's position profile
    
    Returns:
        Dictionary with 'intensity' and 'accuracy' keys, each containing BytesIO object or None
    """
    if not position_config or 'metrics' not in position_config:
        return None
    
    if all_players_df is None or all_players_df.empty:
        # Try to use shortlist data if available
        return None
    
    if 'Position Profile' not in all_players_df.columns:
        return None
    
    try:
        # Get player's name for legend
        player_name = str(player_row.get('Player', 'Player')).strip()
        
        # Get player's conference
        player_conference = str(player_row.get('Conference', '')).strip()
        
        # Power Five conferences
        power_five = {'ACC', 'SEC', 'BIG10', 'Big Ten', 'BIG12', 'Big 12', 'PAC12', 'Pac-12'}
        
        # Filter to same position profile
        pos_players = all_players_df[all_players_df['Position Profile'] == position_profile].copy()
        if len(pos_players) == 0:
            return None
        
        # Filter conference players
        conf_players = pos_players[pos_players['Conference'] == player_conference].copy() if player_conference else pd.DataFrame()
        
        # Filter Power Five players
        power_five_players = pos_players[pos_players['Conference'].isin(power_five)].copy()
        
        # Select the 8 best metrics for each position profile for optimal radar chart visualization
        # Note: All metrics must exist in the player data
        position_best_metrics = {
            'Hybrid CB': [
                'Aerial duels per 90',
                'Aerial duels won, %',
                'Defensive duels per 90',
                'Defensive duels won, %',
                'Progressive passes per 90',
                'Accurate progressive passes, %',
                'Shots blocked per 90',  # Replaced Clearances per 90
                'Interceptions per 90'
            ],
            'DM Box-To-Box': [
                'Defensive duels per 90',
                'Defensive duels won, %',
                'Progressive passes per 90',
                'Accurate progressive passes, %',
                'Long passes per 90',
                'Accurate long passes, %',
                'Deep completions per 90',  # Replaced Touches in box per 90
                'Goals per 90'
            ],
            'AM Advanced Playmaker': [
                'Assists per 90',
                'Smart passes per 90',  # Replaced Shot assists per 90
                'Progressive passes per 90',
                'Accurate progressive passes, %',
                'Through passes per 90',
                'Accurate through passes, %',
                'Dribbles per 90',
                'Successful dribbles, %'
            ],
            'Right Touchline Winger': [
                'Offensive duels per 90',
                'Offensive duels won, %',
                'Dribbles per 90',
                'Successful dribbles, %',
                'Crosses per 90',  # Replaced Crosses from right flank per 90
                'Accurate crosses, %',
                'Goals per 90',
                'Assists per 90'
            ]
        }
        
        # Get selected metrics for this position profile
        selected_metrics = position_best_metrics.get(position_profile, [])
        if not selected_metrics:
            return None
        
        # Collect selected metrics from position config
        all_metric_keys = []
        
        # Get Core metrics
        core_metrics = position_config['metrics'].get('Core', {})
        for metric_key in core_metrics.keys():
            if metric_key in selected_metrics:
                all_metric_keys.append(('Core', metric_key))
        
        # Get Specific metrics
        specific_metrics = position_config['metrics'].get('Specific', {})
        for metric_key in specific_metrics.keys():
            if metric_key in selected_metrics:
                all_metric_keys.append(('Specific', metric_key))
        
        # Also check components of composite metrics
        for metric_type, metric_key in [('Core', k) for k in core_metrics.keys()] + [('Specific', k) for k in specific_metrics.keys()]:
            if metric_type == 'Core':
                metric_config = core_metrics.get(metric_key)
            else:
                metric_config = specific_metrics.get(metric_key)
            
            if isinstance(metric_config, dict) and 'components' in metric_config:
                # Check if any component matches selected metrics
                for component_name in metric_config['components'].keys():
                    if component_name in selected_metrics and ('Core', metric_key) not in all_metric_keys and ('Specific', metric_key) not in all_metric_keys:
                        # Add the composite metric so we can extract the component
                        if metric_type == 'Core':
                            all_metric_keys.append(('Core', metric_key))
                        else:
                            all_metric_keys.append(('Specific', metric_key))
                        break
        
        if not all_metric_keys:
            return None
        
        # Prepare data - collect only selected individual metrics (including components from composite metrics)
        all_individual_metrics = []
        
        for metric_type, metric_key in all_metric_keys:
            metric_config = None
            if metric_type == 'Core':
                metric_config = core_metrics.get(metric_key)
            else:
                metric_config = specific_metrics.get(metric_key)
            
            if isinstance(metric_config, dict) and 'components' in metric_config:
                # Composite metric - include only selected components
                for component_name in metric_config['components'].keys():
                    if component_name in selected_metrics:
                        all_individual_metrics.append(component_name)
            else:
                # Single metric - include if selected
                if metric_key in selected_metrics:
                    all_individual_metrics.append(metric_key)
        
        # Remove duplicates while preserving order, and limit to 8 metrics
        seen = set()
        unique_metrics = []
        for metric in all_individual_metrics:
            if metric not in seen and metric in selected_metrics:
                seen.add(metric)
                unique_metrics.append(metric)
                if len(unique_metrics) >= 8:
                    break
        
        # Now find and process each metric, separating into intensity and accuracy
        # Also track original ranges for scale display
        intensity_categories = []
        intensity_player_values = []
        intensity_power_five_avg_values = []
        intensity_ranges = []  # Store (min, max) for each metric
        
        accuracy_categories = []
        accuracy_player_values = []
        accuracy_power_five_avg_values = []
        accuracy_ranges = []  # Store (min, max) for each metric
        
        for metric_name in unique_metrics:
            # Try to find metric column - handle both "per 90" and percentage metrics
            metric_col = None
            
            # Normalize metric name for matching
            metric_lower = metric_name.lower().strip()
            metric_normalized = metric_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
            
            # Try exact match first (most precise)
            for col in player_row.index:
                col_lower = str(col).lower().strip()
                col_normalized = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                
                if col_normalized == metric_normalized:
                    metric_col = col
                    break
            
            # If exact match not found, try partial match (but be more careful)
            if not metric_col:
                for col in player_row.index:
                    col_lower = str(col).lower().strip()
                    col_normalized = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                    
                    # For multi-word metrics, require word boundary matching
                    metric_words = set(metric_normalized.split())
                    col_words = set(col_normalized.split())
                    
                    # If all metric words are in column (for composite metrics like "Short / medium passes")
                    if metric_words and metric_words.issubset(col_words):
                        metric_col = col
                        break
                    
                    # For single-word or short metrics, check if metric is contained in column
                    if len(metric_words) == 1 and metric_normalized in col_normalized:
                        # Make sure it's not a substring (e.g., "passes" shouldn't match "progressive passes")
                        if metric_normalized == col_normalized or col_normalized.startswith(metric_normalized + ' '):
                            metric_col = col
                            break
                    
                    # Special handling for PAdj metrics (they might be stored without PAdj prefix)
                    if 'padj' in metric_lower or 'interception' in metric_lower or 'sliding' in metric_lower:
                        metric_base = metric_normalized.replace('padj ', '').replace('interceptions', 'interception').replace('sliding tackles', 'sliding tackle')
                        if metric_base in col_normalized or col_normalized in metric_base:
                            metric_col = col
                            break
                    
                    # Special handling for "Interceptions + Sliding Tackles" combined metric
                    if 'interception' in metric_lower and 'sliding' in metric_lower:
                        if 'interception' in col_lower and ('sliding' in col_lower or 'tackle' in col_lower):
                            metric_col = col
                            break
                    
                    # Special handling for "Crosses from right flank" -> might be "Crosses from right flank per 90" or "Crosses per 90"
                    if 'cross' in metric_lower and 'right' in metric_lower:
                        if 'cross' in col_lower and ('right' in col_lower or 'flank' in col_lower):
                            metric_col = col
                            break
                        # Fallback: just "Crosses per 90"
                        elif 'cross' in col_lower and 'per 90' in col_lower:
                            metric_col = col
                            break
                    
                    # Special handling for "Accelerations" -> might be "Accelerations per 90"
                    if 'acceleration' in metric_lower:
                        if 'acceleration' in col_lower or 'accel' in col_lower:
                            metric_col = col
                            break
                    
                    # Special handling for assist metrics (Shot assists, Second assists, Third assists)
                    if 'assist' in metric_lower:
                        if 'shot assist' in metric_lower and 'shot assist' in col_lower:
                            metric_col = col
                            break
                        elif 'second assist' in metric_lower and 'second assist' in col_lower:
                            metric_col = col
                            break
                        elif 'third assist' in metric_lower and 'third assist' in col_lower:
                            metric_col = col
                            break
                        # Fallback: just "Assists per 90" for the main assists metric
                        elif metric_normalized == 'assists' and 'assist' in col_lower and 'shot' not in col_lower and 'second' not in col_lower and 'third' not in col_lower:
                            metric_col = col
                            break
            
            if metric_col and metric_col in player_row.index:
                player_val = player_row[metric_col]
                # Allow zero values - they're valid data points
                if pd.notna(player_val) and player_val != '':
                    try:
                        player_val = float(player_val)
                        # Zero is a valid value, don't skip it
                        
                        # Helper function to find matching column (case-insensitive)
                        def find_matching_column(target_col, available_cols):
                            target_lower = str(target_col).lower().strip()
                            for col in available_cols:
                                col_lower = str(col).lower().strip()
                                # Exact match
                                if col_lower == target_lower:
                                    return col
                                # Match without spaces/case differences
                                if col_lower.replace(' ', '') == target_lower.replace(' ', ''):
                                    return col
                                # Match core metric name (for variations like "Defensive Duels" vs "Defensive duels")
                                target_base = target_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('%', '').strip()
                                col_base = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('%', '').strip()
                                if target_base == col_base:
                                    return col
                            return None
                        
                        # Calculate averages - find matching column (case-insensitive)
                        # Use shortlist_df if available (has both per-90 and percentage metrics)
                        # Otherwise use all_players_df (conference reports, only per-90 metrics)
                        # Note: Removed conf_avg - only using Power Five average now
                        power_five_avg = None
                        metric_min = None
                        metric_max = None
                        
                        # Determine which data source to use
                        data_source = None
                        if shortlist_df is not None and not shortlist_df.empty:
                            # Use shortlist (has all metrics)
                            pos_players_source = shortlist_df[shortlist_df.get('Position Profile', '') == position_profile].copy()
                            # Match conference (handle variations - convert to string and normalize)
                            if 'Conference' in pos_players_source.columns:
                                pos_players_source['Conference'] = pos_players_source['Conference'].astype(str).str.strip()
                                conf_players_source = pos_players_source[
                                    pos_players_source['Conference'].str.upper() == player_conference.upper().strip()
                                ].copy()
                                power_five_set = {'ACC', 'SEC', 'BIG10', 'BIG TEN', 'BIG12', 'BIG 12', 'PAC12', 'PAC-12'}
                                power_five_players_source = pos_players_source[
                                    pos_players_source['Conference'].str.upper().isin([c.upper() for c in power_five_set])
                                ].copy()
                            else:
                                conf_players_source = pd.DataFrame()
                                power_five_players_source = pd.DataFrame()
                            data_source = 'shortlist'
                        else:
                            # Use conference reports (only per-90)
                            conf_players_source = conf_players
                            power_five_players_source = power_five_players
                            data_source = 'conference'
                        
                        if len(power_five_players_source) > 0:
                            matching_col = find_matching_column(metric_col, power_five_players_source.columns)
                            if matching_col:
                                power_five_values = pd.to_numeric(power_five_players_source[matching_col], errors='coerce')
                                power_five_values = power_five_values[power_five_values > 0]  # Filter out zeros/negatives
                                if len(power_five_values) > 0:
                                    power_five_avg = power_five_values.mean()
                                    metric_min = power_five_values.min()
                                    metric_max = power_five_values.max()
                                else:
                                    power_five_avg = None
                        
                        # Determine if this is a percentage/accuracy metric (check BEFORE normalization)
                        metric_has_pct = '%' in metric_name
                        col_has_pct = '%' in str(metric_col)
                        metric_has_won = 'won' in metric_lower
                        metric_has_accurate = 'accurate' in metric_lower
                        metric_has_successful = 'successful' in metric_lower
                        
                        is_percentage = (
                            metric_has_pct or 
                            col_has_pct or
                            (metric_has_won and col_has_pct) or
                            (metric_has_accurate and col_has_pct) or
                            (metric_has_successful and col_has_pct)
                        )
                        
                        # If we're using shortlist_df, we already have the right data above
                        # If we're using all_players_df and it's a percentage metric, we won't find it (expected)
                        
                        # Normalize to 0-100 scale
                        # For percentage metrics, if we still don't have averages, use player value directly
                        if power_five_avg is None and is_percentage:
                            # Percentage metric without averages - use player value directly (already 0-100)
                            player_normalized = min(100, max(0, player_val))
                            power_five_normalized = 0  # No average to show
                            metric_min = 0
                            metric_max = 100
                        else:
                            # Per-90 metrics or percentage metrics with averages
                            # Check if we have at least one valid value (player or average)
                            # Allow zero values - they're valid data points
                            has_player_val = player_val is not None and pd.notna(player_val)
                            has_power_five_avg = power_five_avg is not None and pd.notna(power_five_avg) and power_five_avg > 0
                            
                            if not has_player_val and not has_power_five_avg:
                                continue
                            
                            # Use the range from Power Five data if available, otherwise use player value
                            if metric_min is None or metric_max is None:
                                # Need to calculate range from available data
                                if has_power_five_avg:
                                    # Use Power Five range (already calculated above)
                                    if metric_min is None:
                                        metric_min = 0  # Default to 0 if not set
                                    if metric_max is None:
                                        metric_max = power_five_avg * 2  # Use 2x average as max if not set
                                elif has_player_val:
                                    # Use player value as baseline
                                    metric_min = 0
                                    metric_max = max(player_val * 1.5, 1)  # At least 1, or 1.5x player value
                                else:
                                    continue
                            
                            # Ensure player value is included in range (even if it's 0)
                            if has_player_val:
                                metric_min = min(metric_min, player_val)
                                metric_max = max(metric_max, player_val)
                            
                            # Use range-based normalization to ensure averages are visible
                            # Add 10% padding to the range to make differences more visible
                            range_val = metric_max - metric_min
                            if range_val == 0:
                                range_val = metric_max if metric_max > 0 else 1
                            
                            # Normalize with padding
                            padding = range_val * 0.1
                            scale_max = metric_max + padding
                            scale_min = metric_min
                            
                            if scale_max > scale_min:
                                # Normalize player value (allow 0)
                                if has_player_val:
                                    player_normalized = min(100, max(0, ((player_val - scale_min) / (scale_max - scale_min)) * 100))
                                else:
                                    player_normalized = 0
                                
                                # Normalize Power Five average
                                if has_power_five_avg:
                                    power_five_normalized = min(100, max(0, ((power_five_avg - scale_min) / (scale_max - scale_min)) * 100))
                                else:
                                    power_five_normalized = 0
                            else:
                                continue
                        
                        # Format display name
                        display_name = metric_name.replace('PAdj ', '')
                        # Truncate if too long
                        if len(display_name) > 20:
                            display_name = display_name[:17] + '...'
                        
                        # Categorize and add to appropriate list (for BOTH paths)
                        # Store metric category for sorting
                        metric_category = _categorize_metric(display_name)
                        
                        if is_percentage:
                            accuracy_categories.append((display_name, metric_category))
                            accuracy_player_values.append(player_normalized)
                            accuracy_power_five_avg_values.append(power_five_normalized)
                            accuracy_ranges.append((metric_min, metric_max))
                        else:
                            intensity_categories.append((display_name, metric_category))
                            intensity_player_values.append(player_normalized)
                            intensity_power_five_avg_values.append(power_five_normalized)
                            intensity_ranges.append((metric_min, metric_max))
                    except (ValueError, TypeError):
                        continue
        
        # Sort metrics by category (defensive, passing, attacking)
        def sort_key(item):
            name, category = item
            category_order = {'defensive': 0, 'passing': 1, 'attacking': 2, 'other': 3}
            return (category_order.get(category, 3), name)
        
        # Sort and extract names
        if len(intensity_categories) >= 3:
            intensity_categories_sorted = sorted(intensity_categories, key=sort_key)
            # Reorder values to match sorted categories
            sorted_indices = [intensity_categories.index(item) for item in intensity_categories_sorted]
            intensity_categories = [item[0] for item in intensity_categories_sorted]
            intensity_player_values = [intensity_player_values[i] for i in sorted_indices]
            intensity_power_five_avg_values = [intensity_power_five_avg_values[i] for i in sorted_indices]
            intensity_ranges = [intensity_ranges[i] for i in sorted_indices]
        
        if len(accuracy_categories) >= 3:
            accuracy_categories_sorted = sorted(accuracy_categories, key=sort_key)
            sorted_indices = [accuracy_categories.index(item) for item in accuracy_categories_sorted]
            accuracy_categories = [item[0] for item in accuracy_categories_sorted]
            accuracy_player_values = [accuracy_player_values[i] for i in sorted_indices]
            accuracy_power_five_avg_values = [accuracy_power_five_avg_values[i] for i in sorted_indices]
            accuracy_ranges = [accuracy_ranges[i] for i in sorted_indices]
        
        # Combine all metrics into one radar chart
        charts = {}
        
        # Combine intensity and accuracy metrics
        # Extract just the names from tuples
        all_categories = [item[0] if isinstance(item, tuple) else item for item in intensity_categories] + \
                        [item[0] if isinstance(item, tuple) else item for item in accuracy_categories]
        all_player_values = intensity_player_values + accuracy_player_values
        all_power_five_avg_values = intensity_power_five_avg_values + accuracy_power_five_avg_values
        all_ranges = intensity_ranges + accuracy_ranges
        
        # Generate single combined radar chart
        if len(all_categories) >= 3:
            combined_buffer = _create_radar_chart(
                all_categories,
                all_player_values,
                all_power_five_avg_values,
                all_ranges,
                'Performance Metrics',
                player_name=player_name
            )
            if combined_buffer:
                charts['combined'] = combined_buffer
        
        return charts
        
    except Exception as e:
        print(f"  ⚠️  Error generating radar charts: {e}")
        import traceback
        traceback.print_exc()
        plt.close()
        return {}

def _categorize_metric(metric_name):
    """Categorize a metric as defensive, passing, or attacking."""
    name_lower = metric_name.lower()
    
    # Defensive metrics
    defensive_keywords = ['defensive', 'tackle', 'clearance', 'interception', 'aerial', 'duel', 'block', 'foul']
    if any(keyword in name_lower for keyword in defensive_keywords):
        return 'defensive'
    
    # Passing metrics
    passing_keywords = ['pass', 'assist', 'cross', 'progressive', 'long pass', 'short pass', 'medium pass']
    if any(keyword in name_lower for keyword in passing_keywords):
        return 'passing'
    
    # Attacking metrics
    attacking_keywords = ['goal', 'shot', 'dribble', 'offensive', 'xg', 'xg per', 'touch', 'key pass']
    if any(keyword in name_lower for keyword in attacking_keywords):
        return 'attacking'
    
    return 'other'

def _create_radar_chart(categories, player_values, power_five_avg_values, ranges, title_suffix, player_name='Player'):
    """Helper function to create a single radar chart - styled like Cibao project."""
    try:
        # Helper function to capitalize first letter of every word
        def capitalize_words(text):
            """Capitalize first letter of every word."""
            return ' '.join(word.capitalize() for word in text.split())
        
        # Create radar chart with white background
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(projection='polar'), 
                              facecolor='white')
        ax.set_facecolor('white')
        
        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        # Complete the data
        player_values += player_values[:1]
        power_five_avg_values += power_five_avg_values[:1]
        
        # Always plot averages if we have any non-zero values
        has_pf_data = any(v > 0.1 for v in power_five_avg_values[:-1])
        
        # Plot with filled polygons - thinner lines
        # Player - Portland Thorns dark red (#8B0000) with semi-transparent fill
        ax.fill(angles, player_values, alpha=0.2, color='#8B0000', zorder=1)
        ax.plot(angles, player_values, 'o-', linewidth=2, label=player_name, 
               color='#8B0000', markersize=5, markerfacecolor='#8B0000', 
               markeredgecolor='#8B0000', zorder=2)
        
        # Power Five Average - dark grey with semi-transparent fill
        if has_pf_data:
            ax.fill(angles, power_five_avg_values, alpha=0.2, color='#34495e', zorder=1)
            ax.plot(angles, power_five_avg_values, '-', linewidth=1.5, 
                   label='Power Five Avg', color='#34495e', 
                   marker='o', markersize=3, markerfacecolor='#34495e', 
                   markeredgecolor='#34495e', zorder=2)
        
        # Capitalize metric labels and add scale
        capitalized_categories_with_scale = []
        for i, cat in enumerate(categories):
            capitalized = capitalize_words(cat)
            # Add scale if available
            if i < len(ranges) and ranges[i][0] is not None and ranges[i][1] is not None:
                min_val, max_val = ranges[i]
                if '%' in cat or 'won' in cat.lower() or 'accurate' in cat.lower() or 'successful' in cat.lower():
                    # Percentage metric
                    scale_text = f"({min_val:.0f}-{max_val:.0f}%)"
                else:
                    # Per-90 metric
                    scale_text = f"(0-{max_val:.1f})"
                capitalized_categories_with_scale.append(f"{capitalized}\n{scale_text}")
            else:
                capitalized_categories_with_scale.append(capitalized)
        
        # Set labels - black text, larger font, with scale
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(capitalized_categories_with_scale, fontsize=8, color='#000000', wrap=True)
        ax.set_ylim(0, 100)
        # Hide radial tick labels
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['', '', '', ''], fontsize=0)  # Hide labels
        # Grid - grey, semi-transparent
        ax.grid(True, color='#bdc3c7', linewidth=1, linestyle='-', alpha=0.5)
        ax.spines['polar'].set_visible(False)
        
        # Title - capitalize and black text, set separately
        title = capitalize_words(title_suffix)
        ax.set_title(title, fontsize=9, fontweight='bold', pad=12, color='#000000', y=1.20)
        
        # Add subtitle separately below title to avoid overlap
        ax.text(0.5, 1.12, "(8 key metrics vs Power Five average)", 
               transform=ax.transAxes, fontsize=7, ha='center', va='bottom',
               style='normal', weight='normal', color='#000000')
        
        # Legend - horizontal, one line, positioned above chart (off the chart)
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), 
                          fontsize=8, frameon=True, fancybox=True, 
                          framealpha=0.9, facecolor='white', edgecolor='#bdc3c7',
                          ncol=2, mode='expand')  # ncol=2 for better spacing
        for text in legend.get_texts():
            text.set_color('#000000')
        
        # Save to BytesIO with white background
        img_buffer = BytesIO()
        plt.tight_layout(pad=1.5, rect=[0, 0, 1, 0.90])  # Leave more space at top for legend
        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', transparent=False)
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    except Exception as e:
        print(f"  ⚠️  Error creating radar chart: {e}")
        plt.close()
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error generating radar charts: {e}")
        import traceback
        traceback.print_exc()
        plt.close()
        return {}

def generate_consistency_chart(player_row):
    """
    Generate a stacked bar chart showing metrics above/below/at average.
    
    Args:
        player_row: Player data row
    
    Returns:
        BytesIO object with chart image, or None if unable to generate
    """
    try:
        metrics_above = player_row.get('Metrics Above Avg', 0)
        metrics_below = player_row.get('Metrics Below Avg', 0)
        metrics_at = player_row.get('Metrics At Avg', 0)
        
        # Convert to integers
        if pd.notna(metrics_above):
            if isinstance(metrics_above, str) and '/' in metrics_above:
                metrics_above = int(metrics_above.split('/')[0])
            else:
                metrics_above = int(metrics_above)
        else:
            metrics_above = 0
        
        if pd.notna(metrics_below):
            if isinstance(metrics_below, str) and '/' in metrics_below:
                metrics_below = int(metrics_below.split('/')[0])
            else:
                metrics_below = int(metrics_below)
        else:
            metrics_below = 0
        
        if pd.notna(metrics_at):
            if isinstance(metrics_at, str) and '/' in metrics_at:
                metrics_at = int(metrics_at.split('/')[0])
            else:
                metrics_at = int(metrics_at)
        else:
            metrics_at = 0
        
        total = metrics_above + metrics_below + metrics_at
        if total == 0:
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(4, 4))
        
        # Create stacked bar
        bars = ax.barh(0, [metrics_above, metrics_at, metrics_below], 
                       left=[0, metrics_above, metrics_above + metrics_at],
                       color=['#2ecc71', '#f39c12', '#e74c3c'], 
                       height=0.6, edgecolor='white', linewidth=1)
        
        # Add value labels
        if metrics_above > 0:
            ax.text(metrics_above / 2, 0, f'{metrics_above}', 
                   ha='center', va='center', fontweight='bold', fontsize=8, color='white')
        if metrics_at > 0:
            ax.text(metrics_above + metrics_at / 2, 0, f'{metrics_at}', 
                   ha='center', va='center', fontweight='bold', fontsize=8, color='white')
        if metrics_below > 0:
            ax.text(metrics_above + metrics_at + metrics_below / 2, 0, f'{metrics_below}', 
                   ha='center', va='center', fontweight='bold', fontsize=8, color='white')
        
        # Set labels
        ax.set_xlim(0, total)
        ax.set_xticks(range(0, total + 1, max(1, total // 5)))
        ax.set_xlabel('Number of Metrics', fontsize=8)
        ax.set_yticks([])
        ax.set_title('Consistency Score Breakdown', fontsize=9, fontweight='bold', pad=10)
        
        # Add legend
        legend_elements = [
            mpatches.Patch(facecolor='#2ecc71', label=f'Above Avg ({metrics_above})'),
            mpatches.Patch(facecolor='#f39c12', label=f'At Avg ({metrics_at})'),
            mpatches.Patch(facecolor='#e74c3c', label=f'Below Avg ({metrics_below})')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=7)
        
        # Add total label
        consistency_score = player_row.get('Consistency Score', 'N/A')
        if pd.notna(consistency_score):
            ax.text(total / 2, -0.3, f'Total: {total} metrics | Score: {consistency_score:.1f}/100', 
                   ha='center', va='top', fontsize=7, style='italic')
        
        plt.tight_layout(pad=1.0)
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
        
    except Exception as e:
        print(f"  ⚠️  Error generating consistency chart: {e}")
        plt.close()
        return None

def generate_top_metrics_chart(strengths, all_players_df=None):
    """
    Generate a horizontal bar chart comparing top 5 strengths vs position average.
    
    Args:
        strengths: List of strength dictionaries
        all_players_df: DataFrame with all players for calculating averages
    
    Returns:
        BytesIO object with chart image, or None if unable to generate
    """
    if not strengths or len(strengths) == 0:
        return None
    
    try:
        # Get top 5 strengths
        top_strengths = strengths[:5]
        
        metric_names = []
        player_values = []
        percentile_ranks = []
        
        for strength in top_strengths:
            metric = strength.get('metric', '')
            value = strength.get('value', 0)
            
            # Format metric name
            metric_display = metric.replace(' per 90', '').replace('PAdj ', '')[:25]
            metric_names.append(metric_display)
            player_values.append(value if pd.notna(value) else 0)
            
            # Get percentile rank if available
            if strength.get('power_five_rank') is not None and strength.get('power_five_total'):
                pct = (1 - (strength['power_five_rank'] - 1) / strength['power_five_total']) * 100
                percentile_ranks.append(f"{pct:.0f}th")
            elif strength.get('conference_rank') is not None and strength.get('conference_total'):
                pct = (1 - (strength['conference_rank'] - 1) / strength['conference_total']) * 100
                percentile_ranks.append(f"{pct:.0f}th")
            else:
                percentile_ranks.append('')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(4, 4))
        
        y_pos = np.arange(len(metric_names))
        bars = ax.barh(y_pos, player_values, color='#3498db', edgecolor='white', linewidth=1)
        
        # Add value labels on bars
        for i, (bar, val, pct) in enumerate(zip(bars, player_values, percentile_ranks)):
            width = bar.get_width()
            label = f'{val:.2f}'
            if pct:
                label += f' ({pct})'
            ax.text(width, bar.get_y() + bar.get_height()/2, label,
                   ha='left', va='center', fontsize=7, fontweight='bold', padx=5)
        
        # Set labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(metric_names, fontsize=7)
        ax.set_xlabel('Value', fontsize=8)
        ax.set_title('Top 5 Strengths', fontsize=9, fontweight='bold', pad=10)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout(pad=1.0)
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
        
    except Exception as e:
        print(f"  ⚠️  Error generating top metrics chart: {e}")
        plt.close()
        return None

def generate_style_fit_chart(player_row, thorns_ranks, position_profile, full_position_configs):
    """
    Generate a visualization showing Portland Thorns style fits.
    
    Args:
        player_row: Player data row
        thorns_ranks: Dictionary of Thorns ranks by metric
        position_profile: Player's position profile
        full_position_configs: Full position configurations
    
    Returns:
        BytesIO object with chart image, or None if unable to generate
    """
    try:
        style_fits = player_row.get('Style Fits', 0)
        if pd.isna(style_fits) or style_fits == 0:
            return None
        
        # Get style fit details (we'll create a simple visualization)
        # For now, show the count and create a visual representation
        fig, ax = plt.subplots(figsize=(4, 4))
        
        # Create a simple bar showing style fits
        fit_count = int(style_fits) if pd.notna(style_fits) else 0
        
        # Create a gauge-like visualization
        colors = ['#2ecc71'] * fit_count + ['#ecf0f1'] * (10 - fit_count)
        bars = ax.barh(0, [1] * 10, color=colors, height=0.4, edgecolor='white', linewidth=1)
        
        # Add text
        ax.text(5, 0, f'{fit_count} Style Fits', ha='center', va='center', 
               fontsize=10, fontweight='bold', color='#2c3e50')
        
        # Set labels
        ax.set_xlim(0, 10)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Portland Thorns Style Fit', fontsize=9, fontweight='bold', pad=10)
        
        # Add description
        ax.text(5, -0.3, f'Player excels in {fit_count} metric(s) where\nPortland Thorns rank in top 20% of NWSL', 
               ha='center', va='top', fontsize=7, style='italic', color='#7f8c8d')
        
        plt.tight_layout(pad=1.0)
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
        
    except Exception as e:
        print(f"  ⚠️  Error generating style fit chart: {e}")
        plt.close()
        return None

def generate_scatterplots(player_row, position_profile, all_players_df=None, shortlist_df=None):
    """
    Generate scatterplots for a player based on their position profile.
    
    Args:
        player_row: Player data row
        position_profile: Player's position profile
        all_players_df: DataFrame with all players for comparison
    
    Returns:
        Dictionary with scatterplot names as keys and BytesIO objects as values
    """
    charts = {}
    
    # Define scatterplot configurations for each position
    scatter_configs = {
        'Hybrid CB': [
            {
                'x_metric': 'Aerial duels per 90',
                'y_metric': 'Aerial duels won, %',
                'title': 'Aerial Duels: Intent vs Success Rate'
            },
            {
                'x_metric': 'Progressive passes per 90',
                'y_metric': 'Accurate progressive passes, %',
                'title': 'Progressive Passing: Intent vs Accuracy'
            },
            {
                'x_metric': 'Aerial duels per 90',
                'y_metric': 'Progressive passes per 90',
                'title': 'Aerial Duels vs Progressive Passes'
            }
        ],
        'DM Box-To-Box': [
            {
                'x_metric': 'Defensive duels per 90',
                'y_metric': 'Defensive duels won, %',
                'title': 'Defensive Duels: Intent vs Success Rate'
            },
            {
                'x_metric': 'Progressive passes per 90',
                'y_metric': 'Accurate progressive passes, %',
                'title': 'Progressive Passing: Intent vs Accuracy'
            },
            {
                'x_metric': 'Progressive passes per 90',
                'y_metric': 'Long passes per 90',
                'title': 'Progressive Passes vs Long Passes'
            }
        ],
        'Right Touchline Winger': [
            {
                'x_metric': 'Offensive duels per 90',
                'y_metric': 'Offensive duels won, %',
                'title': 'Offensive Duels: Intent vs Success Rate'
            },
            {
                'x_metric': 'Dribbles per 90',
                'y_metric': 'Successful dribbles, %',
                'title': 'Dribbling: Intent vs Success Rate'
            },
            {
                'x_metric': 'Offensive duels per 90',
                'y_metric': 'Crosses from right flank per 90',
                'title': 'Offensive Duels vs Crosses',
                'y_metric_alt': 'Crosses per 90'  # Fallback if 'Crosses from right flank per 90' not found
            }
        ],
        'AM Advanced Playmaker': [
            {
                'x_metric': 'Offensive duels per 90',
                'y_metric': 'Offensive duels won, %',
                'title': 'Offensive Duels: Intent vs Success Rate'
            },
            {
                'x_metric': 'Dribbles per 90',
                'y_metric': 'Successful dribbles, %',
                'title': 'Dribbling: Intent vs Success Rate'
            },
            {
                'x_metric': 'Goals per 90',
                'y_metric': 'Assists per 90 + Shot assists per 90 + Second assists per 90 + Third assists per 90',
                'title': 'Goals vs Total Assists'
            }
        ]
    }
    
    # Get scatterplot configs for this position
    configs = scatter_configs.get(position_profile, [])
    if not configs:
        return charts
    
    # Get all players of the same position for comparison
    # ALWAYS use shortlist_df if available (has percentage columns), otherwise use all_players_df
    # Conference reports don't have percentage columns, so we MUST use shortlist for scatterplots
    if shortlist_df is not None and not shortlist_df.empty:
        position_players = shortlist_df[shortlist_df.get('Position Profile', '') == position_profile].copy()
    elif all_players_df is not None and not all_players_df.empty:
        position_players = all_players_df[all_players_df.get('Position Profile', '') == position_profile].copy()
    else:
        position_players = pd.DataFrame()
    
    # Generate each scatterplot
    for idx, config in enumerate(configs):
        scatter = _create_scatterplot(
            player_row,
            config['x_metric'],
            config['y_metric'],
            config['title'],
            position_players,
            position_profile,
            config  # Pass full config for alternative metrics
        )
        if scatter:
            charts[f'scatter_{idx+1}'] = scatter
    
    return charts

def _create_scatterplot(player_row, x_metric, y_metric, title, position_players=None, position_profile=None, config=None):
    """
    Create a single scatterplot comparing player against position average.
    
    Args:
        player_row: Player data row
        x_metric: X-axis metric name
        y_metric: Y-axis metric name (can be composite)
        title: Chart title
        position_players: DataFrame with other players for comparison
        position_profile: Position profile name
    
    Returns:
        BytesIO object with chart image, or None if unable to generate
    """
    try:
        # Helper function to find matching column
        def find_metric_column(metric_name, available_cols):
            metric_lower = str(metric_name).lower().strip()
            for col in available_cols:
                col_lower = str(col).lower().strip()
                if col_lower == metric_lower:
                    return col
                # Try normalized matching
                col_norm = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('%', '').strip()
                metric_norm = metric_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('%', '').strip()
                if col_norm == metric_norm:
                    return col
                # Try word matching
                if metric_norm.replace(' ', '') == col_norm.replace(' ', ''):
                    return col
            return None
        
        # Get player's x value
        x_col = find_metric_column(x_metric, player_row.index)
        if not x_col or x_col not in player_row.index:
            return None
        
        player_x = player_row[x_col]
        if pd.isna(player_x) or player_x == '':
            return None
        try:
            player_x = float(player_x)
        except (ValueError, TypeError):
            return None
        
        # Handle alternative metric if specified (try primary first, then fallback)
        y_metric_to_use = y_metric
        if config and 'y_metric_alt' in config and config.get('y_metric_alt'):
            # Try primary metric first
            y_col_primary = find_metric_column(y_metric, player_row.index)
            if y_col_primary and y_col_primary in player_row.index:
                y_metric_to_use = y_metric
            else:
                # Fallback to alternative
                y_col_alt = find_metric_column(config['y_metric_alt'], player_row.index)
                if y_col_alt and y_col_alt in player_row.index:
                    y_metric_to_use = config['y_metric_alt']
        
        # Get player's y value (handle composite metrics)
        if ' + ' in y_metric_to_use:
            # Composite metric - sum the components
            components = [c.strip() for c in y_metric.split(' + ')]
            player_y = 0
            for component in components:
                y_col = find_metric_column(component, player_row.index)
                if y_col and y_col in player_row.index:
                    val = player_row[y_col]
                    if pd.notna(val) and val != '':
                        try:
                            player_y += float(val)
                        except (ValueError, TypeError):
                            pass
            # If composite metric sums to 0, still include it (player might have 0 assists)
            if player_y == 0 and all(component in player_row.index for component in components):
                # All components exist but sum to 0 - this is valid
                pass
            elif player_y == 0:
                # Some components missing - skip this scatterplot
                return None
        else:
            y_col = find_metric_column(y_metric_to_use, player_row.index)
            if not y_col or y_col not in player_row.index:
                return None
            player_y = player_row[y_col]
            if pd.isna(player_y) or player_y == '':
                return None
            try:
                player_y = float(player_y)
            except (ValueError, TypeError):
                return None
        
        # Use ALL players from all five conferences (not just Power Five)
        all_conference_players = position_players.copy() if position_players is not None and not position_players.empty else None
        
        # Get position averages for quadrant lines (from all conferences)
        avg_x = None
        avg_y = None
        if all_conference_players is not None and not all_conference_players.empty:
            if x_col in all_conference_players.columns:
                avg_x = pd.to_numeric(all_conference_players[x_col], errors='coerce').mean()
                if pd.isna(avg_x):
                    avg_x = None
            
            if ' + ' in y_metric_to_use:
                # For composite, calculate average of sum
                components = [c.strip() for c in y_metric_to_use.split(' + ')]
                y_values = []
                for component in components:
                    y_col = find_metric_column(component, all_conference_players.columns)
                    if y_col and y_col in all_conference_players.columns:
                        vals = pd.to_numeric(all_conference_players[y_col], errors='coerce')
                        y_values.append(vals)
                if y_values:
                    # Sum across components for each player, then average
                    combined = sum(y_values)
                    avg_y = combined.mean()
                    if pd.isna(avg_y):
                        avg_y = None
            else:
                y_col = find_metric_column(y_metric_to_use, all_conference_players.columns)
                if y_col and y_col in all_conference_players.columns:
                    avg_y = pd.to_numeric(all_conference_players[y_col], errors='coerce').mean()
                    if pd.isna(avg_y):
                        avg_y = None
        
        # Create scatterplot (smaller size to fit on one page)
        fig, ax = plt.subplots(figsize=(3, 3), facecolor='#f8f9fa')  # Light grey background
        ax.set_facecolor('#f8f9fa')  # Light grey background for plot area
        
        # Initialize lists for other players (outside if block so they're always available)
        other_players_x = []
        other_players_y = []
        
        # Plot all other players from all conferences as grey dots
        if all_conference_players is not None and not all_conference_players.empty:
            player_name = player_row.get('Player', '')
            player_team = player_row.get('Team', '')
            
            # Track which players we've already processed to avoid duplicates
            processed_players = set()
            
            for idx, other_player in all_conference_players.iterrows():
                # Skip the current player
                other_name = str(other_player.get('Player', '')).strip()
                other_team = str(other_player.get('Team', '')).strip()
                
                # Create unique identifier
                player_id = (other_name, other_team)
                
                # Skip if it's the current player OR if we've already processed this player
                if (other_name == player_name and other_team == player_team) or player_id in processed_players:
                    continue
                
                processed_players.add(player_id)
                
                # Get x value - use find_metric_column to find the correct column for this player
                other_x_col = find_metric_column(x_metric, other_player.index)
                if not other_x_col:
                    # Try direct column name match as fallback
                    if x_col in other_player.index:
                        other_x_col = x_col
                
                if other_x_col and other_x_col in other_player.index:
                    other_x = pd.to_numeric(other_player[other_x_col], errors='coerce')
                    if pd.isna(other_x) or other_x <= 0:
                        continue
                else:
                    continue
                
                # Get y value
                if ' + ' in y_metric_to_use:
                    # Composite metric
                    components = [c.strip() for c in y_metric_to_use.split(' + ')]
                    other_y = 0
                    all_components_found = True
                    for component in components:
                        other_y_col = find_metric_column(component, other_player.index)
                        if other_y_col and other_y_col in other_player.index:
                            val = pd.to_numeric(other_player[other_y_col], errors='coerce')
                            if pd.notna(val):
                                other_y += val
                            else:
                                all_components_found = False
                                break
                        else:
                            all_components_found = False
                            break
                    
                    if all_components_found and other_y >= 0:  # Allow 0 for composite metrics
                        other_players_x.append(other_x)
                        other_players_y.append(other_y)
                else:
                    other_y_col = find_metric_column(y_metric_to_use, other_player.index)
                    if not other_y_col:
                        # Try using the y_col we found for the player as fallback
                        y_col_for_player = find_metric_column(y_metric_to_use, player_row.index)
                        if y_col_for_player and y_col_for_player in other_player.index:
                            other_y_col = y_col_for_player
                    
                    if other_y_col and other_y_col in other_player.index:
                        other_y = pd.to_numeric(other_player[other_y_col], errors='coerce')
                        if pd.notna(other_y) and other_y >= 0:  # Allow 0 for percentage metrics
                            other_players_x.append(other_x)
                            other_players_y.append(other_y)
            
            # Plot other players with white outlines
            if len(other_players_x) == len(other_players_y) and len(other_players_x) > 0:
                ax.scatter(other_players_x, other_players_y, s=30, color='#bdc3c7', 
                          marker='o', alpha=0.6, zorder=1, edgecolors='white', linewidth=0.5)
        
        # Plot dashed average lines to create four quadrants
        if avg_x is not None:
            ax.axvline(avg_x, color='#95a5a6', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
        if avg_y is not None:
            ax.axhline(avg_y, color='#95a5a6', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
        
        # Quadrant shading will be done after axis limits are set (see below)
        
        # Plot player in Portland Thorns dark red (3x size of grey dots)
        ax.scatter(player_x, player_y, s=90, color='#8B0000', marker='o', 
                  edgecolors='white', linewidth=1, zorder=4, alpha=0.8)
        
        # Format axis labels - capitalize first letter of every word
        def capitalize_words(text):
            """Capitalize first letter of every word."""
            return ' '.join(word.capitalize() for word in text.split())
        
        x_label = x_metric.replace(' per 90', '/90').replace('PAdj ', '')
        y_label = y_metric_to_use.replace(' per 90', '/90').replace('PAdj ', '').replace(' + ', ' + ')
        
        # Capitalize words
        x_label = capitalize_words(x_label)
        y_label = capitalize_words(y_label)
        
        if len(x_label) > 30:
            x_label = x_label[:27] + '...'
        if len(y_label) > 30:
            y_label = y_label[:27] + '...'
        
        # Set axis limits - MUST include other_players data (calculated above in the loop)
        all_x_values = [player_x]
        all_y_values = [player_y]
        
        # Add other players' values (populated in the loop above)
        if len(other_players_x) > 0 and len(other_players_y) > 0:
            all_x_values.extend(other_players_x)
            all_y_values.extend(other_players_y)
        
        if all_x_values:
            x_min, x_max = min(all_x_values), max(all_x_values)
            x_range = x_max - x_min
            if x_range == 0:
                x_range = x_max * 0.1 if x_max > 0 else 1
            x_lim_low = max(0, x_min - x_range * 0.1)
            x_lim_high = x_max + x_range * 0.1
            ax.set_xlim(x_lim_low, x_lim_high)
        
        if all_y_values:
            y_min, y_max = min(all_y_values), max(all_y_values)
            y_range = y_max - y_min
            if y_range == 0:
                y_range = y_max * 0.1 if y_max > 0 else 1
            y_lim_low = max(0, y_min - y_range * 0.1)
            y_lim_high = y_max + y_range * 0.1
            ax.set_ylim(y_lim_low, y_lim_high)
        
        # Generate dynamic summary text based on player's position relative to averages
        player_name = str(player_row.get('Player', 'Player')).strip()
        dynamic_summary = ""
        
        if avg_x is not None and avg_y is not None:
            # Determine if player is above/below average for each metric
            x_above = player_x > avg_x
            y_above = player_y > avg_y
            
            # Get metric names for the summary
            x_metric_name = x_label.replace('/90', ' per 90').replace(' Per 90', ' per 90')
            y_metric_name = y_label.replace('%', '').strip()
            
            # Build summary text, allowing for line breaks if needed
            if x_above and y_above:
                summary_text = f"{player_name} is above average for both {x_metric_name} and {y_metric_name}"
            elif x_above and not y_above:
                summary_text = f"{player_name} is above average for {x_metric_name} but below average for {y_metric_name}"
            elif not x_above and y_above:
                summary_text = f"{player_name} is below average for {x_metric_name} but above average for {y_metric_name}"
            else:
                summary_text = f"{player_name} is below average for both {x_metric_name} and {y_metric_name}"
            
            # Split into two lines if too long (approximately 50 characters)
            if len(summary_text) > 50:
                # Try to split at a natural break point
                if ' but ' in summary_text:
                    parts = summary_text.split(' but ', 1)
                    dynamic_summary = f"{parts[0]}\nbut {parts[1]}"
                elif ' and ' in summary_text:
                    parts = summary_text.split(' and ', 1)
                    dynamic_summary = f"{parts[0]}\nand {parts[1]}"
                else:
                    # Split roughly in the middle
                    mid_point = len(summary_text) // 2
                    # Find nearest space
                    split_point = summary_text.rfind(' ', 0, mid_point + 10)
                    if split_point > 0:
                        dynamic_summary = f"{summary_text[:split_point]}\n{summary_text[split_point+1:]}"
                    else:
                        dynamic_summary = summary_text
            else:
                dynamic_summary = summary_text
        else:
            # Fallback to generic summary if averages not available
            if 'Intent' in title:
                dynamic_summary = "(Volume vs Success comparison)"
            elif 'Aerial' in title or 'Defensive' in title:
                dynamic_summary = "(Defensive action comparison)"
            elif 'Progressive' in title or 'Passes' in title:
                dynamic_summary = "(Passing quality comparison)"
            elif 'Dribbles' in title or 'Offensive' in title:
                dynamic_summary = "(Attacking action comparison)"
            elif 'Goals' in title or 'Assists' in title:
                dynamic_summary = "(Goal contribution comparison)"
        
        # Set uniform font size for title, axis labels, and tick labels
        uniform_fontsize = 8
        
        # Set axis labels with same font size
        ax.set_xlabel(x_label, fontsize=uniform_fontsize, fontweight='bold', labelpad=4)
        ax.set_ylabel(y_label, fontsize=uniform_fontsize, fontweight='bold', labelpad=4)
        
        # Make tick labels same size
        ax.tick_params(axis='both', which='major', labelsize=uniform_fontsize, pad=2)
        
        # Make both axis baselines black
        ax.spines['bottom'].set_color('black')
        ax.spines['left'].set_color('black')
        
        # Add arrows to show "better" direction - will be done after axis limits are set
        
        ax.grid(True, alpha=0.3, linestyle='--')
        # Legend removed per user request
        
        # Save the figure - CRITICAL: Set axis limits AFTER tight_layout to prevent override
        # Use tight_layout with extra top padding to make room for title and summary
        plt.tight_layout(pad=1.5, rect=[0, 0, 1, 0.70])  # rect=[left, bottom, right, top] - leave 30% at top
        
        # NOW set title and summary AFTER tight_layout so they don't get moved around
        # Set title first (bold) with proper padding - positioned higher
        ax.set_title(title, fontsize=uniform_fontsize, fontweight='bold', pad=8, y=1.16)
        
        # Add summary text below title (normal weight) with clear spacing
        if dynamic_summary:
            # Position summary text below the title using figure coordinates
            # This ensures it stays in the right place relative to the figure, not the axes
            fig = ax.figure
            # Position at 74% from bottom of figure (in the reserved top space, below title)
            fig.text(0.5, 0.74, dynamic_summary, fontsize=uniform_fontsize, 
                    ha='center', va='top', style='normal', weight='normal', color='black',
                    transform=fig.transFigure)
        
        # Re-apply axis limits AFTER tight_layout (it can override them)
        if len(all_x_values) > 1:  # Only if we have multiple data points
            ax.set_xlim(x_lim_low, x_lim_high)
        if len(all_y_values) > 1:
            ax.set_ylim(y_lim_low, y_lim_high)
        
        # Add player name label AFTER axis limits are set to avoid conflicts
        player_name = str(player_row.get('Player', 'Player')).strip()
        
        # Calculate smart label position based on player location and axis limits
        x_range = x_lim_high - x_lim_low
        y_range = y_lim_high - y_lim_low
        x_center = (x_lim_low + x_lim_high) / 2
        y_center = (y_lim_low + y_lim_high) / 2
        
        # Determine offset direction based on quadrant
        if player_x >= x_center and player_y >= y_center:
            # Top-right quadrant - place label top-right
            offset_x, offset_y = 20, 20
        elif player_x < x_center and player_y >= y_center:
            # Top-left quadrant - place label top-left
            offset_x, offset_y = -20, 20
        elif player_x >= x_center and player_y < y_center:
            # Bottom-right quadrant - place label bottom-right
            offset_x, offset_y = 20, -20
        else:
            # Bottom-left quadrant - place label bottom-left
            offset_x, offset_y = -20, -20
        
        # Adjust if player is near edges to avoid going off-chart
        edge_threshold = 0.12  # 12% of range from edge
        if player_y > (y_lim_high - y_range * edge_threshold):
            # Near top edge - move label down
            offset_y = -20
        elif player_y < (y_lim_low + y_range * edge_threshold):
            # Near bottom edge - move label up
            offset_y = 20
        
        if player_x > (x_lim_high - x_range * edge_threshold):
            # Near right edge - move label left
            offset_x = -20
        elif player_x < (x_lim_low + x_range * edge_threshold):
            # Near left edge - move label right
            offset_x = 20
        
        # Position label with calculated offset
        ax.annotate(player_name, xy=(player_x, player_y), 
                   xytext=(offset_x, offset_y), textcoords='offset points',
                   fontsize=8, fontweight='bold', color='#8B0000',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor='#8B0000', linewidth=1, alpha=0.9),
                   zorder=5, ha='center', va='center')
        
        # Shade quadrants - after setting limits
        if avg_x is not None and avg_y is not None:
            x_lims = ax.get_xlim()
            y_lims = ax.get_ylim()
            # Only shade if averages are within the visible range
            if x_lim_low <= avg_x <= x_lim_high and y_lim_low <= avg_y <= y_lim_high:
                from matplotlib.patches import Rectangle
                # Top right quadrant (good - above average in both) - green tint
                # Use Rectangle to ensure clean, single-color shading with no overlap
                top_right = Rectangle((avg_x, avg_y), x_lim_high - avg_x, y_lim_high - avg_y,
                                     facecolor='#2ecc71', alpha=0.15, zorder=0, edgecolor='none')
                ax.add_patch(top_right)
                # Bottom left quadrant (bad - below average in both) - muted orange/brown (NOT red)
                bottom_left = Rectangle((x_lim_low, y_lim_low), avg_x - x_lim_low, avg_y - y_lim_low,
                                       facecolor='#d35400', alpha=0.15, zorder=0, edgecolor='none')
                ax.add_patch(bottom_left)
        
        # Arrows removed per user request
        
        img_buffer = BytesIO()
        # Save WITHOUT bbox_inches='tight' to preserve axis limits
        # bbox_inches='tight' can crop the image and hide data points
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches=None, pad_inches=0.1, facecolor='white')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
        
    except Exception as e:
        print(f"  ⚠️  Error generating scatterplot ({title}): {e}")
        import traceback
        traceback.print_exc()
        plt.close()
        return None

def get_grade_from_score(score):
    """
    Convert total score to grade based on 1-10 scale.
    9+ = A, 8-8.99 = B, 7-7.99 = C, 6-6.99 = D, <6 = F
    """
    if pd.isna(score):
        return 'F'
    try:
        score = float(score)
        if score >= 9.0:
            return 'A'
        elif score >= 8.0:
            return 'B'
        elif score >= 7.0:
            return 'C'
        elif score >= 6.0:
            return 'D'
        else:
            return 'F'
    except (ValueError, TypeError):
        return 'F'

def get_grade_color(grade):
    """
    Get color for grade based on conference report color scale (same as Mike's reports).
    A = Dark Red, B = Red, C = Light Red, D = Light Blue, F = Dark Blue
    """
    grade_colors = {
        'A': '#8B0000',      # Dark red (Portland Thorns color)
        'B': '#C5504B',      # Red
        'C': '#F2A2A2',      # Light red
        'D': '#8FAADC',      # Light blue
        'F': '#1F4E79'       # Dark blue
    }
    return grade_colors.get(str(grade).upper(), '#95a5a6')  # Default grey

def generate_total_score_beeswarm(player_row, position_profile, shortlist_df=None, all_players_df=None):
    """
    Generate a horizontal beeswarm chart showing where the player's total score ranks
    compared to all other players in the same position profile.
    Colors circles based on grade (A=9+, B=8-8.99, C=7-7.99, D=6-6.99, F=<6).
    
    Args:
        player_row: Player data row
        position_profile: Player's position profile
        shortlist_df: DataFrame with all players (preferred source)
        all_players_df: Alternative DataFrame if shortlist_df not available
    
    Returns:
        BytesIO object with chart image or None
    """
    try:
        # Determine data source
        if shortlist_df is not None and not shortlist_df.empty:
            data_source = shortlist_df
        elif all_players_df is not None and not all_players_df.empty:
            data_source = all_players_df
        else:
            return None
        
        # Filter to same position profile
        position_players = data_source[data_source.get('Position Profile', '') == position_profile].copy()
        if position_players.empty:
            return None
        
        # Find Total Score column (try variations)
        total_score_col = None
        # First try to find "2025 Total Score" or "Total_Score_1_10"
        for col in position_players.columns:
            col_lower = str(col).lower()
            if ('2025' in col_lower and 'total score' in col_lower) or 'total_score_1_10' in col_lower:
                total_score_col = col
                break
        
        # If not found, try generic "Total Score"
        if not total_score_col:
            for col in position_players.columns:
                col_lower = str(col).lower()
                if 'total score' in col_lower or 'total_score' in col_lower or col_lower == 'total':
                    total_score_col = col
                    break
        
        # If still not found, try just "Score"
        if not total_score_col:
            for col in position_players.columns:
                col_lower = str(col).lower()
                if col_lower == 'score' and 'total' not in col_lower:
                    total_score_col = col
                    break
        
        if not total_score_col or total_score_col not in position_players.columns:
            return None
        
        # Get player's total score
        player_name = player_row.get('Player', '')
        player_team = player_row.get('Team', '')
        player_score = None
        
        # Find player in data
        for idx, row in position_players.iterrows():
            if str(row.get('Player', '')).strip() == str(player_name).strip() and \
               str(row.get('Team', '')).strip() == str(player_team).strip():
                player_score = row.get(total_score_col)
                if pd.notna(player_score):
                    try:
                        player_score = float(player_score)
                    except (ValueError, TypeError):
                        player_score = None
                break
        
        if player_score is None:
            return None
        
        # Get all other players' scores with their grades
        other_scores = []
        other_grades = []
        for idx, row in position_players.iterrows():
            other_name = str(row.get('Player', '')).strip()
            other_team = str(row.get('Team', '')).strip()
            
            # Skip current player
            if other_name == str(player_name).strip() and other_team == str(player_team).strip():
                continue
            
            score = row.get(total_score_col)
            if pd.notna(score):
                try:
                    score = float(score)
                    other_scores.append(score)
                    other_grades.append(get_grade_from_score(score))
                except (ValueError, TypeError):
                    continue
        
        if not other_scores:
            return None
        
        # Create horizontal beeswarm chart (smaller to fit on one page)
        fig, ax = plt.subplots(figsize=(6, 1.2), facecolor='white')
        ax.set_facecolor('white')
        
        # Set x-axis (score range) first so we can shade backgrounds
        all_scores = other_scores + [player_score]
        score_min = min(all_scores)
        score_max = max(all_scores)
        score_range = score_max - score_min
        padding = score_range * 0.1 if score_range > 0 else 1
        x_min = score_min - padding
        x_max = score_max + padding
        
        # Set y-axis limits
        y_min = -0.5
        y_max = 0.5
        
        # Shade background sections by grade
        # Grade boundaries: F (<6), D (6-6.99), C (7-7.99), B (8-8.99), A (9+)
        grade_ranges = [
            (x_min, 6.0, 'F', '#1F4E79'),      # Dark blue
            (6.0, 7.0, 'D', '#8FAADC'),        # Light blue
            (7.0, 8.0, 'C', '#F2A2A2'),        # Light red
            (8.0, 9.0, 'B', '#C5504B'),       # Red
            (9.0, x_max, 'A', '#8B0000')       # Dark red
        ]
        
        for range_min, range_max, grade, color in grade_ranges:
            # Only shade if the range overlaps with our data range
            if range_max > x_min and range_min < x_max:
                shade_min = max(range_min, x_min)
                shade_max = min(range_max, x_max)
                ax.axvspan(shade_min, shade_max, ymin=0, ymax=1, 
                          facecolor=color, alpha=0.25, zorder=0)  # Increased from 0.15 to 0.25
        
        # Create beeswarm effect by adding small random y-offsets
        np.random.seed(42)  # For reproducibility
        y_other = np.random.normal(0, 0.15, len(other_scores))
        y_player = 0  # Player at center
        
        # Plot all other players as grey circles
        ax.scatter(other_scores, y_other, s=40, c='#95a5a6', alpha=0.7, 
                  edgecolors='white', linewidth=0.5, zorder=2)
        
        # Plot player as red circle (Portland Thorns color)
        ax.scatter([player_score], [y_player], s=40, c='#8B0000', alpha=0.9, 
                  edgecolors='white', linewidth=1, zorder=3)
        
        # Set axis limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_yticks([])
        ax.set_yticklabels([])
        
        # Format x-axis (no label)
        ax.tick_params(axis='x', labelsize=9, colors='black')
        
        # Add title with summary
        ax.set_title('Total Score Ranking\n(Player position relative to all position peers)', 
                    fontsize=9, fontweight='bold', pad=6, color='black')
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#34495e')
        ax.spines['bottom'].set_linewidth(1)
        
        # Add grid for readability (above background shading)
        ax.grid(True, axis='x', color='#ecf0f1', linestyle='-', linewidth=0.5, alpha=0.5, zorder=1)
        
        # Add grade boundaries as vertical lines
        for boundary in [9.0, 8.0, 7.0, 6.0]:
            if boundary >= x_min and boundary <= x_max:
                ax.axvline(boundary, color='#bdc3c7', linestyle='--', linewidth=0.8, alpha=0.5, zorder=2)
        
        plt.tight_layout()
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
        
    except Exception as e:
        print(f"  ⚠️  Error generating total score beeswarm: {e}")
        import traceback
        traceback.print_exc()
        plt.close()
        return None

def generate_comparison_table(player_row, position_profile, shortlist_df=None, all_players_df=None):
    """
    Generate a comparison table showing the player vs all other players in the same position profile.
    Includes columns for each metric from the radar chart.
    
    Args:
        player_row: Player data row
        position_profile: Player's position profile
        shortlist_df: DataFrame with all players (preferred source)
        all_players_df: Alternative DataFrame if shortlist_df not available
    
    Returns:
        HTML string with the comparison table or None
    """
    try:
        # Get the 8 metrics for this position profile
        position_best_metrics = {
            'Hybrid CB': [
                'Aerial duels per 90',
                'Aerial duels won, %',
                'Defensive duels per 90',
                'Defensive duels won, %',
                'Progressive passes per 90',
                'Accurate progressive passes, %',
                'Shots blocked per 90',
                'Interceptions per 90'
            ],
            'DM Box-To-Box': [
                'Defensive duels per 90',
                'Defensive duels won, %',
                'Progressive passes per 90',
                'Accurate progressive passes, %',
                'Long passes per 90',
                'Accurate long passes, %',
                'Deep completions per 90',
                'Goals per 90'
            ],
            'AM Advanced Playmaker': [
                'Assists per 90',
                'Smart passes per 90',
                'Progressive passes per 90',
                'Accurate progressive passes, %',
                'Through passes per 90',
                'Accurate through passes, %',
                'Dribbles per 90',
                'Successful dribbles, %'
            ],
            'Right Touchline Winger': [
                'Offensive duels per 90',
                'Offensive duels won, %',
                'Dribbles per 90',
                'Successful dribbles, %',
                'Crosses per 90',
                'Accurate crosses, %',
                'Goals per 90',
                'Assists per 90'
            ]
        }
        
        selected_metrics = position_best_metrics.get(position_profile, [])
        if not selected_metrics:
            return None
        
        # Determine data source
        if shortlist_df is not None and not shortlist_df.empty:
            data_source = shortlist_df
        elif all_players_df is not None and not all_players_df.empty:
            data_source = all_players_df
        else:
            return None
        
        # Filter to same position profile
        position_players = data_source[data_source.get('Position Profile', '') == position_profile].copy()
        if position_players.empty:
            return None
        
        # Find Total Score column
        total_score_col = None
        for col in position_players.columns:
            col_lower = str(col).lower()
            if ('2025' in col_lower and 'total score' in col_lower) or 'total_score_1_10' in col_lower:
                total_score_col = col
                break
        if not total_score_col:
            for col in position_players.columns:
                col_lower = str(col).lower()
                if 'total score' in col_lower or 'total_score' in col_lower:
                    total_score_col = col
                    break
        
        # Get player info
        player_name = player_row.get('Player', '')
        player_team = player_row.get('Team', '')
        
        # Build table data
        table_rows = []
        player_row_data = None
        
        for idx, row in position_players.iterrows():
            other_name = str(row.get('Player', '')).strip()
            other_team = str(row.get('Team', '')).strip()
            
            # Get total score for ranking
            total_score = row.get(total_score_col) if total_score_col else None
            if pd.notna(total_score):
                try:
                    total_score = float(total_score)
                except (ValueError, TypeError):
                    total_score = 0
            else:
                total_score = 0
            
            # Get metric values
            metric_values = []
            for metric in selected_metrics:
                # Find matching column
                metric_col = None
                metric_lower = metric.lower().strip()
                metric_normalized = metric_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                
                for col in row.index:
                    col_lower = str(col).lower().strip()
                    col_normalized = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                    if col_normalized == metric_normalized:
                        metric_col = col
                        break
                
                if not metric_col:
                    for col in row.index:
                        col_lower = str(col).lower().strip()
                        col_normalized = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                        metric_words = set(metric_normalized.split())
                        col_words = set(col_normalized.split())
                        if metric_words and metric_words.issubset(col_words):
                            metric_col = col
                            break
                
                if metric_col and metric_col in row.index:
                    val = row.get(metric_col)
                    if pd.notna(val) and val != '':
                        try:
                            val = float(val)
                            metric_values.append(val)
                        except (ValueError, TypeError):
                            metric_values.append(None)
                    else:
                        metric_values.append(None)
                else:
                    metric_values.append(None)
            
            row_data = {
                'player': other_name,
                'team': other_team,
                'total_score': total_score,
                'metrics': metric_values
            }
            
            # Check if this is the current player
            if other_name == str(player_name).strip() and other_team == str(player_team).strip():
                player_row_data = row_data
            else:
                table_rows.append(row_data)
        
        # Calculate similarity scores if we have player data
        # Similarity is calculated using Euclidean distance across the 8 radar chart metrics
        # For each metric, we calculate: (player_value - other_player_value)²
        # Then sum all squared differences and take the square root
        # Lower distance = more similar player profile
        if player_row_data and player_row_data['metrics']:
            player_metrics = player_row_data['metrics']
            
            # First, normalize all metrics to 0-1 scale for fair comparison
            # (since different metrics have different scales, e.g., per-90 vs percentages)
            all_metric_values = [[] for _ in selected_metrics]
            for row_data in table_rows + [player_row_data]:
                if row_data['metrics']:
                    for i, val in enumerate(row_data['metrics']):
                        if val is not None:
                            all_metric_values[i].append(val)
            
            # Calculate min/max for each metric for normalization
            metric_ranges = []
            for metric_vals in all_metric_values:
                if metric_vals:
                    metric_min = min(metric_vals)
                    metric_max = max(metric_vals)
                    metric_range = metric_max - metric_min if metric_max > metric_min else 1
                    metric_ranges.append((metric_min, metric_max, metric_range))
                else:
                    metric_ranges.append((0, 1, 1))
            
            # Normalize player metrics
            player_metrics_normalized = []
            for i, val in enumerate(player_metrics):
                if val is not None and metric_ranges[i][2] > 0:
                    normalized = (val - metric_ranges[i][0]) / metric_ranges[i][2]
                    player_metrics_normalized.append(normalized)
                else:
                    player_metrics_normalized.append(None)
            
            # Calculate similarity for each other player using Euclidean distance on normalized metrics
            for row_data in table_rows:
                if row_data['metrics']:
                    # Normalize other player's metrics
                    other_metrics_normalized = []
                    for i, val in enumerate(row_data['metrics']):
                        if val is not None and metric_ranges[i][2] > 0:
                            normalized = (val - metric_ranges[i][0]) / metric_ranges[i][2]
                            other_metrics_normalized.append(normalized)
                        else:
                            other_metrics_normalized.append(None)
                    
                    # Calculate Euclidean distance (lower = more similar)
                    distances = []
                    for i, (player_norm, other_norm) in enumerate(zip(player_metrics_normalized, other_metrics_normalized)):
                        if player_norm is not None and other_norm is not None:
                            # Squared difference
                            distances.append((player_norm - other_norm) ** 2)
                    
                    if distances:
                        # Euclidean distance: sqrt(sum of squared differences)
                        similarity_score = sum(distances) ** 0.5
                        row_data['similarity'] = similarity_score
                    else:
                        row_data['similarity'] = float('inf')
                else:
                    row_data['similarity'] = float('inf')
            
            # Sort by similarity (most similar first)
            table_rows.sort(key=lambda x: x.get('similarity', float('inf')))
            
            # Keep only the 5 most similar players
            table_rows = table_rows[:5]
            
            # Add player row at the top
            table_rows.insert(0, player_row_data)
        else:
            # Fallback: sort by total score if similarity calculation fails
            table_rows.sort(key=lambda x: x['total_score'], reverse=True)
            if player_row_data:
                # Find insertion point
                insert_idx = 0
                for i, row in enumerate(table_rows):
                    if row['total_score'] < player_row_data['total_score']:
                        insert_idx = i
                        break
                    insert_idx = i + 1
                table_rows.insert(insert_idx, player_row_data)
                # Keep top 5 + player
                if len(table_rows) > 6:
                    # Keep player and top 5 by score
                    top_by_score = sorted([r for r in table_rows if r != player_row_data], 
                                        key=lambda x: x['total_score'], reverse=True)[:5]
                    table_rows = [player_row_data] + top_by_score
        
        # Build HTML table
        html = '<div style="margin-top: 0.3em; margin-bottom: 0.2em;">\n'
        html += '<h3 style="color: #8B0000; font-size: 9pt; font-weight: bold; margin-bottom: 0.1em;">'
        html += f'Comparison: {player_name} vs 5 Most Similar {position_profile}s</h3>\n'
        html += '<p style="font-size: 7pt; color: #666; margin: 0 0 0.2em 0;">Players selected based on similarity across all 8 metrics. Colors indicate percentile rank (red=top, blue=bottom).</p>\n'
        html += '<table style="width: 100%; border-collapse: collapse; font-size: 6.5pt; margin-top: 0.1em;">\n'
        
        # Header row
        html += '<thead><tr style="background-color: #f5f5f5; border-bottom: 2px solid #8B0000;">\n'
        html += '<th style="padding: 2px; text-align: left; font-weight: bold; font-size: 6.5pt;">Player</th>\n'
        html += '<th style="padding: 2px; text-align: left; font-weight: bold; font-size: 6.5pt;">Team</th>\n'
        def capitalize_words(text):
            """Capitalize first letter of every word."""
            return ' '.join(word.capitalize() for word in text.split())
        
        for metric in selected_metrics:
            # Shorten metric names for table and capitalize
            metric_short = metric.replace(' per 90', '/90').replace(' won, %', ' Won%').replace(', %', '%')
            metric_short = capitalize_words(metric_short)
            if len(metric_short) > 20:
                metric_short = metric_short[:17] + '...'
            html += f'<th style="padding: 2px; text-align: center; font-weight: bold; font-size: 6.5pt;">{metric_short}</th>\n'
        html += '</tr></thead>\n<tbody>\n'
        
        # Calculate percentiles for each metric across all position players
        # This will be used for color scaling
        metric_percentiles = []
        for i, metric in enumerate(selected_metrics):
            # Get all values for this metric from all position players
            all_values = []
            for idx, row in position_players.iterrows():
                # Find matching column
                metric_col = None
                metric_lower = metric.lower().strip()
                metric_normalized = metric_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                
                for col in row.index:
                    col_lower = str(col).lower().strip()
                    col_normalized = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                    if col_normalized == metric_normalized:
                        metric_col = col
                        break
                
                if not metric_col:
                    for col in row.index:
                        col_lower = str(col).lower().strip()
                        col_normalized = col_lower.replace(' per 90', '').replace(' per90', '').replace(',', '').replace('padj ', '').strip()
                        metric_words = set(metric_normalized.split())
                        col_words = set(col_normalized.split())
                        if metric_words and metric_words.issubset(col_words):
                            metric_col = col
                            break
                
                if metric_col and metric_col in row.index:
                    val = row.get(metric_col)
                    if pd.notna(val) and val != '':
                        try:
                            all_values.append(float(val))
                        except (ValueError, TypeError):
                            pass
            
            # Calculate percentiles
            if all_values:
                sorted_values = sorted(all_values)
                metric_percentiles.append(sorted_values)
            else:
                metric_percentiles.append([])
        
        def get_percentile_color(value, sorted_values):
            """Get color based on percentile using the same red-blue scale as beeswarm chart.
            A (80-100%) = Dark Red, B (60-80%) = Red, C (40-60%) = Light Red, D (20-40%) = Light Blue, F (0-20%) = Dark Blue
            """
            if not sorted_values or value is None:
                return '#ffffff'  # White for missing data
            
            try:
                value = float(value)
                # Calculate percentile
                percentile = (sum(1 for v in sorted_values if v <= value) / len(sorted_values)) * 100
                
                # Use same color scale as beeswarm chart (grade-based)
                # A (80-100%) = Dark Red, B (60-80%) = Red, C (40-60%) = Light Red, D (20-40%) = Light Blue, F (0-20%) = Dark Blue
                if percentile >= 80:
                    return '#8B0000'  # Dark red (A grade - top 20%)
                elif percentile >= 60:
                    return '#C5504B'  # Red (B grade - 60-80%)
                elif percentile >= 40:
                    return '#F2A2A2'  # Light red (C grade - 40-60%)
                elif percentile >= 20:
                    return '#8FAADC'  # Light blue (D grade - 20-40%)
                else:
                    return '#1F4E79'  # Dark blue (F grade - bottom 20%)
            except (ValueError, TypeError):
                return '#ffffff'
        
        # Data rows
        for row_data in table_rows:
            is_player = (row_data['player'] == str(player_name).strip() and 
                        row_data['team'] == str(player_team).strip())
            
            # No background color for player row, just bold the name
            html += f'<tr style="border-bottom: 1px solid #ddd;">\n'
            
            # Bold player name and team if it's the player's row
            html += f'<td style="padding: 2px; text-align: left; font-weight: {"bold" if is_player else "normal"}; font-size: 6.5pt;">{row_data["player"]}</td>\n'
            html += f'<td style="padding: 2px; text-align: left; font-weight: {"bold" if is_player else "normal"}; font-size: 6.5pt;">{row_data["team"]}</td>\n'
            
            for i, val in enumerate(row_data['metrics']):
                if val is not None:
                    # Check if this metric is a percentage based on metric name
                    metric = selected_metrics[i]
                    is_percentage = '%' in metric or 'won' in metric.lower() or 'accurate' in metric.lower() or 'successful' in metric.lower()
                    
                    # Get color based on percentile
                    bg_color = get_percentile_color(val, metric_percentiles[i])
                    
                    # White text for all metric values to stand out against colored backgrounds
                    if isinstance(val, float):
                        if is_percentage:
                            html += f'<td style="padding: 2px; text-align: center; background-color: {bg_color}; color: white; font-weight: {"bold" if is_player else "normal"}; font-size: 6.5pt;">{val:.1f}%</td>\n'
                        else:
                            html += f'<td style="padding: 2px; text-align: center; background-color: {bg_color}; color: white; font-weight: {"bold" if is_player else "normal"}; font-size: 6.5pt;">{val:.2f}</td>\n'
                    else:
                        html += f'<td style="padding: 2px; text-align: center; background-color: {bg_color}; color: white; font-weight: {"bold" if is_player else "normal"}; font-size: 6.5pt;">{val}</td>\n'
                else:
                    html += f'<td style="padding: 2px; text-align: center; background-color: #ffffff; font-weight: {"bold" if is_player else "normal"}; font-size: 6.5pt;">-</td>\n'
            
            html += '</tr>\n'
        
        html += '</tbody></table></div>\n'
        
        return html
        
    except Exception as e:
        print(f"  ⚠️  Error generating comparison table: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_all_charts(player_row, position_profile, position_config, thorns_ranks, 
                       full_position_configs, strengths, all_players_df=None, shortlist_df=None):
    """
    Generate all charts for a player overview.
    
    Args:
        shortlist_df: DataFrame from shortlist file (has percentage columns)
    
    Returns:
        Dictionary with chart names as keys and BytesIO objects as values
    """
    charts = {}
    
    # Generate radar charts (combined)
    # Pass shortlist_df for percentage metric averages
    radar_charts = generate_performance_radar_charts(player_row, position_config, all_players_df, position_profile, shortlist_df)
    if radar_charts:
        if 'combined' in radar_charts:
            charts['radar_combined'] = radar_charts['combined']
    
    # Generate scatterplots (pass shortlist_df for all players)
    scatterplots = generate_scatterplots(player_row, position_profile, all_players_df, shortlist_df)
    if scatterplots:
        charts.update(scatterplots)
    
    # Generate total score beeswarm chart
    beeswarm = generate_total_score_beeswarm(player_row, position_profile, shortlist_df, all_players_df)
    if beeswarm:
        charts['total_score_beeswarm'] = beeswarm
    
    # Generate comparison table
    comparison_table = generate_comparison_table(player_row, position_profile, shortlist_df, all_players_df)
    if comparison_table:
        charts['comparison_table'] = comparison_table
    
    consistency = generate_consistency_chart(player_row)
    if consistency:
        charts['consistency'] = consistency
    
    top_metrics = generate_top_metrics_chart(strengths, all_players_df)
    if top_metrics:
        charts['top_metrics'] = top_metrics
    
    style_fit = generate_style_fit_chart(player_row, thorns_ranks, position_profile, full_position_configs)
    if style_fit:
        charts['style_fit'] = style_fit
    
    return charts

