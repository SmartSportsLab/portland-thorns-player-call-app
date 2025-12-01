# Power BI Alignment Notebook - Complete Requirements Checklist

## 📋 Overview
This document lists all components that need to be included in the Jupyter notebook for Power BI data alignment. The notebook should contain all data processing logic, calculations, and transformations needed to produce the final datasets that Power BI will consume.

---

## 🔧 1. SETUP & CONFIGURATION

### 1.1 Import Statements
- [ ] `pandas` - Data manipulation
- [ ] `numpy` - Numerical operations
- [ ] `openpyxl` - Excel file reading/writing
- [ ] `json` - Configuration file loading
- [ ] `pathlib.Path` - File path handling
- [ ] `sys` - System path modifications
- [ ] `re` - Regular expressions (for data cleaning)
- [ ] `datetime` - Date handling (if needed)

### 1.2 Path Configuration
- [ ] Base directory path setup
- [ ] Input data directories:
  - [ ] Championship Reports directory
  - [ ] Raw player stats directory (`Exports/Players Stats By Position`)
  - [ ] Team stats directory (`Brief Conferences/[Conference]/Team Stats`)
  - [ ] Historical data directory (`NWSL/Past Seasons`)
- [ ] Output directory for Power BI exports
- [ ] Configuration file paths

### 1.3 Configuration Files
- [ ] `position_metrics_config.json` - Position-specific metric weightings
- [ ] Position profile mappings:
  - [ ] `'Hybrid CB'` → `'Center Back'`
  - [ ] `'DM Box-To-Box'` → `'Centre Midfielder'`
  - [ ] `'AM Advanced Playmaker'` → `'Attacking Midfielder'`
  - [ ] `'Right Touchline Winger'` → `'Winger'`
- [ ] Conference list: `['ACC', 'SEC', 'BIG10', 'BIG12', 'IVY']`
- [ ] Position filters for Wyscout positions

### 1.4 Constants
- [ ] Grade colors mapping
- [ ] Position initials mapping
- [ ] Minimum thresholds (matches, minutes)
- [ ] Scoring weights (80/20 intent vs accuracy)

---

## 📊 2. DATA LOADING FUNCTIONS

### 2.1 Championship Report Loading
- [ ] Function to load players from conference report Excel files
- [ ] Handle merged headers (row 1 + row 2)
- [ ] Read position profile sheets
- [ ] Extract base columns:
  - [ ] Player, Team, Conference, Position
  - [ ] Total Score, Conference Grade, Power Five Grade
  - [ ] Previous Year, Previous Score, Change From Previous
  - [ ] Changed Position, Total Minutes, % of Team Minutes
  - [ ] Seasons Played, Top 15s (Power Five)
  - [ ] Consistency Score, Metrics Above/Below/At Avg
  - [ ] Consistency %, Style Fits
- [ ] Extract all position-specific metrics (per 90, percentages)

### 2.2 Raw Data Loading
- [ ] Function to load raw player stats from Excel files
- [ ] Match players by name and team
- [ ] Handle team name variations
- [ ] Load data by conference and position
- [ ] Handle missing data (fill with 0)

### 2.3 Historical Data Loading
- [ ] Function to load historical season data (2021-2024)
- [ ] Count seasons played per player
- [ ] Extract previous year scores
- [ ] Calculate progression metrics

### 2.4 Team Stats Loading
- [ ] Function to load team statistics
- [ ] Calculate team averages
- [ ] Calculate team position averages
- [ ] Load Portland Thorns team stats for style fit analysis

---

## 🧮 3. CALCULATION FUNCTIONS

### 3.1 Scoring Functions
- [ ] `calculate_with_historical_normalization()` - Historical percentile scoring
- [ ] `calculate_percentile_against_distribution()` - Percentile calculations
- [ ] `convert_percentile_to_1_10()` - Score conversion (0-10 scale)
- [ ] `assign_grade_single()` - Grade assignment (A-F)
- [ ] Position-specific metric weighting
- [ ] Composite metric calculations (e.g., "Interceptions + Sliding Tackles")

### 3.2 Consistency Calculations
- [ ] `calculate_position_averages()` - Calculate metric averages per position
- [ ] `calculate_consistency_score()` - Compare player metrics to averages
- [ ] Categorize metrics as Above/Below/At average
- [ ] Calculate consistency percentage
- [ ] Handle combined/composite metrics

### 3.3 Style Fit Calculations
- [ ] Load Portland Thorns team rankings
- [ ] Identify Portland's top 3 metrics (top 20% threshold)
- [ ] Calculate player ranks in those metrics (Power Five)
- [ ] Determine style fits (top 20% threshold)
- [ ] Count total style fits per player

### 3.4 Top 15 Calculations
- [ ] Calculate Top 15 rankings per metric (Power Five only)
- [ ] Count total Top 15s per player
- [ ] Identify which metrics player ranks Top 15

### 3.5 Progression Calculations
- [ ] Compare current score to previous year
- [ ] Calculate change from previous
- [ ] Identify position changes
- [ ] Calculate improvement rate

---

## 🔄 4. DATA TRANSFORMATION FUNCTIONS

### 4.1 Data Merging
- [ ] Merge championship report data with raw player stats
- [ ] Handle player name matching (exact and fuzzy)
- [ ] Handle team name matching
- [ ] Preserve report data when merging
- [ ] Fill missing metric values with 0

### 4.2 Data Cleaning
- [ ] Standardize player names
- [ ] Standardize team names
- [ ] Handle merged cells in Excel
- [ ] Remove duplicates
- [ ] Handle NaN/null values
- [ ] Convert data types (numeric, string, date)

### 4.3 Data Enrichment
- [ ] Add conference information
- [ ] Add position profile information
- [ ] Add season information
- [ ] Add team context (team averages)
- [ ] Add position context (position averages)

### 4.4 Metric Calculations
- [ ] Calculate per 90 metrics (if not already)
- [ ] Calculate percentage metrics
- [ ] Calculate "% better than position" metrics
- [ ] Calculate composite metrics
- [ ] Normalize metrics for comparison

---

## 📈 5. REPORT GENERATION FUNCTIONS

### 5.1 Shortlist Report Functions
- [ ] `load_all_players_from_reports()` - Load all players across conferences
- [ ] Filter by grade (B and above)
- [ ] Filter by position profile
- [ ] Sort by Total Score
- [ ] Generate Excel output with formatting

### 5.2 AI Shortlist Functions
- [ ] `calculate_ai_score()` - Composite scoring
- [ ] Select top 15 players per position
- [ ] Generate reasoning for selections
- [ ] Output formatted report

### 5.3 Full Shortlist Functions
- [ ] Generate unfiltered shortlist
- [ ] Include all players with data
- [ ] Apply sorting and ranking

---

## 📤 6. POWER BI EXPORT FUNCTIONS

### 6.1 Data Preparation for Power BI
- [ ] Flatten nested data structures
- [ ] Standardize column names (Power BI friendly)
- [ ] Remove special characters from column names
- [ ] Ensure consistent data types
- [ ] Create date columns (if needed)
- [ ] Create dimension tables (Players, Teams, Conferences, Positions)

### 6.2 Fact Tables
- [ ] **Player Performance Fact Table**:
  - [ ] Player ID (or name)
  - [ ] Team ID
  - [ ] Conference ID
  - [ ] Position Profile ID
  - [ ] Season/Year
  - [ ] All performance metrics
  - [ ] Scores and grades
  - [ ] Consistency metrics
  - [ ] Style fit metrics
  - [ ] Top 15 counts

- [ ] **Player Summary Fact Table**:
  - [ ] Player ID
  - [ ] Total Score
  - [ ] Conference Grade
  - [ ] Power Five Grade
  - [ ] Consistency Score
  - [ ] Style Fits Count
  - [ ] Top 15s Count
  - [ ] Progression metrics

### 6.3 Dimension Tables
- [ ] **Players Dimension**:
  - [ ] Player ID
  - [ ] Player Name
  - [ ] Full Name (if available)
  - [ ] Team
  - [ ] Conference
  - [ ] Position Profile
  - [ ] Seasons Played
  - [ ] Total Minutes
  - [ ] % of Team Minutes

- [ ] **Teams Dimension**:
  - [ ] Team ID
  - [ ] Team Name
  - [ ] Conference
  - [ ] Team averages (for context)

- [ ] **Conferences Dimension**:
  - [ ] Conference ID
  - [ ] Conference Name
  - [ ] Conference Code

- [ ] **Position Profiles Dimension**:
  - [ ] Position Profile ID
  - [ ] Position Profile Name
  - [ ] Internal Position Name
  - [ ] Position Initials

- [ ] **Metrics Dimension**:
  - [ ] Metric ID
  - [ ] Metric Name
  - [ ] Metric Type (per 90, %, composite)
  - [ ] Position Relevance
  - [ ] Metric Weight (by position)

### 6.4 Export Formats
- [ ] Export to CSV (for Power BI import)
- [ ] Export to Excel (multiple sheets)
- [ ] Export to Parquet (if Power BI supports)
- [ ] Export to JSON (for reference)
- [ ] Include metadata file (column descriptions)

---

## 🎯 7. SPECIFIC DATA POINTS TO INCLUDE

### 7.1 Player Base Information
- [ ] Player Name (First Initial. Last Name format)
- [ ] Team Name
- [ ] Conference
- [ ] Position Profile
- [ ] Season/Year

### 7.2 Scoring Metrics
- [ ] Total Score (0-10 scale)
- [ ] Conference Grade (A-F)
- [ ] Power Five Grade (A-F)
- [ ] Previous Year Score
- [ ] Change From Previous
- [ ] Previous Year (if applicable)

### 7.3 Consistency Metrics
- [ ] Consistency Score (0-100)
- [ ] Metrics Above Avg (X/Y format)
- [ ] Metrics Below Avg (X/Y format)
- [ ] Metrics At Avg (X/Y format)
- [ ] Consistency % (percentage)
- [ ] List of below-average metrics (if needed)

### 7.4 Style Fit Metrics
- [ ] Style Fits Count (integer)
- [ ] Which metrics are style fits (list)
- [ ] Player rank in each style fit metric
- [ ] Portland rank in each style fit metric

### 7.5 Top 15 Metrics
- [ ] Top 15s (Power Five) Count
- [ ] Which metrics player ranks Top 15 (list)
- [ ] Rank in each Top 15 metric

### 7.6 Position-Specific Metrics
- [ ] All per 90 metrics (position-specific)
- [ ] All percentage metrics (position-specific)
- [ ] All "% better than position" metrics
- [ ] Composite metrics (if applicable)

### 7.7 Contextual Metrics
- [ ] Total Minutes
- [ ] % of Team Minutes
- [ ] Seasons Played
- [ ] Changed Position (Y/N or position codes)
- [ ] Team Average for each metric
- [ ] Team Position Average for each metric

---

## 🔍 8. DATA VALIDATION & QUALITY CHECKS

### 8.1 Data Quality Functions
- [ ] Check for missing required fields
- [ ] Validate data types
- [ ] Check for duplicate players
- [ ] Validate score ranges (0-10)
- [ ] Validate grade values (A-F)
- [ ] Check consistency score ranges (0-100)
- [ ] Validate metric value ranges (reasonable bounds)

### 8.2 Data Completeness Checks
- [ ] Count players per conference
- [ ] Count players per position
- [ ] Identify missing data patterns
- [ ] Report data coverage percentages

### 8.3 Data Alignment Checks
- [ ] Verify player names match across sources
- [ ] Verify team names match across sources
- [ ] Check metric column alignment
- [ ] Verify calculations match expected outputs

---

## 📝 9. DOCUMENTATION & METADATA

### 9.1 Column Descriptions
- [ ] Document each column's purpose
- [ ] Document calculation methods
- [ ] Document data sources
- [ ] Document update frequency

### 9.2 Data Dictionary
- [ ] Column names
- [ ] Data types
- [ ] Value ranges
- [ ] Null handling
- [ ] Example values

### 9.3 Calculation Documentation
- [ ] Scoring methodology
- [ ] Consistency calculation explanation
- [ ] Style fit calculation explanation
- [ ] Top 15 calculation explanation
- [ ] Progression calculation explanation

---

## 🚀 10. NOTEBOOK STRUCTURE

### 10.1 Recommended Cell Organization
1. **Setup Cell**:
   - [ ] Imports
   - [ ] Path configuration
   - [ ] Constants

2. **Configuration Cell**:
   - [ ] Load JSON configs
   - [ ] Set up mappings
   - [ ] Define filters

3. **Data Loading Cells** (one per data source):
   - [ ] Load championship reports
   - [ ] Load raw player stats
   - [ ] Load historical data
   - [ ] Load team stats

4. **Data Processing Cells**:
   - [ ] Merge data
   - [ ] Clean data
   - [ ] Calculate metrics

5. **Calculation Cells**:
   - [ ] Calculate scores
   - [ ] Calculate consistency
   - [ ] Calculate style fits
   - [ ] Calculate Top 15s

6. **Data Transformation Cells**:
   - [ ] Prepare for Power BI
   - [ ] Create dimension tables
   - [ ] Create fact tables

7. **Export Cells**:
   - [ ] Export to CSV
   - [ ] Export to Excel
   - [ ] Export metadata

8. **Validation Cells**:
   - [ ] Run quality checks
   - [ ] Display summary statistics
   - [ ] Display sample data

---

## 📦 11. DEPENDENCIES & REQUIREMENTS

### 11.1 Python Packages
- [ ] `pandas>=1.5.0`
- [ ] `numpy>=1.23.0`
- [ ] `openpyxl>=3.0.0`
- [ ] `jupyter` or `jupyterlab`
- [ ] `ipython` (for notebook execution)

### 11.2 Data Files Required
- [ ] Championship Reports (Excel files)
- [ ] Raw player stats (Excel files)
- [ ] Historical data (Excel/CSV files)
- [ ] Team stats (Excel files)
- [ ] Configuration JSON files

### 11.3 File Structure Assumptions
- [ ] Document expected directory structure
- [ ] Document expected file naming conventions
- [ ] Document expected sheet names
- [ ] Document expected column names

---

## 🎨 12. POWER BI SPECIFIC CONSIDERATIONS

### 12.1 Data Model Requirements
- [ ] Star schema design (fact + dimensions)
- [ ] Proper relationships between tables
- [ ] Unique keys for each dimension
- [ ] Date tables (if time-series analysis)

### 12.2 Performance Optimization
- [ ] Minimize row count (filter early)
- [ ] Use appropriate data types
- [ ] Remove unnecessary columns
- [ ] Aggregate where possible

### 12.3 Visualization Readiness
- [ ] Categorical columns for filters
- [ ] Numeric columns for measures
- [ ] Hierarchical columns (Conference → Team → Player)
- [ ] Calculated columns vs measures considerations

---

## ✅ 13. VALIDATION CHECKLIST

Before sending to colleague, verify:
- [ ] All imports work
- [ ] All paths are configurable
- [ ] All data loads successfully
- [ ] All calculations produce expected results
- [ ] All exports generate correctly
- [ ] Data types are correct
- [ ] No hardcoded paths (use relative or configurable)
- [ ] Error handling is in place
- [ ] Comments explain complex logic
- [ ] Sample outputs are included
- [ ] Data dictionary is included

---

## 📋 14. EXAMPLE OUTPUT STRUCTURE

### 14.1 Main Player Dataset (CSV/Excel)
```
Columns:
- Player_ID (or Player_Name)
- Team
- Conference
- Position_Profile
- Season
- Total_Score
- Conference_Grade
- Power_Five_Grade
- Consistency_Score
- Metrics_Above_Avg
- Metrics_Below_Avg
- Metrics_At_Avg
- Consistency_Pct
- Style_Fits_Count
- Top_15s_Count
- Previous_Score
- Change_From_Previous
- Total_Minutes
- Pct_Of_Team_Minutes
- Seasons_Played
- [All position-specific metrics]
```

### 14.2 Dimension Tables
- `dim_players.csv`
- `dim_teams.csv`
- `dim_conferences.csv`
- `dim_position_profiles.csv`
- `dim_metrics.csv`

### 14.3 Fact Tables
- `fact_player_performance.csv` (detailed metrics)
- `fact_player_summary.csv` (aggregated scores)

---

## 🔗 15. INTEGRATION POINTS

### 15.1 Power BI Import
- [ ] Document which tables to import
- [ ] Document relationship setup
- [ ] Document refresh schedule
- [ ] Document data source credentials (if needed)

### 15.2 Update Process
- [ ] Document how to run notebook
- [ ] Document when to run (after data updates)
- [ ] Document output location
- [ ] Document Power BI refresh process

---

## 📞 16. COMMUNICATION NOTES

### 16.1 For Your Colleague
- [ ] Explain data sources
- [ ] Explain calculation logic
- [ ] Explain update frequency
- [ ] Provide sample queries
- [ ] Provide troubleshooting guide

### 16.2 Questions to Ask
- [ ] What format does Power BI prefer? (CSV, Excel, Parquet, Database)
- [ ] Do they need historical data or just current?
- [ ] What level of detail? (Player-level, aggregated, both)
- [ ] Any specific metrics they want to prioritize?
- [ ] Any filters they want pre-applied?

---

## 📝 SUMMARY

**Critical Components:**
1. ✅ Data loading from all sources
2. ✅ All calculation functions
3. ✅ Data merging and cleaning
4. ✅ Power BI export format
5. ✅ Dimension and fact table creation
6. ✅ Data validation
7. ✅ Documentation

**Nice to Have:**
- Visualization examples
- Sample Power BI queries
- Automated refresh scripts
- Error logging
- Performance monitoring

---

**Next Steps:**
1. Create notebook structure
2. Add all functions from existing scripts
3. Test with sample data
4. Generate sample outputs
5. Document everything
6. Send to colleague for review


