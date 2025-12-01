# New Columns & Filters Suggestions

## 📊 Current Columns (Reference)

### Base Information
- Player, Team, Conference, Position
- Total Score, Conference Grade, Power Five Grade
- Previous Year, Previous Score, Change From Previous
- Changed Position, Total Minutes, % of Team Minutes
- Seasons Played, Top 15s (Power Five)

### Performance Metrics
- Consistency Score, Metrics Above Avg, Metrics Below Avg, Metrics At Avg
- Consistency %, Style Fits
- Position-specific per 90 metrics
- % better than position metrics

---

## 🆕 Suggested New Columns

### 1. Composite & Derived Metrics

#### 1.1 Elite Performance Index
- **Column**: `Elite Performance Index`
- **Calculation**: `(Top 15s × 2) + (Style Fits × 1.5) + (Consistency Score / 10)`
- **Purpose**: Single score combining elite performance indicators
- **Range**: 0-100+ (higher = more elite)
- **Filter**: `Elite Performance Index ≥ X` (e.g., ≥15)

#### 1.2 Well-Rounded Score
- **Column**: `Well-Rounded Score`
- **Calculation**: `(Metrics Above Avg / Total Metrics) × 100 - (Metrics Below Avg / Total Metrics) × 50`
- **Purpose**: Rewards consistency, penalizes weaknesses
- **Range**: -50 to 100
- **Filter**: `Well-Rounded Score ≥ X` (e.g., ≥60)

#### 1.3 Progression Rate
- **Column**: `Progression Rate`
- **Calculation**: `Change From Previous / Previous Score × 100` (if previous score exists)
- **Purpose**: Percentage improvement, accounts for starting point
- **Range**: -100% to +100%+
- **Filter**: `Progression Rate ≥ X%` (e.g., ≥10%)

#### 1.4 Stability Index
- **Column**: `Stability Index`
- **Calculation**: Based on variance in metrics (low variance = high stability)
- **Purpose**: Identifies consistent performers vs. volatile players
- **Range**: 0-100
- **Filter**: `Stability Index ≥ X` (e.g., ≥70)

---

### 2. Comparative Metrics

#### 2.1 Grade Differential
- **Column**: `Grade Differential`
- **Calculation**: Power Five Grade - Conference Grade (A=4, B=3, C=2, etc.)
- **Purpose**: Shows if player performs better against stronger competition
- **Range**: -3 to +3
- **Filter**: `Grade Differential ≥ 0` (better vs. Power Five) or `≥ +1` (significantly better)

#### 2.2 Score vs. Grade Alignment
- **Column**: `Score-Grade Alignment`
- **Calculation**: Check if Total Score aligns with grade (e.g., Score 9.0+ should be A)
- **Purpose**: Flags potential scoring inconsistencies
- **Values**: "Aligned", "Over-scored", "Under-scored"
- **Filter**: `Score-Grade Alignment = "Aligned"`

#### 2.3 Position Rank Percentile
- **Column**: `Position Rank Percentile`
- **Calculation**: `(Total Players - Rank) / Total Players × 100`
- **Purpose**: Shows percentile rank within position (e.g., 95th percentile)
- **Range**: 0-100
- **Filter**: `Position Rank Percentile ≥ X` (e.g., ≥90th percentile)

---

### 3. Style & Fit Metrics

#### 3.1 Style Fit Strength
- **Column**: `Style Fit Strength`
- **Calculation**: Average rank of metrics where player fits Portland style (lower rank = stronger)
- **Purpose**: Not just count, but how elite in those specific metrics
- **Range**: 1-100+ (lower = better)
- **Filter**: `Style Fit Strength ≤ X` (e.g., ≤10)

#### 3.2 Core Metric Excellence
- **Column**: `Core Metrics Top 15s`
- **Calculation**: Count of Top 15s in core position metrics only (from JSON config)
- **Purpose**: Focuses on fundamental position requirements
- **Range**: 0-10+
- **Filter**: `Core Metrics Top 15s ≥ X` (e.g., ≥2)

#### 3.3 Style Fit Coverage
- **Column**: `Style Fit Coverage %`
- **Calculation**: `(Style Fits / Total Style Fit Metrics) × 100`
- **Purpose**: Percentage of Portland's style metrics where player excels
- **Range**: 0-100%
- **Filter**: `Style Fit Coverage ≥ X%` (e.g., ≥50%)

---

### 4. Consistency & Reliability Metrics

#### 4.1 Consistency Trend
- **Column**: `Consistency Trend`
- **Calculation**: Compare Consistency Score across seasons (if multi-season)
- **Purpose**: Shows if player is improving or declining in consistency
- **Values**: "Improving", "Stable", "Declining", "N/A"
- **Filter**: `Consistency Trend = "Improving"` or `"Stable"`

#### 4.2 Reliability Score
- **Column**: `Reliability Score`
- **Calculation**: `(Metrics At Avg / Total Metrics) × 100` (metrics within 1% of average)
- **Purpose**: Measures how often player performs exactly at average
- **Range**: 0-100
- **Filter**: `Reliability Score ≤ X` (e.g., ≤20) - want players who are consistently above/below, not at average

#### 4.3 Volatility Index
- **Column**: `Volatility Index`
- **Calculation**: Standard deviation of all position metrics (normalized)
- **Purpose**: Measures how much player's metrics vary
- **Range**: 0-100 (lower = more consistent)
- **Filter**: `Volatility Index ≤ X` (e.g., ≤30)

---

### 5. Progression & Development Metrics

#### 5.1 Improvement Rate
- **Column**: `Improvement Rate`
- **Calculation**: `Change From Previous / Seasons Played` (if multi-season)
- **Purpose**: Average improvement per season
- **Range**: -10 to +10
- **Filter**: `Improvement Rate ≥ X` (e.g., ≥0.5 per season)

#### 5.2 Peak Performance Indicator
- **Column**: `Peak Performance`
- **Calculation**: Highest Total Score across all seasons (2021-2025)
- **Purpose**: Shows player's ceiling/peak ability
- **Range**: 0-10
- **Filter**: `Peak Performance ≥ X` (e.g., ≥9.0)

#### 5.3 Development Trajectory
- **Column**: `Development Trajectory`
- **Calculation**: Linear regression slope of scores across seasons
- **Purpose**: Predicts if player is on upward or downward trend
- **Values**: "Rising", "Stable", "Declining", "Insufficient Data"
- **Filter**: `Development Trajectory = "Rising"`

---

### 6. Position-Specific Composite Metrics

#### 6.1 Defensive Action Rate (CBs/DMs)
- **Column**: `Defensive Action Rate`
- **Calculation**: `(Defensive Duels + Interceptions + Sliding Tackles) per 90`
- **Purpose**: Total defensive involvement
- **Filter**: `Defensive Action Rate ≥ X` (position-specific)

#### 6.2 Creative Output Index (AMs/Wingers)
- **Column**: `Creative Output Index`
- **Calculation**: `(Assists + Shot Assists + Key Passes + Smart Passes) per 90`
- **Purpose**: Total creative contribution
- **Filter**: `Creative Output Index ≥ X`

#### 6.3 Ball Progression Score (All Positions)
- **Column**: `Ball Progression Score`
- **Calculation**: `(Progressive Passes + Progressive Runs + Deep Completions) per 90`
- **Purpose**: Measures forward movement contribution
- **Filter**: `Ball Progression Score ≥ X`

#### 6.4 Aerial Dominance (CBs)
- **Column**: `Aerial Dominance`
- **Calculation**: `Aerial Duels per 90 × Aerial Duels Won %`
- **Purpose**: Combined volume and success in aerial duels
- **Filter**: `Aerial Dominance ≥ X`

---

### 7. Efficiency Metrics

#### 7.1 Efficiency Score
- **Column**: `Efficiency Score`
- **Calculation**: `(Goals + Assists) / (xG + xA)` (if > 0)
- **Purpose**: Measures over/under-performance vs. expected
- **Range**: 0-2+ (1.0 = expected, >1.0 = over-performing)
- **Filter**: `Efficiency Score ≥ X` (e.g., ≥1.1)

#### 7.2 Pass Efficiency
- **Column**: `Pass Efficiency`
- **Calculation**: `Accurate Passes % × Passes per 90 / 100`
- **Purpose**: Combines volume and accuracy
- **Filter**: `Pass Efficiency ≥ X`

#### 7.3 Duel Efficiency
- **Column**: `Duel Efficiency`
- **Calculation**: Weighted average of all duel win percentages
- **Purpose**: Overall duel success rate
- **Range**: 0-100%
- **Filter**: `Duel Efficiency ≥ X%` (e.g., ≥60%)

---

### 8. Contextual Metrics

#### 8.1 Team Strength Adjustment
- **Column**: `Team Strength Adjusted Score`
- **Calculation**: Adjust Total Score based on team's conference ranking
- **Purpose**: Accounts for playing on stronger/weaker teams
- **Filter**: `Team Strength Adjusted Score ≥ X`

#### 8.2 Competition Level Factor
- **Column**: `Competition Level Factor`
- **Calculation**: Average rank of opponents faced (if available)
- **Purpose**: Accounts for strength of schedule
- **Range**: 0-1 (higher = stronger competition)
- **Filter**: `Competition Level Factor ≥ X`

#### 8.3 Clutch Performance Index
- **Column**: `Clutch Performance Index`
- **Calculation**: Performance in high-pressure situations (if data available)
- **Purpose**: Measures performance when it matters most
- **Filter**: `Clutch Performance Index ≥ X`

---

### 9. Predictive Metrics

#### 9.1 NWSL Readiness Score
- **Column**: `NWSL Readiness Score`
- **Calculation**: Based on comparison to successful NCAA→NWSL transitions
- **Purpose**: Predicts likelihood of NWSL success
- **Range**: 0-100
- **Filter**: `NWSL Readiness Score ≥ X` (e.g., ≥75)

#### 9.2 Upside Potential
- **Column**: `Upside Potential`
- **Calculation**: `(Peak Performance - Current Score) + (Progression Rate × 2)`
- **Purpose**: Estimates how much player could improve
- **Range**: 0-10+
- **Filter**: `Upside Potential ≥ X` (e.g., ≥2.0)

#### 9.3 Risk Factor
- **Column**: `Risk Factor`
- **Calculation**: Combines volatility, consistency trends, and progression
- **Purpose**: Measures uncertainty/risk in player evaluation
- **Range**: 0-100 (lower = less risky)
- **Filter**: `Risk Factor ≤ X` (e.g., ≤30)

---

### 10. Comparison Metrics

#### 10.1 vs. Position Average
- **Column**: `vs. Position Average`
- **Calculation**: `Total Score - Position Average Score`
- **Purpose**: Shows how much above/below position average
- **Range**: -10 to +10
- **Filter**: `vs. Position Average ≥ X` (e.g., ≥+1.0)

#### 10.2 vs. Top 10% of Position
- **Column**: `vs. Top 10% Average`
- **Calculation**: `Total Score - Top 10% Average Score`
- **Purpose**: Comparison to elite tier
- **Range**: -10 to +10
- **Filter**: `vs. Top 10% Average ≥ X`

#### 10.3 Percentile Rank
- **Column**: `Percentile Rank`
- **Calculation**: Percentile based on Total Score distribution
- **Purpose**: Shows where player ranks in distribution
- **Range**: 0-100
- **Filter**: `Percentile Rank ≥ X` (e.g., ≥90th percentile)

---

## 🔍 New Filters Based on New Columns

### Quick Win Filters (Easy to Implement)

1. **Elite Performance Index ≥ 15**
   - Combines Top 15s, Style Fits, and Consistency
   
2. **Well-Rounded Score ≥ 60**
   - Ensures multi-dimensional excellence
   
3. **Grade Differential ≥ 0**
   - Only players who perform as well or better vs. Power Five
   
4. **Core Metrics Top 15s ≥ 2**
   - Excellence in fundamental position requirements
   
5. **Style Fit Coverage ≥ 50%**
   - Strong alignment with Portland's style

### Advanced Filters (Medium Effort)

6. **Development Trajectory = "Rising"**
   - Only players on upward trend
   
7. **Peak Performance ≥ 9.0**
   - Players who have reached elite levels
   
8. **NWSL Readiness Score ≥ 75**
   - Based on historical transition data
   
9. **Risk Factor ≤ 30**
   - Lower uncertainty/risk players

### Position-Specific Filters

10. **CBs: Aerial Dominance ≥ X**
11. **AMs/Wingers: Creative Output Index ≥ X**
12. **All: Ball Progression Score ≥ X**
13. **CBs/DMs: Defensive Action Rate ≥ X**

---

## 📈 Recommended Column Additions (Priority Order)

### Phase 1: High Value, Easy Implementation
1. ✅ **Elite Performance Index** - Single composite score
2. ✅ **Grade Differential** - Simple calculation
3. ✅ **Core Metrics Top 15s** - Uses existing data
4. ✅ **Style Fit Coverage %** - Uses existing data
5. ✅ **vs. Position Average** - Simple comparison

### Phase 2: Medium Value, Medium Effort
6. ⚠️ **Well-Rounded Score** - More complex calculation
7. ⚠️ **Progression Rate** - Requires previous score handling
8. ⚠️ **Development Trajectory** - Requires multi-season analysis
9. ⚠️ **Position-Specific Composites** - Custom per position

### Phase 3: Advanced Analytics
10. 🔧 **NWSL Readiness Score** - Requires historical data analysis
11. 🔧 **Upside Potential** - Predictive metric
12. 🔧 **Team Strength Adjustment** - Requires team ranking data
13. 🔧 **Volatility Index** - Statistical calculation

---

## 💡 Implementation Strategy

### Step 1: Add Columns to Shortlist Report
- Add new calculated columns to `create_top_15_report.py`
- Include in Excel output with proper formatting

### Step 2: Add Columns to Conference Reports
- Update `update_mike_norris_reports.py` to include new columns
- Ensure consistency across all reports

### Step 3: Add Filters to Scripts
- Update filtering logic to use new columns
- Add filter options to command-line or config file

### Step 4: Update Player Overviews
- Include new metrics in PDF overviews
- Add to summary section if relevant

---

## 🎯 Questions for Team

1. **Which new columns provide the most value for scouting decisions?**
2. **Are there specific position-specific metrics we should prioritize?**
3. **Do we want predictive metrics (NWSL Readiness, Upside Potential)?**
4. **Should we add team/contextual adjustments to scores?**
5. **Are there any metrics from other scouting systems we should adopt?**

---

## 📝 Example: Complete Filter Combination

### "Elite Multi-Dimensional Player" Filter
- **Elite Performance Index ≥ 15**
- **Well-Rounded Score ≥ 60**
- **Core Metrics Top 15s ≥ 2**
- **Style Fit Coverage ≥ 50%**
- **Consistency Score ≥ 70**
- **Grade Differential ≥ 0**

This would identify players who are:
- Elite in multiple areas
- Well-rounded (few weaknesses)
- Excellent in core position requirements
- Strong Portland style fit
- Consistent performers
- Perform well vs. stronger competition

---

## 🔗 Integration with Existing Metrics

All new columns can be:
- ✅ Added to shortlist Excel reports
- ✅ Added to conference reports
- ✅ Included in player overview PDFs
- ✅ Used in AI Shortlist generation
- ✅ Filtered in `create_top_15_report.py`
- ✅ Visualized in future dashboards





