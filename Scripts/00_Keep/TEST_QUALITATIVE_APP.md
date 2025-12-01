# Testing the Qualitative Capture App

## Prerequisites

### 1. Install Required Packages

```bash
pip3 install streamlit pandas openpyxl
```

Or if you prefer to install in user space:

```bash
pip3 install --user streamlit pandas openpyxl
```

### 2. Verify Installation

```bash
streamlit --version
python3 -c "import pandas; import openpyxl; print('All packages installed!')"
```

---

## Running the App

### Step 1: Navigate to the Script Directory

```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"
```

### Step 2: Run the Streamlit App

```bash
streamlit run qualitative_capture_app.py
```

**Expected Output**:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

The app should automatically open in your default web browser. If not, copy the Local URL and paste it into your browser.

---

## Testing Checklist

### ✅ Test 1: App Loads Successfully

**What to check**:
- [ ] App opens in browser
- [ ] Title shows "⚽ Portland Thorns - Call Log"
- [ ] Sidebar navigation is visible
- [ ] "Log New Call" page is displayed by default

**If it fails**:
- Check terminal for error messages
- Verify all packages are installed
- Check that the shortlist file exists at the expected path

---

### ✅ Test 2: Player Database Loading

**What to check**:
- [ ] Player search box appears
- [ ] Player dropdown shows player names (may take a moment to load)
- [ ] Can search for players by typing
- [ ] Player info displays when selected (Team, Position, Score)

**Test steps**:
1. Type a player name in the search box
2. Select a player from the dropdown
3. Verify player info appears below

**If it fails**:
- Check that `Portland Thorns 2025 Shortlist.xlsx` exists
- Verify the file has sheets with "Player" column
- Check terminal for error messages

---

### ✅ Test 3: Log a Test Call

**Test steps**:
1. Fill out the form with test data:
   - **Call Date**: Today's date (default)
   - **Call Type**: Select "Player Call"
   - **Duration**: Enter 30 minutes
   - **Player Name**: Select any player from dropdown
   - **Participants**: Enter "Mike, Test Player"
   - **Call Notes**: Enter "Test call for app validation"

2. **Player Assessment** (set all sliders to 7):
   - Communication Skills: 7
   - Maturity: 7
   - Coachability: 7
   - Leadership Potential: 7
   - Work Ethic: 7
   - Confidence Level: 7
   - Team Fit: 7
   - Overall Rating: 7

3. **Personality Traits**: Select 2-3 traits

4. **Agent Assessment**: Set all to 7

5. **Key Talking Points**:
   - Interest Level: Select "High"
   - Timeline: Enter "Available after season"
   - Key Talking Points: Enter "Test notes"

6. **Recommendation**: Select "Yes"

7. **Summary Notes**: Enter "This is a test entry"

8. Click **"💾 Save Call Log"** button

**What to check**:
- [ ] Success message appears: "✅ Call log saved for [Player Name]!"
- [ ] Confetti animation appears (balloons)
- [ ] Form can be filled out again for another call

**If it fails**:
- Check terminal for error messages
- Verify `Qualitative_Data/` folder was created
- Check file permissions

---

### ✅ Test 4: Verify Data Saved

**Test steps**:
1. Check that file was created:
   ```bash
   ls -lh "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Qualitative_Data/call_log.csv"
   ```

2. View the file:
   ```bash
   cat "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Qualitative_Data/call_log.csv"
   ```

**What to check**:
- [ ] CSV file exists
- [ ] Contains your test data
- [ ] All fields are populated correctly

---

### ✅ Test 5: View Call History

**Test steps**:
1. Click "View Call History" in sidebar
2. Verify your test call appears in the table

**What to check**:
- [ ] Table displays call data
- [ ] All columns are visible
- [ ] Data matches what you entered

**Test filters**:
- [ ] Filter by Player (select your test player)
- [ ] Filter by Recommendation (select "Yes")
- [ ] Verify filtered results

**Test download**:
- [ ] Click "📥 Download Filtered Data (CSV)"
- [ ] Verify CSV file downloads
- [ ] Open downloaded file and verify data

---

### ✅ Test 6: Player Summary

**Test steps**:
1. Click "Player Summary" in sidebar
2. Select your test player from dropdown

**What to check**:
- [ ] Summary metrics display:
  - Total Calls: 1
  - Avg Overall Rating: 7.0/10
  - Latest Recommendation: Yes
  - Last Call: Today's date
- [ ] Bar chart shows average ratings
- [ ] All calls table displays your test call

---

### ✅ Test 7: Export Data

**Test steps**:
1. Click "Export Data" in sidebar
2. Verify summary statistics display:
   - Total Calls Logged: 1
   - Unique Players: 1
   - Average Overall Rating: 7.00/10

**Test downloads**:
- [ ] Click "📥 Download Full Call Log (CSV)"
- [ ] Verify CSV downloads correctly
- [ ] Click "📥 Download Full Call Log (Excel)"
- [ ] Verify Excel file downloads (may take a moment)
- [ ] Open both files and verify data matches

**If Excel download fails**:
- Verify `openpyxl` is installed: `pip3 install openpyxl`
- Check terminal for error messages

---

### ✅ Test 8: Multiple Calls

**Test steps**:
1. Log 2-3 more test calls with different:
   - Players
   - Ratings
   - Recommendations
   - Dates

**What to check**:
- [ ] All calls save successfully
- [ ] Call History shows all calls
- [ ] Player Summary aggregates correctly
- [ ] Export includes all data

---

### ✅ Test 9: Form Validation

**Test steps**:
1. Try to submit form without selecting a player
2. Click "Save Call Log"

**What to check**:
- [ ] Error message appears: "Please select a player name"
- [ ] Form does not submit
- [ ] Data is not saved

---

### ✅ Test 10: Search Functionality

**Test steps**:
1. Go to "Log New Call"
2. Type a partial player name in search box
3. Verify dropdown filters to matching players

**What to check**:
- [ ] Search filters players correctly
- [ ] Case-insensitive search works
- [ ] Can select filtered player

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**:
```bash
pip3 install streamlit
```

### Issue: "FileNotFoundError: Portland Thorns 2025 Shortlist.xlsx"

**Solution**:
- Verify the file exists at the expected path
- Update `PLAYER_DB_FILE` path in the script if needed

### Issue: "Permission denied" when saving CSV

**Solution**:
- Check folder permissions:
  ```bash
  ls -ld "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Qualitative_Data"
  ```
- Create folder manually if needed:
  ```bash
  mkdir -p "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Qualitative_Data"
  ```

### Issue: App won't start / browser won't open

**Solution**:
- Check terminal for the Local URL
- Manually open browser and paste URL
- Check firewall settings

### Issue: Player dropdown is empty

**Solution**:
- Verify shortlist file exists and has data
- Check that sheets have "Player" column
- Look for error messages in terminal
- Try refreshing the page (Streamlit auto-reloads)

### Issue: Excel download doesn't work

**Solution**:
```bash
pip3 install openpyxl
```

---

## Performance Testing

### Test with Large Dataset

1. Log 50+ test calls (or use script to generate test data)
2. Test:
   - Loading speed
   - Filtering speed
   - Export speed
   - Player summary calculation speed

**Expected**: Should handle 100+ calls without issues

---

## User Acceptance Testing

### Real-World Scenario Test

1. **Simulate a real call**:
   - Use actual player name from shortlist
   - Fill out all fields realistically
   - Include notes, red flags, action items

2. **Test workflow**:
   - Log call → View history → Check summary → Export data

3. **Verify usability**:
   - Is the form intuitive?
   - Are all fields accessible?
   - Is data easy to find later?
   - Can you export for sharing?

---

## Next Steps After Testing

Once testing is complete:

1. **Fix any bugs** found during testing
2. **Customize fields** if needed (add/remove fields)
3. **Train Mike** on using the app
4. **Set up backup** system for data
5. **Document** any customizations or workflows

---

## Quick Test Script

Run this to quickly verify everything works:

```bash
# Install packages
pip3 install streamlit pandas openpyxl

# Navigate to script
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Scripts/00_Keep"

# Run app
streamlit run qualitative_capture_app.py
```

Then in the browser:
1. Select a player
2. Fill out minimum required fields
3. Save
4. Check "View Call History"
5. Verify data appears

**If all 5 steps work, the app is ready to use!** ✅

---

## Support

If you encounter issues:
1. Check terminal output for error messages
2. Verify all prerequisites are met
3. Check file paths and permissions
4. Review this testing guide

