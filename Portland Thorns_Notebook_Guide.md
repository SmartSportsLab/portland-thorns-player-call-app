# Power BI Data Alignment Notebook - User Guide

## 📋 Overview

This notebook processes all player data from championship reports and prepares it for Power BI import. It loads data from Excel files, cleans and standardizes it, creates a star schema structure (fact and dimension tables), and exports everything in Power BI-friendly formats.

**Purpose**: Align all player scouting data into a format that Power BI can easily consume and visualize.

---

## 🎯 What This Notebook Does

1. **Loads Data**: Reads all championship reports (Excel files) across 5 conferences and 4 position profiles
2. **Enriches Data**: Merges report data with raw player statistics
3. **Cleans Data**: Standardizes column names, fills missing values
4. **Creates Star Schema**: Builds dimension tables (Players, Teams, Conferences, Positions) and fact tables (Performance data)
5. **Exports**: Saves everything as CSV and Excel files ready for Power BI import

---

## 📁 Prerequisites

### Required Files
- Championship Reports (Excel files) in `Championship Reports/` folder:
  - `Portland Thorns 2025 ACC Championship Scouting Report.xlsx`
  - `Portland Thorns 2025 SEC Championship Scouting Report.xlsx`
  - `Portland Thorns 2025 BIG10 Championship Scouting Report.xlsx`
  - `Portland Thorns 2025 BIG12 Championship Scouting Report.xlsx`
  - `Portland Thorns 2025 IVY Championship Scouting Report.xlsx`

- Raw Player Stats in `Exports/Players Stats By Position/` folder

- Configuration file: `Scripts/00_Keep/position_metrics_config.json`

### Required Python Packages
```bash
pip install pandas numpy openpyxl jupyter
```

---

## 📖 Step-by-Step Guide

### Step 1: Setup & Configuration

#### Cell 1: Import Libraries
**What it does**: Imports all required Python libraries
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `pathlib` - File path handling
- `openpyxl` - Excel file reading
- `json` - Configuration loading

**Expected output**: `✅ Libraries imported successfully`

**If it fails**: Install missing packages with `pip install [package_name]`

---

#### Cell 2: Path Configuration
**What it does**: Sets up all file paths and directories

**⚠️ IMPORTANT**: Update the `BASE_DIR` path to match your system!

```python
BASE_DIR = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search")
```

**What gets created**:
- Input directories are defined (championship reports, raw stats, etc.)
- Output directory `Power_BI_Exports/` is created automatically

**Expected output**: 
```
📁 Base Directory: [your path]
📁 Output Directory: [your path]/Power_BI_Exports
```

**If it fails**: 
- Check that the path exists
- Ensure you have write permissions
- Update `BASE_DIR` to match your system

---

#### Cell 3: Constants & Mappings
**What it does**: 
- Defines position profile mappings (e.g., 'Hybrid CB' → 'Center Back')
- Sets up conference list (ACC, SEC, BIG10, BIG12, IVY)
- Loads position metrics configuration from JSON file

**Expected output**: `✅ Configuration loaded`

**If it fails**:
- Check that `position_metrics_config.json` exists
- Verify the file path is correct
- Check JSON file format is valid

---

### Step 2: Data Loading Functions

#### Cell 4: Define `load_players_from_report()` Function
**What it does**: 
- Reads Excel files with merged headers (row 1 + row 2)
- Handles complex header combinations (e.g., "Goals per 90")
- Enriches data by merging with raw player stats
- Matches players by name and team

**Key features**:
- Handles merged cells in Excel headers
- Fuzzy matching for player names
- Fallback matching if initial merge fails
- Fills missing data appropriately

**Expected output**: `✅ Data loading function defined`

**No action needed** - this just defines the function

---

#### Cell 5: Define `load_all_players_from_reports()` Function
**What it does**: 
- Loops through all conferences
- Loads all position profiles from each conference report
- Combines all players into one DataFrame

**Expected output**: `✅ Load all players function defined`

**No action needed** - this just defines the function

---

### Step 3: Load All Data

#### Cell 6: Execute Data Loading
**What it does**: Actually runs the data loading functions

**What happens**:
1. Loops through each conference (ACC, SEC, BIG10, BIG12, IVY)
2. For each conference, loads 4 position profiles:
   - Hybrid CB
   - DM Box-To-Box
   - AM Advanced Playmaker
   - Right Touchline Winger
3. Combines everything into `df_all_players`

**Expected output**:
```
📊 Loading ACC...
  ✅ Hybrid CB: 45 players
  ✅ DM Box-To-Box: 52 players
  ✅ AM Advanced Playmaker: 38 players
  ✅ Right Touchline Winger: 41 players

📊 Loading SEC...
  ...

✅ Total players loaded: 850
```

**If it fails**:
- Check that championship report files exist
- Verify file names match exactly (case-sensitive)
- Check that sheets exist in Excel files (position profile names must match)
- Look for error messages indicating which file/sheet failed

**Troubleshooting**:
- If a conference is missing: Check file name spelling
- If a position profile is missing: Verify sheet name in Excel file
- If players are missing: Check raw stats files exist in `Exports/Players Stats By Position/`

---

### Step 4: Data Cleaning & Standardization

#### Cell 7: Clean and Standardize Data
**What it does**:
1. **Standardizes column names**: 
   - Replaces spaces with underscores
   - Removes special characters
   - Makes names Power BI-friendly (e.g., "Goals per 90" → "Goals_per_90")

2. **Fills missing values**:
   - Numeric columns: Fill with 0
   - String columns: Fill with empty string

**Why this matters**: Power BI works better with standardized column names and no null values

**Expected output**:
```
✅ Data cleaned and standardized
   Columns: 127
```

**If it fails**:
- Usually means `df_all_players` is empty
- Go back and check data loading step
- Verify championship reports exist and have data

---

### Step 5: Create Dimension Tables

#### Cell 8: Build Dimension Tables
**What it does**: Creates lookup/reference tables for Power BI star schema

**Creates 4 dimension tables**:

1. **dim_players**: 
   - Player_ID (unique identifier)
   - Player (name)
   - Team
   - Conference
   - Position_Profile

2. **dim_teams**:
   - Team_ID (unique identifier)
   - Team (name)
   - Conference

3. **dim_conferences**:
   - Conference_ID (unique identifier)
   - Conference (code: ACC, SEC, etc.)
   - Conference_Name (full name: Big Ten, Big 12, etc.)

4. **dim_positions**:
   - Position_Profile_ID (unique identifier)
   - Position_Profile (display name)
   - Internal_Position (internal name)

**Why dimension tables?**: 
- Reduces data duplication
- Makes Power BI relationships easier
- Improves query performance
- Enables better filtering and grouping

**Expected output**:
```
✅ Dimension tables created
   Players: 850 rows
   Teams: 89 rows
   Conferences: 5 rows
   Positions: 4 rows
```

**If it fails**:
- Check that `df_cleaned` exists and has data
- Verify required columns exist: Player, Team, Conference, Position_Profile

---

### Step 6: Create Fact Tables

#### Cell 9: Build Fact Tables
**What it does**: Creates fact tables with actual performance data

**Creates 2 fact tables**:

1. **fact_player_performance**: 
   - Contains ALL columns from cleaned data
   - Includes all performance metrics
   - Links to dimension tables via IDs
   - Use for detailed analysis

2. **fact_player_summary**:
   - Contains only key columns:
     - IDs (Player_ID, Team_ID, etc.)
     - Base info (Player, Team, Conference, Position)
     - Scores (Total Score, Grades, Consistency Score)
     - Style Fits, Top 15s
     - Minutes, Seasons, Progression
   - Use for high-level analysis

**What happens**:
1. Merges cleaned data with dimension tables to get IDs
2. Creates full performance table
3. Extracts key columns for summary table

**Expected output**:
```
✅ Fact tables created
   Player Performance: 850 rows, 127 columns
   Player Summary: 850 rows, 25 columns
```

**If it fails**:
- Check that dimension tables were created successfully
- Verify merge keys exist in both tables
- Check for column name mismatches after standardization

---

### Step 7: Export to Power BI Formats

#### Cell 10: Export Files
**What it does**: Saves all tables as CSV and Excel files

**Exports**:
- **CSV files** (one per table):
  - `dim_players.csv`
  - `dim_teams.csv`
  - `dim_conferences.csv`
  - `dim_positions.csv`
  - `fact_player_performance.csv`
  - `fact_player_summary.csv`

- **Excel file** (all tables in one file):
  - `Power_BI_Data.xlsx` with multiple sheets

**File location**: `Power_BI_Exports/` folder

**Expected output**:
```
✅ Dimension tables exported to CSV
✅ Fact table (performance) exported: 850 rows
✅ Fact table (summary) exported: 850 rows

✅ All data exported to: [path]/Power_BI_Exports
   - CSV files for each table
   - Excel file: Power_BI_Data.xlsx (all tables)
```

**If it fails**:
- Check write permissions on output directory
- Ensure output directory exists
- Check disk space
- Look for specific error message

---

### Step 8: Data Summary & Validation

#### Cell 11: Display Summary Statistics
**What it does**: Shows overview of loaded data

**Shows**:
- Total players loaded
- Unique players count
- Number of conferences
- Number of position profiles
- Players by conference (breakdown)
- Players by position (breakdown)
- Missing values check

**Expected output**:
```
======================================================================
DATA SUMMARY
======================================================================

📊 Total Players: 850
📊 Unique Players: 850
📊 Conferences: 5
📊 Position Profiles: 4

📊 Players by Conference:
ACC     180
SEC     175
BIG10   185
BIG12   170
IVY     140

📊 Players by Position:
Hybrid CB                 215
DM Box-To-Box             220
AM Advanced Playmaker      195
Right Touchline Winger     220

📊 Missing Values Check:
   Player: 0 missing (0.0%)
   Team: 0 missing (0.0%)
   Conference: 0 missing (0.0%)
   Position_Profile: 0 missing (0.0%)

======================================================================
```

**Use this to verify**: 
- Data loaded correctly
- No major data quality issues
- Expected counts match reality

---

#### Cell 12: Display Sample Data
**What it does**: Shows first 5 rows of cleaned data

**Use this to**: 
- Verify data looks correct
- Check column names
- Spot any obvious issues

**Expected output**: Table showing sample rows

---

### Step 9: Column Documentation

#### Cell 13: Generate Column Documentation
**What it does**: Creates a documentation file describing all columns

**Creates**:
- `column_documentation.csv`
- `column_documentation.xlsx`

**Contains**:
- Column name
- Data type
- Non-null count
- Null count
- Unique values (for text columns)
- Min/Max/Mean (for numeric columns)

**Expected output**:
```
✅ Column documentation exported
   File: [path]/column_documentation.csv
```

**Use this to**: 
- Understand what each column means
- Check data quality
- Plan Power BI visualizations

---

### Step 10: Power BI Import Instructions

#### Cell 14: Instructions (Markdown)
**What it does**: Provides step-by-step guide for importing into Power BI

**No code execution** - just documentation

---

## 🔄 Running the Notebook

### First Time Setup

1. **Open Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```
   Or use JupyterLab:
   ```bash
   jupyter lab
   ```

2. **Navigate to the notebook file**:
   - `Power_BI_Data_Alignment.ipynb`

3. **Update the BASE_DIR path** (Cell 2):
   - Change to match your system path

4. **Run all cells**:
   - Menu: `Cell` → `Run All`
   - Or: `Kernel` → `Restart & Run All`

### Regular Use

1. **Open notebook**
2. **Run all cells** (or run cells sequentially)
3. **Check outputs** for any errors
4. **Verify exports** in `Power_BI_Exports/` folder
5. **Import into Power BI** (see instructions below)

---

## 📊 Power BI Import Process

### Option 1: Import Excel File (Recommended)

1. **Open Power BI Desktop**

2. **Get Data**:
   - Click `Get Data` → `Excel`
   - Navigate to `Power_BI_Exports/Power_BI_Data.xlsx`
   - Click `Open`

3. **Select Sheets**:
   - Check all sheets:
     - `dim_players`
     - `dim_teams`
     - `dim_conferences`
     - `dim_positions`
     - `fact_player_performance`
     - `fact_player_summary`
   - Click `Load`

4. **Set Up Relationships**:
   - Go to `Model` view
   - Create relationships:
     - `fact_player_performance[Player_ID]` → `dim_players[Player_ID]`
     - `fact_player_performance[Team_ID]` → `dim_teams[Team_ID]`
     - `fact_player_performance[Conference_ID]` → `dim_conferences[Conference_ID]`
     - `fact_player_performance[Position_Profile_ID]` → `dim_positions[Position_Profile_ID]`
     - Same for `fact_player_summary`

### Option 2: Import CSV Files

1. **Get Data** → `Text/CSV`
2. **Import each CSV file**:
   - `dim_players.csv`
   - `dim_teams.csv`
   - `dim_conferences.csv`
   - `dim_positions.csv`
   - `fact_player_performance.csv`
   - `fact_player_summary.csv`
3. **Set up relationships** (same as above)

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: "File not found" errors
**Solution**: 
- Check `BASE_DIR` path is correct
- Verify championship report files exist
- Check file names match exactly (case-sensitive)

#### Issue: "No data loaded"
**Solution**:
- Check Excel files have data
- Verify sheet names match position profiles exactly
- Check raw stats files exist

#### Issue: "Merge failed" warnings
**Solution**:
- This is usually okay - some players may not have raw stats
- Check if many players are affected
- Verify player name matching logic

#### Issue: "Column not found" errors
**Solution**:
- Check column names after standardization
- Verify required columns exist in source data
- Check for typos in column references

#### Issue: Export fails
**Solution**:
- Check write permissions
- Ensure output directory exists
- Check disk space
- Close Excel file if it's open

#### Issue: Power BI import fails
**Solution**:
- Check file paths are accessible
- Verify CSV files are not corrupted
- Try importing Excel file instead
- Check Power BI version compatibility

---

## 📈 Next Steps After Import

### Create Measures

Example measures to create in Power BI:

1. **Average Total Score**:
   ```
   Avg Total Score = AVERAGE(fact_player_summary[Total_Score])
   ```

2. **Total Players**:
   ```
   Total Players = COUNTROWS(dim_players)
   ```

3. **Players by Conference**:
   ```
   Players by Conference = COUNTROWS(fact_player_summary)
   ```
   (Then group by Conference)

4. **Average Consistency Score**:
   ```
   Avg Consistency = AVERAGE(fact_player_summary[Consistency_Score])
   ```

### Create Visualizations

Suggested visualizations:
- **Bar chart**: Players by Conference
- **Bar chart**: Players by Position Profile
- **Scatter plot**: Total Score vs Consistency Score
- **Table**: Top players by Total Score
- **Card**: Total number of players
- **Card**: Average Total Score

---

## 🔄 Refresh Schedule

### Set Up Scheduled Refresh

1. **Publish to Power BI Service**:
   - File → Publish → Power BI
   - Sign in and select workspace

2. **Configure Data Source**:
   - Settings → Datasets → [Your Dataset]
   - Data Source Credentials → Edit
   - Set authentication method

3. **Set Refresh Schedule**:
   - Settings → Datasets → [Your Dataset]
   - Scheduled Refresh → Enable
   - Set frequency (daily, weekly, etc.)

### Manual Refresh

1. **In Power BI Desktop**:
   - Home → Refresh
   - Or: Right-click dataset → Refresh

2. **After updating data**:
   - Run notebook again
   - Refresh Power BI dataset

---

## 📝 Notes

### Data Updates

- **When to run**: After championship reports are updated
- **Frequency**: As needed (weekly, monthly, etc.)
- **Process**: Run notebook → Export files → Refresh Power BI

### File Locations

- **Input**: `Championship Reports/` folder
- **Output**: `Power_BI_Exports/` folder
- **Config**: `Scripts/00_Keep/position_metrics_config.json`

### Data Structure

- **Star Schema**: Fact tables (data) + Dimension tables (lookups)
- **Relationships**: One-to-many (dimensions → facts)
- **Keys**: ID columns link tables together

---

## ❓ Questions?

If you encounter issues:

1. **Check error messages** - they usually indicate the problem
2. **Verify file paths** - most issues are path-related
3. **Check data exists** - ensure source files have data
4. **Review outputs** - summary statistics help identify issues
5. **Check column names** - after standardization, names may differ

---

## 📞 Support

For questions or issues:
- Check this guide first
- Review error messages carefully
- Verify all prerequisites are met
- Check file paths and permissions

---

**Last Updated**: November 2024
**Notebook Version**: 1.0
**Compatible with**: Power BI Desktop (all versions)

