#!/usr/bin/env python3
"""
Create Custom Metric Scatterplot
=================================

Flexible script to create scatterplots with any two metrics.
Usage: python create_custom_scatterplot.py [CONFERENCE] [POSITION] [X_METRIC] [Y_METRIC] [SIZE_COL]

Example:
    python create_custom_scatterplot.py ACC "Hybrid CB" "Defensive duels per 90" "Defensive duels won, %" "Total Minutes"
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import numpy as np
import matplotlib.patches as mpatches

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

# Grade colors
GRADE_COLORS = {
    'A': '#8B0000', 'A+': '#8B0000',
    'B': '#C5504B',
    'C': '#F2A2A2',
    'D': '#8FAADC',
    'F': '#1F4E79'
}


def create_custom_scatterplot(excel_file, position, x_metric, y_metric, size_col='Total Minutes',
                              grade_col='Conference Grade', output_path=None):
    """
    Create custom scatterplot with any two metrics.
    
    Args:
        excel_file: Path to Excel file
        position: Sheet name (position profile or team)
        x_metric: Column name for X-axis
        y_metric: Column name for Y-axis
        size_col: Column name for circle size (default: 'Total Minutes')
        grade_col: Column name for coloring (default: 'Conference Grade')
        output_path: Output path (auto-generated if None)
    """
    print(f"\n{'='*80}")
    print(f"CREATING CUSTOM SCATTERPLOT")
    print(f"{'='*80}")
    print(f"Position/Team: {position}")
    print(f"X-axis: {x_metric}")
    print(f"Y-axis: {y_metric}")
    print(f"Circle size: {size_col}")
    
    # Load data
    try:
        df = pd.read_excel(excel_file, sheet_name=position)
    except Exception as e:
        print(f"❌ Error loading sheet '{position}': {e}")
        return None
    
    print(f"Loaded {len(df)} players")
    
    # Prepare data
    df_plot = df.copy()
    
    # Check required columns
    required_cols = [x_metric, y_metric, size_col]
    missing_cols = [col for col in required_cols if col not in df_plot.columns]
    
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        print(f"\nAvailable columns:")
        for i, col in enumerate(df_plot.columns, 1):
            print(f"  {i}. {col}")
        return None
    
    # Convert to numeric
    for col in required_cols:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
    
    # Filter out invalid data
    df_plot = df_plot[
        (df_plot[x_metric].notna()) & 
        (df_plot[y_metric].notna()) & 
        (df_plot[size_col].notna()) &
        (df_plot[x_metric] > 0) &
        (df_plot[y_metric] > 0) &
        (df_plot[size_col] > 0)
    ].copy()
    
    print(f"Valid data points: {len(df_plot)}")
    
    if len(df_plot) == 0:
        print("❌ No valid data points")
        return None
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Normalize circle size (min 50, max 500 pixels)
    min_size = df_plot[size_col].min()
    max_size = df_plot[size_col].max()
    if max_size > min_size:
        df_plot['Circle_Size'] = 50 + (df_plot[size_col] - min_size) / (max_size - min_size) * 450
    else:
        df_plot['Circle_Size'] = 200
    
    # Color by grade if available
    has_grade = grade_col in df_plot.columns
    if has_grade:
        df_plot['Color'] = df_plot[grade_col].map(GRADE_COLORS).fillna('#808080')
        
        # Plot by grade
        for grade in ['A+', 'A', 'B', 'C', 'D', 'F']:
            if grade not in df_plot[grade_col].values:
                continue
            
            grade_data = df_plot[df_plot[grade_col] == grade]
            if len(grade_data) == 0:
                continue
            
            ax.scatter(
                grade_data[x_metric],
                grade_data[y_metric],
                s=grade_data['Circle_Size'],
                c=grade_data['Color'],
                alpha=0.6,
                edgecolors='black',
                linewidths=1.5,
                label=f'Grade {grade}',
                zorder=3
            )
    else:
        # No grade column, use single color
        ax.scatter(
            df_plot[x_metric],
            df_plot[y_metric],
            s=df_plot['Circle_Size'],
            c='steelblue',
            alpha=0.6,
            edgecolors='black',
            linewidths=1.5,
            zorder=3
        )
    
    # Add player names for top performers
    # Show players with high size OR high x_metric
    top_size = df_plot.nlargest(8, size_col)
    top_x = df_plot.nlargest(5, x_metric)
    
    for _, player in pd.concat([top_size, top_x]).drop_duplicates().iterrows():
        player_name = str(player.get('Player', ''))[:18]
        
        ax.annotate(
            player_name,
            (player[x_metric], player[y_metric]),
            fontsize=8,
            alpha=0.8,
            xytext=(8, 8),
            textcoords='offset points',
            bbox=dict(
                boxstyle='round,pad=0.4', 
                facecolor='white', 
                alpha=0.85, 
                edgecolor='gray', 
                linewidth=1
            ),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', alpha=0.5, color='gray')
        )
    
    # Labels and title
    ax.set_xlabel(x_metric, fontsize=14, fontweight='bold')
    ax.set_ylabel(y_metric, fontsize=14, fontweight='bold')
    ax.set_title(
        f'{position} - {x_metric} vs {y_metric}\n(Circle size = {size_col})', 
        fontsize=16, 
        fontweight='bold', 
        pad=20
    )
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add quadrant lines at median
    median_x = df_plot[x_metric].median()
    median_y = df_plot[y_metric].median()
    
    ax.axhline(y=median_y, color='gray', linestyle='--', alpha=0.5, linewidth=1, 
              label=f'Median {y_metric.split(",")[0]}: {median_y:.1f}')
    ax.axvline(x=median_x, color='gray', linestyle='--', alpha=0.5, linewidth=1, 
              label=f'Median {x_metric.split(" ")[0]}: {median_x:.1f}')
    
    # Add quadrant labels
    max_x = df_plot[x_metric].max()
    max_y = df_plot[y_metric].max()
    min_x = df_plot[x_metric].min()
    min_y = df_plot[y_metric].min()
    
    x_range = max_x - min_x
    y_range = max_y - min_y
    
    ax.text(min_x + x_range * 0.75, min_y + y_range * 0.95, 'High X\nHigh Y', 
            fontsize=11, alpha=0.6, 
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.4),
            ha='center', va='top')
    ax.text(min_x + x_range * 0.25, min_y + y_range * 0.95, 'Low X\nHigh Y', 
            fontsize=11, alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.4),
            ha='center', va='top')
    ax.text(min_x + x_range * 0.75, min_y + y_range * 0.25, 'High X\nLow Y', 
            fontsize=11, alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.4),
            ha='center', va='bottom')
    ax.text(min_x + x_range * 0.25, min_y + y_range * 0.25, 'Low X\nLow Y', 
            fontsize=11, alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.4),
            ha='center', va='bottom')
    
    # Legend
    if has_grade:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            # Separate grade legend from median lines
            grade_handles = [h for h, l in zip(handles, labels) if not l.startswith('Median')]
            grade_labels = [l for l in labels if not l.startswith('Median')]
            median_handles = [h for h, l in zip(handles, labels) if l.startswith('Median')]
            median_labels = [l for l in labels if l.startswith('Median')]
            
            if grade_handles:
                legend1 = ax.legend(grade_handles, grade_labels, loc='upper left', 
                                   framealpha=0.9, title='Grades', title_fontsize=10)
                legend1.get_frame().set_facecolor('white')
                ax.add_artist(legend1)
            
            if median_handles:
                ax.legend(median_handles, median_labels, loc='lower right', 
                         framealpha=0.9, fontsize=9)
    
    # Add size legend
    size_legend_elements = [
        mpatches.Circle((0, 0), radius=50, facecolor='gray', alpha=0.6, 
                       label=f'Min: {int(min_size)}'),
        mpatches.Circle((0, 0), radius=250, facecolor='gray', alpha=0.6,
                       label=f'Max: {int(max_size)}')
    ]
    if not has_grade or not handles:
        ax.legend(handles=size_legend_elements, loc='lower right',
                 title=f'Circle Size = {size_col}', title_fontsize=9, framealpha=0.9)
    
    # Add statistics text box
    stats_text = f"""Statistics:
Players: {len(df_plot)}
Avg {x_metric.split()[0]}: {df_plot[x_metric].mean():.2f}
Avg {y_metric.split()[0]}: {df_plot[y_metric].mean():.1f}
Avg {size_col.split()[0]}: {df_plot[size_col].mean():.0f}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            family='monospace')
    
    plt.tight_layout()
    
    # Save
    if output_path is None:
        safe_name = position.replace(' ', '_').replace('.', '')
        safe_x = x_metric.replace(' ', '_').replace(',', '').replace('%', '')[:20]
        safe_y = y_metric.replace(' ', '_').replace(',', '').replace('%', '')[:20]
        output_path = Path(excel_file).parent / "Scatterplots" / f"{safe_name}_{safe_x}_vs_{safe_y}.png"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path}")
    plt.close()
    
    return output_path


def main():
    """Main function."""
    if len(sys.argv) < 5:
        print("Usage: python create_custom_scatterplot.py [CONFERENCE] [POSITION] [X_METRIC] [Y_METRIC] [SIZE_COL]")
        print("\nExample:")
        print('  python create_custom_scatterplot.py ACC "Hybrid CB" "Defensive duels per 90" "Defensive duels won, %" "Total Minutes"')
        print("\nAvailable positions:")
        print("  - Hybrid CB")
        print("  - DM Box-To-Box")
        print("  - AM Advanced Playmaker")
        print("  - Right Touchline Winger")
        print("  - Team names (e.g., 'Duke Blue Devils')")
        sys.exit(1)
    
    conference = sys.argv[1].upper()
    position = sys.argv[2]
    x_metric = sys.argv[3]
    y_metric = sys.argv[4]
    size_col = sys.argv[5] if len(sys.argv) > 5 else 'Total Minutes'
    
    base_dir = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search")
    excel_file = base_dir / f"Mike_Norris_Scouting_Report_{conference}_IntraConference.xlsx"
    
    if not excel_file.exists():
        print(f"❌ File not found: {excel_file}")
        sys.exit(1)
    
    output_path = create_custom_scatterplot(
        excel_file, 
        position=position,
        x_metric=x_metric,
        y_metric=y_metric,
        size_col=size_col
    )
    
    if output_path:
        print(f"\n✅ Success! Scatterplot created at: {output_path}")
    else:
        print(f"\n❌ Failed to create scatterplot")


if __name__ == "__main__":
    main()

