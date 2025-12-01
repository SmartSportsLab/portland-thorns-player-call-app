# Consistency Score Explanation

## Overview

The **Consistency Score** is a metric designed to identify well-rounded players who perform consistently across multiple metrics for their position, without major weaknesses. It measures how many of a player's position-specific metrics fall above, below, or at the position average.

## How It Works

### 1. Position-Specific Averages

For each position profile (e.g., Hybrid CB, DM Box-To-Box, AM Advanced Playmaker, Right Touchline Winger), we:

- Load **all Power Five players** at that position from the database
- Calculate the **average value** for each metric (e.g., "Defensive duels per 90", "Accurate passes, %")
- These averages serve as the baseline for comparison

### 2. Player Comparison

For each player in the shortlist, we compare their metric values against the position averages:

- **Metrics Above Avg**: Player's value is **more than 1% above** the position average
- **Metrics Below Avg**: Player's value is **more than 1% below** the position average  
- **Metrics At Avg**: Player's value is **within 1%** of the position average (tolerance zone)

### 3. Calculation Details

The calculation uses a **1% tolerance** to account for minor variations:

```python
tolerance = abs(avg_value) * 0.01  # 1% tolerance

if player_val > avg_value + tolerance:
    metrics_above += 1
elif player_val < avg_value - tolerance:
    metrics_below += 1
else:
    metrics_at += 1  # Within tolerance zone
```

### 4. Consistency Score Formula

The **Consistency Score** is calculated as:

```
Consistency Score = max(0, 100 - (metrics_below * (100 / total_metrics)))
```

**Interpretation:**
- **100 points** = All metrics are above or at average (0 below-average metrics)
- **Score decreases** by points for each below-average metric
- **Lower scores** indicate more below-average metrics (more weaknesses)

**Example:**
- Player with 14 metrics: 12 above, 1 below, 1 at average
- Consistency Score = 100 - (1 × (100/14)) = **92.9**

### 5. Consistency Percentage

The **Consistency %** shows what percentage of metrics are above average:

```
Consistency % = (metrics_above / total_metrics) × 100
```

**Example:**
- 12 metrics above out of 14 total = **85.7%**

## Output Columns

In the shortlist report, you'll see:

| Column | Description | Format |
|--------|-------------|--------|
| **Consistency Score** | Overall score (0-100) | Numeric (e.g., 92.9) |
| **Metrics Above Avg** | Count of above-average metrics | X/Y (e.g., 12/14) |
| **Metrics Below Avg** | Count of below-average metrics | X/Y (e.g., 1/14) |
| **Metrics At Avg** | Count of at-average metrics | X/Y (e.g., 1/14) |
| **Consistency %** | Percentage above average | Percentage (e.g., 85.7%) |

**Note:** The three metric counts (Above + Below + At) always sum to the total metrics checked.

## Why It Matters

The Consistency Score helps identify:

✅ **Well-rounded players** with few weaknesses  
✅ **Consistent performers** across multiple dimensions  
✅ **Players without major gaps** in their skill set  

**Use Cases:**
- Filter players with too many below-average metrics (e.g., >3 below average)
- Identify players who excel across the board (high Consistency Score)
- Compare players who have similar total scores but different consistency profiles

## Example

**Player A (Hybrid CB):**
- Metrics Above Avg: 12/14
- Metrics Below Avg: 1/14
- Metrics At Avg: 1/14
- Consistency Score: 92.9
- Consistency %: 85.7%

**Player B (Hybrid CB):**
- Metrics Above Avg: 9/14
- Metrics Below Avg: 5/14
- Metrics At Avg: 0/14
- Consistency Score: 64.3
- Consistency %: 64.3%

Player A is more consistent with fewer weaknesses, making them potentially more reliable despite similar total scores.

## Technical Notes

- Only metrics with valid numeric values are included in the calculation
- Combined metrics (e.g., "Interceptions + Sliding Tackles") are handled as single metrics
- The calculation uses **per 90 values** for consistency (not percentage-based metrics)
- Position averages are calculated from **all Power Five players** at that position, not just the shortlist

