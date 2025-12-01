# Additional Filter Suggestions for Player Shortlist

## Current Filters (Already Implemented)
1. ✅ **% of Team Minutes**: ≥70% threshold
2. ✅ **Score Progression**: Exclude players whose 2025 score is lower than previous score
3. ✅ **Grade Filter**: Only B and above for both Conference Grade and Power Five Grade
4. ✅ **Consistency Metrics**: Available for analysis (Metrics Above/Below/At Avg)
5. ✅ **Style Fits**: Available for analysis (PT Style Fits count)
6. ✅ **Top 15s**: Available for analysis (Top 15s Power Five count)

---

## 🎯 Suggested Additional Filters

### 1. Consistency-Based Filters

#### 1.1 Minimum Consistency Score
- **Filter**: Only players with Consistency Score ≥ X (e.g., ≥70)
- **Rationale**: Ensures players are well-rounded, not just elite in one area
- **Implementation**: Simple threshold check on `Consistency Score` column
- **Example**: "Only show players with Consistency Score ≥ 75"

#### 1.2 Maximum Metrics Below Average
- **Filter**: Exclude players with more than X metrics below average (e.g., ≤3)
- **Rationale**: Identifies players with fewer weaknesses
- **Implementation**: Check `Metrics Below Avg` column (e.g., "≤3/17")
- **Example**: "Exclude players with more than 3 below-average metrics"

#### 1.3 Minimum Metrics Above Average
- **Filter**: Only players with at least X metrics above average (e.g., ≥10)
- **Rationale**: Ensures multi-dimensional excellence
- **Implementation**: Check `Metrics Above Avg` column (e.g., "≥10/17")
- **Example**: "Only show players with at least 10 metrics above average"

---

### 2. Elite Performance Filters

#### 2.1 Minimum Top 15s Count
- **Filter**: Only players with ≥X Top 15s (Power Five) (e.g., ≥3)
- **Rationale**: Focuses on players who are elite in multiple metrics
- **Implementation**: Threshold on `Top 15s (Power Five)` column
- **Example**: "Only players with at least 3 Top 15s"

#### 2.2 Minimum Style Fits Count
- **Filter**: Only players with ≥X PT Style Fits (e.g., ≥2)
- **Rationale**: Ensures alignment with Portland's playing style
- **Implementation**: Threshold on `Style Fits` column
- **Example**: "Only players with at least 2 style fits"

#### 2.3 Combined Elite Performance
- **Filter**: Top 15s + Style Fits ≥ X (e.g., ≥5 combined)
- **Rationale**: Rewards both elite performance AND style alignment
- **Implementation**: Sum of both columns
- **Example**: "Top 15s + Style Fits ≥ 5"

---

### 3. Progression & Development Filters

#### 3.1 Minimum Score Improvement
- **Filter**: Only players with Change From Previous ≥ X (e.g., ≥+0.5)
- **Rationale**: Focuses on players showing improvement/development
- **Implementation**: Threshold on `Change From Previous` column
- **Example**: "Only players who improved by at least +0.5 points"

#### 3.2 Multi-Season Consistency
- **Filter**: Only players with ≥X seasons played (e.g., ≥2)
- **Rationale**: Prefers experienced players with track record
- **Implementation**: Check `Seasons Played` column (exclude "Rookie")
- **Example**: "Only players with 2+ seasons"

#### 3.3 Rookie Exclusion (or Inclusion)
- **Filter**: Exclude rookies OR only show rookies
- **Rationale**: Different strategies for immediate vs. long-term needs
- **Implementation**: Filter on `Seasons Played` = "Rookie"
- **Example**: "Exclude rookies" or "Only rookies"

---

### 4. Grade-Based Filters

#### 4.1 Double A Grade Requirement
- **Filter**: Only players with A/A grades (Conference/Power Five)
- **Rationale**: Focuses on the absolute elite performers
- **Implementation**: Check both `Conference Grade` and `Power Five Grade` = "A"
- **Example**: "Only double A grade players"

#### 4.2 At Least One A Grade
- **Filter**: At least one A grade (Conference OR Power Five)
- **Rationale**: Includes players elite in at least one context
- **Implementation**: Check if either grade = "A"
- **Example**: "At least one A grade"

#### 4.3 Grade Elevation Filter
- **Filter**: Power Five Grade ≥ Conference Grade (or vice versa)
- **Rationale**: Identifies players who perform better against stronger competition
- **Implementation**: Compare grade values (A > B > C)
- **Example**: "Power Five Grade ≥ Conference Grade"

---

### 5. Score-Based Filters

#### 5.1 Minimum Total Score
- **Filter**: Only players with Total Score ≥ X (e.g., ≥8.0)
- **Rationale**: Sets a quality floor
- **Implementation**: Threshold on `Total Score` column
- **Example**: "Only players with Total Score ≥ 8.5"

#### 5.2 Score Range Filter
- **Filter**: Total Score between X and Y (e.g., 8.0-9.5)
- **Rationale**: Focuses on specific tier of players
- **Implementation**: Range check on `Total Score`
- **Example**: "Total Score between 8.0 and 9.5"

---

### 6. Position-Specific Metric Filters

#### 6.1 Key Metric Thresholds
- **Filter**: Minimum value in specific position-critical metrics
- **Rationale**: Ensures players meet minimum standards for key position requirements
- **Implementation**: Position-specific thresholds (e.g., CBs: Defensive duels ≥X, Passes ≥Y)
- **Example**: 
  - "CBs: Defensive duels per 90 ≥ 8.0"
  - "AMs: Assists per 90 ≥ 0.3"
  - "Wingers: Dribbles per 90 ≥ 5.0"

#### 6.2 Core Metric Excellence
- **Filter**: Top 15 in at least one core position metric
- **Rationale**: Ensures excellence in fundamental position requirements
- **Implementation**: Check Top 15s for core metrics only (from JSON config)
- **Example**: "Top 15 in at least one core metric"

---

### 7. Composite Score Filters

#### 7.1 Weighted Composite Score
- **Filter**: Custom weighted score combining multiple factors
- **Formula**: `(Total Score × 0.3) + (Style Fits × 0.25) + (Consistency Score/10 × 0.2) + (Top 15s × 0.15) + (Change From Previous × 0.1)`
- **Rationale**: Balances multiple factors into single score
- **Implementation**: Calculate new column, then filter
- **Example**: "Composite Score ≥ 7.5"

#### 7.2 AI Score Threshold
- **Filter**: Use existing AI Score from AI Shortlist
- **Rationale**: Leverages already-calculated composite score
- **Implementation**: Filter on `AI Score` column from AI Shortlist
- **Example**: "AI Score ≥ 0.75"

---

### 8. Conference & Team Filters

#### 8.1 Conference Strength Weighting
- **Filter**: Prioritize players from stronger conferences
- **Rationale**: Competition level matters
- **Implementation**: Weight by conference (e.g., SEC/ACC = 1.0, Big Ten = 0.95, etc.)
- **Example**: "Only players from top 3 conferences"

#### 8.2 Team Performance Filter
- **Filter**: Only players from teams with certain performance metrics
- **Rationale**: Team context affects player development
- **Implementation**: Requires team stats data
- **Example**: "Only players from top 25% of teams"

---

### 9. Playing Time Filters

#### 9.1 Absolute Minutes Threshold
- **Filter**: Minimum total minutes played (e.g., ≥1000 minutes)
- **Rationale**: Ensures sufficient sample size for reliable metrics
- **Implementation**: Threshold on `Total Minutes` column
- **Example**: "At least 1000 minutes played"

#### 9.2 Minutes Consistency
- **Filter**: Consistent playing time across seasons (if multi-season)
- **Rationale**: Identifies reliable starters
- **Implementation**: Check % of team minutes across seasons
- **Example**: "≥70% of team minutes in all seasons"

---

### 10. Advanced Combination Filters

#### 10.1 Multi-Dimensional Excellence
- **Filter**: Combines multiple criteria
- **Criteria**: 
  - Consistency Score ≥ 70
  - Top 15s ≥ 3
  - Style Fits ≥ 2
  - Metrics Above Avg ≥ 10/17
- **Rationale**: Ensures well-rounded elite players
- **Example**: "Multi-dimensional excellence filter"

#### 10.2 High Potential Filter
- **Filter**: For younger/developing players
- **Criteria**:
  - Rookie OR 2 seasons
  - Positive progression (Change ≥ +0.3)
  - At least 1 Top 15
  - Consistency Score ≥ 60
- **Rationale**: Identifies high-upside players
- **Example**: "High potential filter"

#### 10.3 Ready-Now Filter
- **Filter**: For immediate impact players
- **Criteria**:
  - Total Score ≥ 8.5
  - 2+ seasons
  - Style Fits ≥ 2
  - Consistency Score ≥ 75
- **Rationale**: Identifies players ready for immediate contribution
- **Example**: "Ready-now filter"

---

## 📊 Recommended Filter Combinations

### Tier 1: Elite Only
- Double A grades (A/A)
- Total Score ≥ 9.0
- Top 15s ≥ 5
- Style Fits ≥ 3

### Tier 2: Strong Candidates
- At least one A grade
- Total Score ≥ 8.0
- Consistency Score ≥ 70
- Top 15s ≥ 2 OR Style Fits ≥ 2

### Tier 3: High Potential
- Positive progression (Change ≥ +0.3)
- Consistency Score ≥ 65
- At least 1 Top 15
- Metrics Above Avg ≥ 8/17

---

## 💡 Implementation Notes

### Easy to Implement (Low Effort)
- ✅ Minimum Consistency Score
- ✅ Maximum Metrics Below Average
- ✅ Minimum Top 15s Count
- ✅ Minimum Style Fits Count
- ✅ Minimum Total Score
- ✅ Double A Grade Requirement
- ✅ Minimum Score Improvement
- ✅ Rookie Inclusion/Exclusion

### Medium Effort (Requires Some Development)
- ⚠️ Position-specific metric thresholds
- ⚠️ Composite score calculations
- ⚠️ Multi-season consistency checks
- ⚠️ Conference strength weighting

### Higher Effort (Requires Additional Data/Logic)
- 🔧 Team performance filters
- 🔧 Advanced combination filters
- 🔧 Key metric excellence (core vs. specific)

---

## 🎯 Suggested Next Steps

1. **Ask team**: Which filters are most valuable for their scouting process?
2. **Prioritize**: Start with easy-to-implement filters that provide most value
3. **Test**: Apply filters and review resulting shortlist quality
4. **Iterate**: Refine thresholds based on results

---

## 📝 Questions to Ask Team

1. What's the target shortlist size per position? (Currently ~15)
2. Are there specific metrics that are "must-haves" for each position?
3. How important is progression vs. current performance?
4. Should we prioritize style fit or overall excellence?
5. Are there any "red flags" that should automatically exclude players?





