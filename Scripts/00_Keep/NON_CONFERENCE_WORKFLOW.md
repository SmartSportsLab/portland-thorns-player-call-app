# Non-Conference Game Data Workflow

## Overview

This workflow handles exporting, merging, and processing both **inter-conference** (conference games) and **non-conference** games separately, then creating combined reports.

## Data Types

1. **Inter-Conference Games**: Conference team vs. Conference team (e.g., SEC vs. SEC)
   - Already exported in `Exports/By Position/`
   - Files: `[Conference] [Position] 2025.xlsx`

2. **Non-Conference Games**: Conference team vs. Non-conference team (e.g., SEC vs. ACC)
   - Must be exported team-by-team (too many players for single export)
   - Files: Individual team Excel files

3. **All Games**: Combined inter-conference + non-conference
   - Created by merging the above two types

## Step-by-Step Workflow

### Step 1: Export Non-Conference Team Data

For each team in the conference:
1. In Wyscout Advanced Search:
   - Select the team
   - Select position profile
   - Filter for **non-conference games only**
   - Export to Excel

2. Save files to:
   ```
   Exports/Non-Conference/[Conference]/[Position]/
   ```
   
   Example:
   ```
   Exports/Non-Conference/SEC/Attacking Midfielder/Tennessee Vols.xlsx
   Exports/Non-Conference/SEC/Attacking Midfielder/LSU Tigers.xlsx
   ```

### Step 2: Merge Non-Conference Team Files

Run the merge script for each position:

```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"

# For each position:
python merge_non_conference_teams.py SEC "Attacking Midfielder"
python merge_non_conference_teams.py SEC "Center Back"
python merge_non_conference_teams.py SEC "Centre Midfielder"
python merge_non_conference_teams.py SEC "Winger"
```

**Output**: `Exports/Non-Conference/[Conference]/[Position Prefix] [Conference] 2025 Non-Conference.xlsx`

### Step 3: Merge All Game Types

Combine non-conference and inter-conference files:

```bash
python merge_all_game_types.py SEC "Attacking Midfielder"
python merge_all_game_types.py SEC "Center Back"
python merge_all_game_types.py SEC "Centre Midfielder"
python merge_all_game_types.py SEC "Winger"
```

**Output** (in `Exports/Merged/[Conference]/`):
- `[Position] [Conference] 2025 Inter-Conference Only.xlsx`
- `[Position] [Conference] 2025 Non-Conference Only.xlsx`
- `[Position] [Conference] 2025 All Games.xlsx`

### Step 4: Process Each Game Type

Run the processing script for each game type:

```bash
# Process All Games
python process_any_position.py "Attacking Midfielder" --game-type all

# Process Inter-Conference Only
python process_any_position.py "Attacking Midfielder" --game-type inter-conference

# Process Non-Conference Only
python process_any_position.py "Attacking Midfielder" --game-type non-conference
```

## Directory Structure

```
Exports/
├── By Position/                          # Inter-conference exports (existing)
│   ├── SEC AM Advanced Playmaker 2025.xlsx
│   └── ...
├── Non-Conference/                       # Non-conference team exports
│   └── [Conference]/
│       ├── [Position]/                   # Individual team files
│       │   ├── Team 1.xlsx
│       │   └── Team 2.xlsx
│       └── [Position Prefix] [Conference] 2025 Non-Conference.xlsx  # Merged
└── Merged/                               # Final merged files
    └── [Conference]/
        ├── [Position] [Conference] 2025 All Games.xlsx
        ├── [Position] [Conference] 2025 Inter-Conference Only.xlsx
        └── [Position] [Conference] 2025 Non-Conference Only.xlsx
```

## Notes

- **Player Aggregation**: When a player appears in both inter-conference and non-conference files, their stats need to be aggregated (summed for counts, averaged for rates)
- **Duplicates**: The merge scripts preserve all entries but flag duplicates with `Appears_in_Both` column
- **Processing**: The processing scripts will need to handle the `Game_Type` column and aggregate stats appropriately

## Example Workflow for SEC

```bash
# 1. After exporting all SEC team non-conference files for Attacking Midfielder

# 2. Merge team files
python merge_non_conference_teams.py SEC "Attacking Midfielder"

# 3. Merge with inter-conference
python merge_all_game_types.py SEC "Attacking Midfielder"

# 4. Process all three game types
python process_any_position.py "Attacking Midfielder" --game-type all
python process_any_position.py "Attacking Midfielder" --game-type inter-conference
python process_any_position.py "Attacking Midfielder" --game-type non-conference
```



















