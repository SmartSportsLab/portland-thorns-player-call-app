# Changelog - Recent Features & Improvements

## UI/UX Enhancements

### Navigation & Layout
- **Button Relocation**: Moved "Save Draft" and "Refresh Form" buttons from main form to Navigation sidebar for better accessibility
- **Menu Reordering**: Moved "Video Analysis" to second position in the navigation dropdown menu
- **Tab Label Sizing**: Increased font size and weight of tab labels throughout the application for improved readability

### Call Log System
- **Column Management**:
  - Added "Clear all" option at the top of "Show/Hide Columns" toggle
  - Added "Select All" button for column visibility
  - Implemented "Save Preset" functionality allowing users to save custom column visibility configurations
  - Added "Load Preset" and "Delete Preset" options with persistent storage
  - Column presets are saved to `column_visibility_presets.json` and persist across sessions
- **Column Sorting & Reordering**:
  - When a column is sorted, it is automatically highlighted in Portland Thorns red (#8B0000)
  - Sorted column is automatically moved to the leftmost position
  - Added drag-and-drop functionality for manual column reordering
- **Form Labels**: Changed "Timeline" label to "Graduation Timeline" for clarity

### Calendar Integration
- **Follow-up Date Sync**: Added Google Calendar and Outlook Calendar sync functionality
  - When "Follow-up Needed" checkbox is selected, users can create calendar events directly
  - Deep linking support for both calendar platforms

### Cloud Storage
- **Google Drive Integration**: 
  - Added "💾 Save to Google Drive" checkbox at bottom of call log form
  - Integrated PyDrive2 for file upload and folder management
  - Automatic folder creation and file organization in Google Drive
  - Improved authentication flow with better error handling and setup instructions

## Video Analysis Enhancements

### Performance Assessment
- **Dynamic Performance Toggles**: Added 9 performance sliders to Video Analysis "Add Review" tab:
  - Technical Ability, Tactical Awareness, Decision Making, Physical Attributes
  - Work Rate, Communication, Leadership, Composure, Overall Video Rating
- **Real-time Score Calculation**: 
  - Total Score, Percentage, and Grade update dynamically as sliders are adjusted
  - Moved performance assessment section outside form for reactive updates
- **UI Cleanup**: Removed "Video Review Checklist" expander section

## Player Summary Page - Major Restructure

### New Section-Based Layout
- **Phone Call Section** (📞):
  - Section header with emoji
  - Summary metrics (4 columns): Total Calls, Avg Overall Rating, Overall Rank, Latest Recommendation
  - Average Ratings bar chart for call metrics
  - All Calls interactive HTML table with expandable cells
  - Call Review Details: Expandable sections for each call with full details including:
    - Performance metrics, call notes, preparation notes, summary notes
    - Red flags, action items, call recordings
  - Radar Chart: Player's call metrics vs. call log average

- **Video Analysis Section** (🎥):
  - Section header with emoji
  - Summary metrics (4 columns): Total Reviews, Avg Video Score, Avg Video Rating, Latest Recommendation
  - Average Ratings bar chart for video metrics
  - All Video Reviews table with key columns
  - Video Review Details: Expandable sections for each review with:
    - Performance metrics, key observations, strengths, weaknesses
    - Red flags, additional notes
  - Radar Chart: Player's video metrics vs. video analysis average

- **Shared Elements**:
  - PDF Download button moved to bottom as shared element
  - PDF export now includes both call log and video review data

### Data Integration
- **Video Reviews in Player Summary**: Added saved video reviews to Player Summary page
- **Enhanced PDF Export**: Updated PDF generation to include video review data and metrics
- **Combined Data Visualization**: Radar charts now properly combine data from both call logs and video reviews where applicable

## Technical Improvements

### Data Persistence
- **Column Preset Storage**: Implemented file-based persistence for column visibility presets
  - Presets saved to `column_visibility_presets.json` in Qualitative_Data directory
  - Automatic loading on app startup
  - Save/delete operations persist immediately

### Code Quality
- Fixed multiple indentation and scope issues
- Improved error handling for Google Drive authentication
- Enhanced data validation and empty state handling
- Better widget key management for Streamlit state resets

## Bug Fixes
- Fixed "Clear all" button functionality for column visibility checkboxes
- Resolved preset loading issues with proper state management
- Fixed radar chart display for players with only video reviews (no call logs)
- Corrected data scope issues for table generation
- Fixed NameError issues with `text_heavy_columns` and `table_data` variables

---

*Last Updated: Current Session*






