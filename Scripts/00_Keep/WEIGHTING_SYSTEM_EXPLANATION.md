# Metric Weighting System Explanation

## Current System Overview

### Structure
1. **Two Categories**: Core and Specific metrics
2. **Metric Groups**: Each category contains multiple metric groups
3. **Component Metrics**: Each metric group can have multiple component metrics
4. **Equal Distribution**: Within each category, metric groups are weighted equally

### Example: Center Back (Hybrid CB)

**Core Metrics** (3 groups, each 12.5% weight):
- Defensive duels per 90 + Defensive duels won, % (12.5%)
- PAdj Interceptions + PAdj Sliding tackles (12.5%)
- Shots blocked per 90 (12.5%)
- **Core Total: 37.5%**

**Specific Metrics** (5 groups, each 12.5% weight):
- Aerial duels per 90 + Aerial duels won, % (12.5%)
- Passes per 90 + Accurate passes, % (12.5%)
- Short/medium passes per 90 + Accurate short/medium passes, % (12.5%)
- Long passes per 90 + Accurate long passes, % (12.5%)
- Progressive passes per 90 + Accurate progressive passes, % (12.5%)
- **Specific Total: 62.5%**

### Component Weights Within Groups

Most composite metrics use an **80/20 split**:
- **80% weight**: Volume metric (e.g., "Defensive duels per 90")
- **20% weight**: Accuracy/quality metric (e.g., "Defensive duels won, %")

This emphasizes volume over quality, assuming that more attempts are more valuable than higher success rates.

## Scoring Process

### Step 1: Normalization
Each metric component is normalized using **min-max normalization**:
```
normalized_value = (value - min) / (max - min)
```
- Uses historical data (2021-2025) to determine min/max
- Scales all values to 0-1 range
- If value is outside 0-100 range, uses full range; otherwise assumes 0-100

### Step 2: Component Combination
Within each metric group, components are weighted and combined:
```
composite_score = (component1_norm × weight1) + (component2_norm × weight2)
```

### Step 3: Metric Group Weighting
Each metric group's score is multiplied by its category weight:
```
contribution = composite_score × metric_group_weight
```

### Step 4: Total Score
```
Total Score = Sum of all Core contributions + Sum of all Specific contributions
```

### Step 5: Percentile & Grade
- Compare each player's total score against ALL 2025 players
- Calculate percentile rank (0-100)
- Convert to 1-10 scale using linear mapping within each decile

## Potential Improvements

### 1. **Weighted Core vs Specific**
**Current**: Roughly equal (37.5% Core, 62.5% Specific for CB)
**Suggestion**: Core metrics might deserve more weight (60-70%) as they're more fundamental
**Action**: Adjust weights based on expert judgment or analysis

### 2. **Volume vs Accuracy Balance**
**Current**: 80% volume, 20% accuracy
**Suggestion**: 
- Test different ratios (70/30, 60/40, 50/50)
- Position-specific: Defenders might need more accuracy weight
- Analyze which ratio best distinguishes elite players

### 3. **Correlation Analysis**
**Current**: Metrics treated independently
**Issue**: Highly correlated metrics get double weight
**Suggestion**:
- Calculate correlation matrix between all metrics
- Identify redundant metrics (e.g., "Passes per 90" correlates with "Accurate passes, %")
- Adjust weights to avoid double-counting
- Consider using factor analysis or PCA

### 4. **Robust Normalization**
**Current**: Min-max normalization (sensitive to outliers)
**Suggestion**:
- Use percentile-based normalization (5th-95th percentile as range)
- Or z-score normalization with robust statistics (median, IQR)
- Cap outliers at 99th percentile before normalization

### 5. **Expert-Weighted Metrics**
**Current**: Equal weights within categories
**Suggestion**:
- Survey coaches/scouts on metric importance
- Use machine learning to identify which metrics best predict success
- Weight metrics based on correlation with elite performance

### 6. **Missing Data Strategy**
**Current**: Missing values filled with 0 or default low score
**Suggestion**:
- Use imputation based on similar players (same position, similar minutes)
- Weight contributions based on data completeness
- Flag players with incomplete data in reports

### 7. **Position-Specific Adjustments**
**Current**: Same weighting structure for all positions
**Suggestion**:
- Different positions might need different volume/accuracy ratios
- Defenders: More weight on accuracy (50/50 or 40/60)
- Attackers: More weight on volume (80/20 or 70/30)
- Midfielders: Balanced (60/40 or 70/30)

## Recommended Next Steps

1. **Analyze Current System**:
   - Run correlation analysis on all metrics
   - Identify which metrics best predict elite performance
   - Check for outliers affecting normalization

2. **Test Improvements**:
   - Create test versions with different weightings
   - Compare rankings of known elite players
   - Validate that changes improve discrimination

3. **Expert Input**:
   - Get feedback from coaches/scouts on metric importance
   - Validate that weighting aligns with position requirements
   - Adjust based on real-world performance

4. **Iterative Refinement**:
   - Track how well rankings predict future performance
   - Adjust weights based on outcomes
   - Document changes for transparency

## Current Weighting Summary

For most positions:
- **Core metrics**: 2-3 groups, each ~12.5-14.3% weight
- **Specific metrics**: 4-6 groups, each ~12.5% weight
- **Component weights**: Typically 80% volume, 20% accuracy
- **Total**: All weights sum to 100%

The system is designed to be:
- **Transparent**: Clear weight structure
- **Equal**: Fair distribution within categories
- **Flexible**: Easy to adjust individual weights
- **Normalized**: All metrics on same 0-1 scale before combining

















