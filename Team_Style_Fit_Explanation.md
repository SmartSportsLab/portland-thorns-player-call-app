# Team Style Fit Score Explanation

## Overview

The **Team Style Fit Score** (also called "Style Fits") identifies NCAA players whose playing strengths align with Portland Thorns' playing style. It measures how many position-specific metrics a player excels in that match Portland's top-ranked metrics in the NWSL.

## How It Works

### Step 1: Identify Portland's Playing Style

We analyze Portland Thorns' performance across all NWSL teams (14 teams total) to identify their **core strengths**:

- Calculate Portland's rank for each metric among all 14 NWSL teams
- Identify metrics where Portland ranks **top 3** in the league
- These metrics represent Portland's **playing style** (what they do best)

**Example:**
- Portland ranks **#2/14** in "Interceptions" → Core strength
- Portland ranks **#3/14** in "Long Passes" → Core strength
- Portland ranks **#8/14** in "Shots" → Not a core strength (doesn't count)

### Step 2: Define Position-Specific Metrics

For each position profile, we use a curated list of metrics from `position_metrics_config.json`:

- **Hybrid CB**: Interceptions, Passes, Progressive passes, Long passes, Defensive duels, Aerial duels
- **DM Box-To-Box**: Interceptions, Progressive passes, Defensive duels, Passes, Received passes, Dribbles
- **AM Advanced Playmaker**: Goals, Assists, Smart passes, Through passes, Deep completions, Dribbles, Offensive duels
- **Right Touchline Winger**: Assists, Crosses, Dribbles, Offensive duels, Progressive runs, Received long passes

These are the metrics we check for style fit (not all available metrics).

### Step 3: Calculate Player Ranks

For each NCAA player, we calculate their rank within their position across **all Power Five conferences**:

- Load all Power Five players at that position (e.g., 240 Hybrid CBs, 370 DM Box-To-Box players)
- Rank each player for each metric (based on per 90 values)
- Calculate **top 20% threshold** (matches Portland's ~21% threshold: top 3/14 teams)

**Example Thresholds:**
- Hybrid CB: Rank #48 or better (out of 240) = top 20%
- DM Box-To-Box: Rank #74 or better (out of 370) = top 20%
- AM Advanced Playmaker: Rank #69 or better (out of 345) = top 20%
- Right Touchline Winger: Rank #73 or better (out of 366) = top 20%

### Step 4: Match Player Strengths to Portland's Style

A **Style Fit** is counted when **both conditions** are met:

1. ✅ Portland ranks **top 3** in NWSL for that metric
2. ✅ Player ranks **top 20%** in Power Five for that same metric

**Example:**
- Portland ranks #3/14 in "Long Passes" ✅
- C. Roller ranks #6/240 in "Long Passes" (top 20%) ✅
- **Result**: 1 Style Fit for C. Roller

### Step 5: Count Total Style Fits

The **Style Fits** column shows the total count of matching metrics:

- **0 Style Fits**: Player's strengths don't align with Portland's style
- **1-2 Style Fits**: Some alignment, but limited
- **3+ Style Fits**: Strong alignment with Portland's playing style

## Example: C. Roller (Duke Blue Devils)

**Portland's Top 3 Metrics (NWSL):**
- #3/14: Long Passes ✅
- #3/14: Total Passes ✅
- #3/14: Progressive Passes ✅

**C. Roller's Ranks (Hybrid CB, Power Five):**
- #6/240: Long Passes (top 20%) ✅ → **Style Fit #1**
- #8/240: Total Passes (top 20%) ✅ → **Style Fit #2**
- #8/240: Progressive Passes (top 20%) ✅ → **Style Fit #3**

**Result: 3 Style Fits** → Strong alignment with Portland's ball-playing, possession-oriented style

## Why Top 20%?

The **top 20% threshold** matches Portland's standard:
- Portland ranks **top 3 out of 14 NWSL teams** = ~21%
- NCAA players must rank **top 20%** in Power Five to match this standard
- This ensures we're comparing elite NCAA performance to elite NWSL performance

## Key Differences from Other Metrics

| Metric | What It Measures | How It's Calculated |
|--------|-----------------|---------------------|
| **Total Score** | Overall performance vs. historical data | Weighted metrics, percentile-based |
| **Consistency Score** | Well-roundedness across all metrics | Unweighted, compares to position average |
| **Top 15s (Power Five)** | Elite performance in specific metrics | Top 15 rank across Power Five |
| **Style Fits** | Alignment with Portland's playing style | Matches Portland's top 3 metrics + player's top 20% |

## Use Cases

**Filtering:**
- Focus on players with **2+ Style Fits** for better alignment
- Combine with Consistency Score to find well-rounded players who fit Portland's style

**Scouting Priority:**
- Players with **3+ Style Fits** are strong candidates for Portland's system
- Players with **0 Style Fits** may excel but in different ways than Portland plays

**Team Building:**
- Identify players who naturally fit Portland's tactical approach
- Reduce adaptation time and increase likelihood of success

## Technical Notes

- Only metrics defined in `position_metrics_config.json` under `style_fit_metrics` are checked
- Rankings are based on **per 90 values** (not percentages) for consistency
- Conference rank is shown for reference but doesn't count toward Style Fit (only Power Five rank counts)
- The calculation uses fuzzy matching to align NCAA metric names with NWSL metric names
- Duplicate metrics are automatically deduplicated (each unique metric counts once)

## Summary

**Style Fits = Number of metrics where:**
- Portland ranks **top 3** in NWSL **AND**
- Player ranks **top 20%** in Power Five

This identifies players whose strengths align with Portland's core playing style, making them potentially better fits for the team's tactical approach.

