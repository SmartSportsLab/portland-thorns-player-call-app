# Scatterplot Visualization Guide

## Overview

Scatterplot visualizations provide an intuitive way to identify players for semi-finals scouting by showing:
- **X-axis**: Total Score (1-10 scale) - Performance quality
- **Y-axis**: Grade Value (A=5, B=4, C=3, D=2, F=1) - Performance ranking
- **Circle Size**: Minutes played - Reliability/sample size
- **Color**: Grade (A=dark red, B=medium red, C=light red, D=light blue, F=dark blue)

## Why Scatterplots?

✅ **Visual identification** - Instantly spot players in the "High Score + High Grade + Large Circle" quadrant  
✅ **Minutes context** - Large circles = reliable, small circles = limited sample  
✅ **Team comparison** - See all players from a team at once  
✅ **Position comparison** - Compare players across positions within a team  

## Quick Start

### Generate All Scatterplots

```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"
python create_scatterplot_visualizations.py ACC Conference_Grade
```

This creates:
- **Position profile scatterplots**: One for each position (Hybrid CB, DM Box-To-Box, etc.)
- **Team scatterplots**: One for each team (Duke, Notre Dame, etc.)
- **PNG images**: Saved in `Scatterplots/` folder

### Generate and Embed in Excel

```bash
python create_scatterplot_visualizations.py ACC Conference_Grade yes
```

This creates the images AND embeds them directly into the Excel sheets.

## Understanding the Plot

### Quadrants

- **Top Right (High Score + High Grade)**: Best performers - ideal targets
- **Top Left (Low Score + High Grade)**: Grade may be inflated, check minutes
- **Bottom Right (High Score + Low Grade)**: Strong performance but ranked lower - potential hidden gems
- **Bottom Left (Low Score + Low Grade)**: Weaker players

### Circle Size

- **Large circles** (750+ minutes): High reliability, proven over many games
- **Medium circles** (400-749 minutes): Good sample size
- **Small circles** (<400 minutes): Limited sample, use caution

### Ideal Player Profile for Semi-Finals

Look for players in the **top-right quadrant with large circles**:
- High Total Score (7.5+)
- High Grade (A or B)
- Large circle (750+ minutes)

These are players who:
1. ✅ Perform well (high score)
2. ✅ Rank highly (high grade)
3. ✅ Are reliable (high minutes)

## Example Output

### Position Profile Plot (e.g., "Hybrid CB")
- Shows all center backs from all teams
- Color-coded by grade
- Circle size = minutes
- Player names labeled for top performers

### Team Plot (e.g., "Duke Blue Devils")
- Shows all players from that team
- Color-coded by position profile
- Circle size = minutes
- Easy to see team depth and top performers

## Command Options

```bash
python create_scatterplot_visualizations.py [CONFERENCE] [GRADE_COL] [EMBED]
```

**Arguments:**
- `CONFERENCE`: `ACC` or `SEC`
- `GRADE_COL`: `Conference_Grade` (default) or `Power_Five_Grade`
- `EMBED`: `yes` to embed in Excel (optional)

**Examples:**

```bash
# ACC with Conference Grade
python create_scatterplot_visualizations.py ACC

# SEC with Power Five Grade
python create_scatterplot_visualizations.py SEC Power_Five_Grade

# ACC with Conference Grade, embedded in Excel
python create_scatterplot_visualizations.py ACC Conference_Grade yes
```

## Output Files

All images are saved in:
```
Data/Advanced Search/Scatterplots/
```

Files named:
- `Hybrid_CB_scatterplot.png`
- `DM_Box-To-Box_scatterplot.png`
- `AM_Advanced_Playmaker_scatterplot.png`
- `Right_Touchline_Winger_scatterplot.png`
- `Duke_Blue_Devils_scatterplot.png`
- `Notre_Dame_Fighting_Irish_scatterplot.png`
- etc.

## Integration with Report Generation

You can add this to `update_mike_norris_reports.py` after the report is created:

```python
# After saving the workbook (around line 800)
from create_scatterplot_visualizations import create_all_scatterplots

print("\n📊 Creating scatterplot visualizations...")
create_all_scatterplots(output_file, grade_col='Conference_Grade')
```

## Customization

### Adjust Circle Size Range

In `create_scatterplot_per_position()`, modify:
```python
# Current: 50-500 pixel range
df_plot['Circle_Size'] = 50 + (df_plot['Minutes'] - min_minutes) / (max_minutes - min_minutes) * 450

# Make larger: 100-800 pixel range
df_plot['Circle_Size'] = 100 + (df_plot['Minutes'] - min_minutes) / (max_minutes - min_minutes) * 700
```

### Change Labels Shown

Modify the player name annotation logic:
```python
# Current: Top 10 by score OR minutes > 700
top_players = df_plot.nlargest(10, 'Score')
high_minutes_players = df_plot[df_plot['Minutes'] >= 700]

# Show top 15 by score
top_players = df_plot.nlargest(15, 'Score')
```

### Change Colors

Modify `GRADE_COLORS` dictionary:
```python
GRADE_COLORS = {
    'A': '#FF0000',  # Bright red
    'B': '#FF8800',  # Orange
    # etc.
}
```

## Tips for Semi-Finals Scouting

1. **Start with position plots** - See who stands out in each position
2. **Check team plots** - Understand team depth and top performers
3. **Look for large circles** - Prioritize players with 750+ minutes
4. **Top-right quadrant** - Focus on players with high score AND high grade
5. **Cross-reference** - Compare Conference Grade vs Power Five Grade plots

## Next Steps

After generating scatterplots:
1. Review position profile plots to identify top performers
2. Review team plots to understand team composition
3. Focus on players with large circles (high minutes) in top-right quadrant
4. Cross-reference with Excel data for detailed metrics

