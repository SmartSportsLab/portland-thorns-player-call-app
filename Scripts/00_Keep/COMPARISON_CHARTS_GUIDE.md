# Adding Comparison Charts to Player Overview PDFs (Page 2)

## Overview

This guide explains how to add comparison charts as a second page to the player overview PDFs.

## Required Libraries

```bash
pip install matplotlib pandas numpy
```

## Chart Types to Implement

### 1. Radar Chart - Position-Specific Metrics

**Purpose**: Compare player against position average and top 15 average

**Data Needed**:
- Player's position-specific metrics (from `position_metrics_config.json`)
- Position average (from all Power Five players)
- Top 15 average (from top 15 players in position)
- Portland Thorns style fit benchmarks (optional)

**Implementation**:
```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import matplotlib.patches as mpatches

def create_radar_chart(player_metrics, position_avg, top15_avg, position_config):
    """
    Create radar chart comparing player to averages.
    
    Args:
        player_metrics: dict of metric_name -> value
        position_avg: dict of metric_name -> average value
        top15_avg: dict of metric_name -> top 15 average
        position_config: position config from JSON
    
    Returns:
        Path to saved chart image
    """
    # Get position-specific metrics
    metrics = []
    for category in ['Core', 'Specific']:
        if category in position_config.get('metrics', {}):
            for metric_name in position_config['metrics'][category].keys():
                metrics.append(metric_name)
    
    # Limit to 6-8 key metrics for readability
    metrics = metrics[:8]
    
    # Normalize values (0-100 scale)
    player_values = []
    avg_values = []
    top15_values = []
    
    for metric in metrics:
        # Extract base metric name and get per-90 value
        player_val = normalize_metric(player_metrics, metric)
        avg_val = normalize_metric(position_avg, metric)
        top15_val = normalize_metric(top15_avg, metric)
        
        player_values.append(player_val)
        avg_values.append(avg_val)
        top15_values.append(top15_val)
    
    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    player_values += player_values[:1]  # Close the loop
    avg_values += avg_values[:1]
    top15_values += top15_values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    ax.plot(angles, player_values, 'o-', linewidth=2, label='Player', color='#FF0000')
    ax.fill(angles, player_values, alpha=0.25, color='#FF0000')
    
    ax.plot(angles, avg_values, 'o-', linewidth=2, label='Position Avg', color='#666666')
    ax.plot(angles, top15_values, 'o-', linewidth=2, label='Top 15 Avg', color='#000000')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m[:20] for m in metrics], fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    plt.title('Position-Specific Metrics Comparison', size=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save
    chart_path = Path('temp_radar_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return chart_path
```

### 2. Percentile Distribution Chart

**Purpose**: Show player's percentile rankings for key metrics

**Implementation**:
```python
def create_percentile_chart(player_row, all_players_df, position_profile):
    """
    Create bar chart showing percentile rankings.
    """
    metrics_to_show = ['Total Score', 'Consistency Score', 'Style Fits', 'Top 15s']
    
    percentiles = []
    labels = []
    
    for metric in metrics_to_show:
        if metric in player_row.index and metric in all_players_df.columns:
            player_val = player_row[metric]
            position_players = all_players_df[all_players_df['Position Profile'] == position_profile]
            
            if len(position_players) > 0:
                percentile = (position_players[metric] <= player_val).sum() / len(position_players) * 100
                percentiles.append(percentile)
                labels.append(metric)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#FF0000' if p >= 75 else '#FF6666' if p >= 50 else '#FF9999' for p in percentiles]
    bars = ax.barh(labels, percentiles, color=colors)
    
    ax.set_xlim(0, 100)
    ax.set_xlabel('Percentile', fontsize=10)
    ax.set_title('Performance Percentiles', fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, p) in enumerate(zip(bars, percentiles)):
        ax.text(p + 2, i, f'{p:.0f}th', va='center', fontsize=9)
    
    plt.tight_layout()
    chart_path = Path('temp_percentile_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return chart_path
```

### 3. Strengths vs. Weaknesses Heatmap

**Purpose**: Visual representation of strengths and weaknesses

**Implementation**:
```python
def create_strengths_weaknesses_chart(strengths, weaknesses, metrics_above, metrics_below, total_metrics):
    """
    Create heatmap-style visualization of strengths and weaknesses.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Strengths (left)
    strength_names = [s['metric'] for s in strengths[:4]]
    strength_values = [s['percentile'] for s in strengths[:4]]
    colors_strength = plt.cm.Greens(np.linspace(0.4, 0.9, len(strength_names)))
    
    ax1.barh(strength_names, strength_values, color=colors_strength)
    ax1.set_xlim(0, 100)
    ax1.set_title('Top Strengths', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Percentile', fontsize=10)
    ax1.grid(axis='x', alpha=0.3)
    
    # Weaknesses (right)
    weakness_names = [w['metric'] for w in weaknesses[:3]]
    weakness_values = [w['percentile'] for w in weaknesses[:3]]
    colors_weakness = plt.cm.Reds(np.linspace(0.4, 0.9, len(weakness_names)))
    
    ax2.barh(weakness_names, weakness_values, color=colors_weakness)
    ax2.set_xlim(0, 100)
    ax2.set_title('Top Weaknesses', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Percentile', fontsize=10)
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    chart_path = Path('temp_strengths_weaknesses_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return chart_path
```

### 4. Consistency Breakdown Chart

**Purpose**: Visual breakdown of metrics above/at/below average

**Implementation**:
```python
def create_consistency_chart(metrics_above, metrics_at, metrics_below, total_metrics):
    """
    Create stacked bar chart showing consistency breakdown.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    categories = ['Metrics Breakdown']
    above = [metrics_above]
    at = [metrics_at]
    below = [metrics_below]
    
    ax.bar(categories, above, label=f'Above Avg ({metrics_above}/{total_metrics})', color='#00AA00')
    ax.bar(categories, at, bottom=above, label=f'At Avg ({metrics_at}/{total_metrics})', color='#FFAA00')
    ax.bar(categories, below, bottom=[a + b for a, b in zip(above, at)], 
           label=f'Below Avg ({metrics_below}/{total_metrics})', color='#AA0000')
    
    ax.set_ylim(0, total_metrics)
    ax.set_ylabel('Number of Metrics', fontsize=10)
    ax.set_title('Consistency Breakdown', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    chart_path = Path('temp_consistency_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return chart_path
```

### 5. Progression Trend Chart (if available)

**Purpose**: Show player development over seasons

**Implementation**:
```python
def create_progression_chart(player_seasons_data):
    """
    Create line chart showing progression over seasons.
    """
    if not player_seasons_data or len(player_seasons_data) < 2:
        return None
    
    seasons = sorted(player_seasons_data.keys())
    scores = [player_seasons_data[s].get('Total Score', 0) for s in seasons]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(seasons, scores, marker='o', linewidth=2, markersize=8, color='#FF0000')
    ax.fill_between(seasons, scores, alpha=0.3, color='#FF0000')
    
    ax.set_xlabel('Season', fontsize=10)
    ax.set_ylabel('Total Score', fontsize=10)
    ax.set_title('Performance Progression', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    chart_path = Path('temp_progression_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return chart_path
```

## Integration into PDF Generation

Add to `generate_player_overviews.py`:

```python
def generate_comparison_charts_page(player_row, position_profile, all_players_df, position_config, thorns_ranks):
    """
    Generate all comparison charts and return HTML for page 2.
    """
    charts = []
    
    # 1. Radar chart
    try:
        radar_chart = create_radar_chart(...)
        charts.append(('radar', radar_chart))
    except Exception as e:
        print(f"  ⚠️  Error creating radar chart: {e}")
    
    # 2. Percentile chart
    try:
        percentile_chart = create_percentile_chart(player_row, all_players_df, position_profile)
        charts.append(('percentile', percentile_chart))
    except Exception as e:
        print(f"  ⚠️  Error creating percentile chart: {e}")
    
    # 3. Strengths/Weaknesses chart
    try:
        strengths_weaknesses_chart = create_strengths_weaknesses_chart(...)
        charts.append(('strengths_weaknesses', strengths_weaknesses_chart))
    except Exception as e:
        print(f"  ⚠️  Error creating strengths/weaknesses chart: {e}")
    
    # 4. Consistency chart
    try:
        consistency_chart = create_consistency_chart(...)
        charts.append(('consistency', consistency_chart))
    except Exception as e:
        print(f"  ⚠️  Error creating consistency chart: {e}")
    
    # 5. Progression chart (if available)
    try:
        progression_chart = create_progression_chart(...)
        if progression_chart:
            charts.append(('progression', progression_chart))
    except Exception as e:
        print(f"  ⚠️  Error creating progression chart: {e}")
    
    # Generate HTML for page 2
    html_lines = ['<div class="page-break"></div>']  # Force new page
    html_lines.append('<h2>Performance Comparison Charts</h2>')
    
    # Add charts in grid layout
    html_lines.append('<div class="charts-grid">')
    for chart_type, chart_path in charts:
        html_lines.append(f'<div class="chart-container">')
        html_lines.append(f'<img src="{chart_path}" alt="{chart_type}" class="chart-image">')
        html_lines.append('</div>')
    html_lines.append('</div>')
    
    return '\n'.join(html_lines)
```

## CSS for Charts

Add to CSS:

```css
.charts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin: 20px 0;
}

.chart-container {
    text-align: center;
}

.chart-image {
    max-width: 100%;
    height: auto;
    page-break-inside: avoid;
}

.page-break {
    page-break-before: always;
}
```

## Next Steps

1. Implement chart generation functions
2. Integrate into `generate_pdf_overview` function
3. Test with sample players
4. Adjust sizing and layout as needed
5. Clean up temporary chart files after PDF generation

