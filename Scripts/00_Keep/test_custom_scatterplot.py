#!/usr/bin/env python3
"""
Test Custom Scatterplot: Defensive Duels Example
=================================================

Creates a scatterplot with:
- X-axis: Defensive duels per 90
- Y-axis: Defensive duels won, %
- Circle size: Total Minutes
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

# Grade colors for reference
GRADE_COLORS = {
    'A': '#8B0000',  # Dark red
    'B': '#C5504B',  # Medium red
    'C': '#F2A2A2',  # Light red
    'D': '#8FAADC',  # Light blue
    'F': '#1F4E79'   # Dark blue
}


def create_defensive_duels_scatterplot(excel_file, position='Hybrid CB', output_path=None):
    """
    Create scatterplot: Defensive duels per 90 vs Defensive duels won %.
    Circle size = Total Minutes.
    """
    print(f"\n{'='*80}")
    print(f"CREATING DEFENSIVE DUELS SCATTERPLOT")
    print(f"{'='*80}")
    print(f"Position: {position}")
    
    # Load data
    df = pd.read_excel(excel_file, sheet_name=position)
    print(f"Loaded {len(df)} players from {position}")
    
    # Prepare data
    df_plot = df.copy()
    
    # Required columns
    x_col = 'Defensive duels per 90'
    y_col = 'Defensive duels won, %'
    size_col = 'Total Minutes'
    grade_col = 'Conference Grade' if 'Conference Grade' in df_plot.columns else 'Power Five Grade'
    
    # Check columns exist
    missing_cols = []
    for col in [x_col, y_col, size_col]:
        if col not in df_plot.columns:
            missing_cols.append(col)
    
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        print(f"Available columns: {list(df_plot.columns)[:10]}...")
        return None
    
    # Convert to numeric
    df_plot[x_col] = pd.to_numeric(df_plot[x_col], errors='coerce')
    df_plot[y_col] = pd.to_numeric(df_plot[y_col], errors='coerce')
    df_plot[size_col] = pd.to_numeric(df_plot[size_col], errors='coerce')
    
    # Filter out invalid data
    df_plot = df_plot[
        (df_plot[x_col].notna()) & 
        (df_plot[y_col].notna()) & 
        (df_plot[size_col].notna()) &
        (df_plot[x_col] > 0) &
        (df_plot[y_col] > 0) &
        (df_plot[size_col] > 0)
    ].copy()
    
    print(f"Valid data points: {len(df_plot)}")
    
    if len(df_plot) == 0:
        print("❌ No valid data points")
        return None
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Normalize circle size (min 50, max 500 pixels)
    min_minutes = df_plot[size_col].min()
    max_minutes = df_plot[size_col].max()
    if max_minutes > min_minutes:
        df_plot['Circle_Size'] = 50 + (df_plot[size_col] - min_minutes) / (max_minutes - min_minutes) * 450
    else:
        df_plot['Circle_Size'] = 200
    
    # Color by grade if available
    if grade_col in df_plot.columns:
        df_plot['Color'] = df_plot[grade_col].map(GRADE_COLORS).fillna('#808080')
        
        # Plot by grade
        for grade in ['A', 'B', 'C', 'D', 'F']:
            if grade not in df_plot[grade_col].values:
                continue
            
            grade_data = df_plot[df_plot[grade_col] == grade]
            if len(grade_data) == 0:
                continue
            
            ax.scatter(
                grade_data[x_col],
                grade_data[y_col],
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
            df_plot[x_col],
            df_plot[y_col],
            s=df_plot['Circle_Size'],
            c='steelblue',
            alpha=0.6,
            edgecolors='black',
            linewidths=1.5,
            zorder=3
        )
    
    # Add player names for top performers
    # Show players with high minutes OR high defensive duels
    top_players = df_plot.nlargest(10, size_col)  # Top 10 by minutes
    high_duels = df_plot.nlargest(5, x_col)  # Top 5 by duels per 90
    
    for _, player in pd.concat([top_players, high_duels]).drop_duplicates().iterrows():
        player_name = str(player.get('Player', ''))[:20]
        player_minutes = int(player[size_col])
        player_grade = player.get(grade_col, '') if grade_col in player.index else ''
        
        label = f"{player_name}\n({player_minutes} min"
        if player_grade:
            label += f", {player_grade}"
        label += ")"
        
        ax.annotate(
            player_name,
            (player[x_col], player[y_col]),
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
    ax.set_xlabel('Defensive Duels per 90', fontsize=14, fontweight='bold')
    ax.set_ylabel('Defensive Duels Won %', fontsize=14, fontweight='bold')
    ax.set_title(
        f'{position} - Defensive Duels Analysis\n(Circle size = Total Minutes played)', 
        fontsize=16, 
        fontweight='bold', 
        pad=20
    )
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add quadrant lines at median
    median_x = df_plot[x_col].median()
    median_y = df_plot[y_col].median()
    
    ax.axhline(y=median_y, color='gray', linestyle='--', alpha=0.5, linewidth=1, label=f'Median Win %: {median_y:.1f}%')
    ax.axvline(x=median_x, color='gray', linestyle='--', alpha=0.5, linewidth=1, label=f'Median per 90: {median_x:.1f}')
    
    # Add quadrant labels
    max_x = df_plot[x_col].max()
    max_y = df_plot[y_col].max()
    
    ax.text(max_x * 0.75, max_y * 0.95, 'High Volume\nHigh Win Rate', 
            fontsize=11, alpha=0.6, 
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.4),
            ha='center', va='top')
    ax.text(max_x * 0.25, max_y * 0.95, 'Low Volume\nHigh Win Rate', 
            fontsize=11, alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.4),
            ha='center', va='top')
    ax.text(max_x * 0.75, max_y * 0.25, 'High Volume\nLow Win Rate', 
            fontsize=11, alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.4),
            ha='center', va='bottom')
    ax.text(max_x * 0.25, max_y * 0.25, 'Low Volume\nLow Win Rate', 
            fontsize=11, alpha=0.6,
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.4),
            ha='center', va='bottom')
    
    # Legend
    if grade_col in df_plot.columns:
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
    
    # Add minutes legend (size reference)
    import matplotlib.patches as mpatches
    minutes_legend_elements = [
        mpatches.Circle((0, 0), radius=50, facecolor='gray', alpha=0.6, 
                       label=f'Min: {int(min_minutes)} min'),
        mpatches.Circle((0, 0), radius=250, facecolor='gray', alpha=0.6,
                       label=f'Max: {int(max_minutes)} min')
    ]
    if grade_col not in df_plot.columns or not handles:
        minutes_legend = ax.legend(handles=minutes_legend_elements, loc='lower right',
                                  title='Circle Size = Minutes', title_fontsize=9, framealpha=0.9)
    
    # Add statistics text box
    stats_text = f"""Statistics:
Players: {len(df_plot)}
Avg Duels/90: {df_plot[x_col].mean():.2f}
Avg Win %: {df_plot[y_col].mean():.1f}%
Avg Minutes: {df_plot[size_col].mean():.0f}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            family='monospace')
    
    plt.tight_layout()
    
    # Save
    if output_path is None:
        output_path = Path(excel_file).parent / "Scatterplots" / f"{position.replace(' ', '_')}_defensive_duels.png"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path}")
    plt.close()
    
    return output_path


def main():
    """Main function."""
    import sys
    
    base_dir = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search")
    excel_file = base_dir / "Mike_Norris_Scouting_Report_ACC_IntraConference.xlsx"
    
    if not excel_file.exists():
        print(f"❌ File not found: {excel_file}")
        return
    
    # Test with Hybrid CB position
    position = 'Hybrid CB'
    
    print(f"\nTesting scatterplot creation...")
    print(f"Excel file: {excel_file.name}")
    print(f"Position: {position}")
    
    output_path = create_defensive_duels_scatterplot(excel_file, position=position)
    
    if output_path:
        print(f"\n✅ Success! Scatterplot created at: {output_path}")
        print(f"\nTo view: open {output_path}")
    else:
        print(f"\n❌ Failed to create scatterplot")


if __name__ == "__main__":
    main()

