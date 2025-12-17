"""
Check existing Excel file for missing metrics and generate a report.
This helps identify which columns need to be added to match the JSON requirements.
"""

import json
import pandas as pd
from pathlib import Path

def load_metrics_config():
    """Load metrics from JSON config file."""
    config_path = Path(__file__).parent / "radar_chart_metrics_short.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading JSON config: {e}")
        return {}

def get_all_metrics(metrics_config):
    """Get all unique metrics across all positions."""
    all_metrics = set()
    for position, metrics in metrics_config.items():
        all_metrics.update(metrics)
    return sorted(list(all_metrics))

def check_excel_file(excel_path):
    """Check Excel file for missing metrics."""
    
    # Load metrics config
    metrics_config = load_metrics_config()
    if not metrics_config:
        print("❌ Could not load metrics config. Exiting.")
        return
    
    # Get all required metrics
    all_required_metrics = get_all_metrics(metrics_config)
    
    print(f"📊 Checking Excel file: {excel_path}")
    print()
    
    # Try to read Excel file
    try:
        # Try different header rows
        df_dict = pd.read_excel(excel_path, sheet_name=None, header=None)
        
        # Find the sheet with player data
        all_columns = set()
        for sheet_name, sheet_df in df_dict.items():
            # Skip non-data sheets
            if sheet_name.startswith('Sheet') or 'Summary' in sheet_name or 'Notes' in sheet_name:
                continue
            
            # Check all rows for column headers
            for header_row in [0, 1, 2]:
                try:
                    test_df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row)
                    if 'Player' in test_df.columns:
                        all_columns.update(test_df.columns)
                        print(f"✅ Found player data in sheet: '{sheet_name}'")
                        break
                except:
                    continue
        
        if not all_columns:
            print("❌ Could not find player data in Excel file.")
            return
        
        # Convert to list and clean
        existing_columns = [str(col).strip() for col in all_columns if pd.notna(col)]
        
        print(f"📋 Found {len(existing_columns)} columns in Excel file")
        print()
        
        # Check which metrics are missing
        missing_metrics = []
        found_metrics = []
        
        for metric in all_required_metrics:
            # Check for exact match
            if metric in existing_columns:
                found_metrics.append(metric)
            else:
                # Check for case-insensitive match
                metric_lower = metric.lower()
                found = False
                for col in existing_columns:
                    if col.lower() == metric_lower:
                        found_metrics.append(f"{metric} (found as: {col})")
                        found = True
                        break
                
                if not found:
                    missing_metrics.append(metric)
        
        # Print results
        print("=" * 80)
        print("📊 METRIC CHECK RESULTS")
        print("=" * 80)
        print()
        
        print(f"✅ Found metrics: {len(found_metrics)}/{len(all_required_metrics)}")
        if found_metrics:
            for metric in found_metrics:
                print(f"   ✓ {metric}")
        print()
        
        print(f"❌ Missing metrics: {len(missing_metrics)}/{len(all_required_metrics)}")
        if missing_metrics:
            print("   These columns need to be added to your Excel file:")
            for metric in missing_metrics:
                print(f"   ✗ {metric}")
        print()
        
        # Show position-specific breakdown
        print("=" * 80)
        print("📋 POSITION-SPECIFIC BREAKDOWN")
        print("=" * 80)
        print()
        
        for position, required_metrics in metrics_config.items():
            print(f"**{position}** ({len(required_metrics)} metrics required):")
            position_found = []
            position_missing = []
            
            for metric in required_metrics:
                if metric in existing_columns:
                    position_found.append(metric)
                else:
                    # Check case-insensitive
                    metric_lower = metric.lower()
                    found = False
                    for col in existing_columns:
                        if col.lower() == metric_lower:
                            position_found.append(f"{metric} (as: {col})")
                            found = True
                            break
                    if not found:
                        position_missing.append(metric)
            
            print(f"   ✅ Found: {len(position_found)}/{len(required_metrics)}")
            if position_found:
                for m in position_found:
                    print(f"      ✓ {m}")
            
            print(f"   ❌ Missing: {len(position_missing)}/{len(required_metrics)}")
            if position_missing:
                for m in position_missing:
                    print(f"      ✗ {m}")
            print()
        
        # Generate recommendations
        print("=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        print()
        
        if missing_metrics:
            print("1. Add the missing metric columns to your Excel file")
            print("2. Use the template file generated by generate_metrics_template.py as a reference")
            print("3. Ensure column names match exactly (case-sensitive)")
            print("4. Fill in metric values for all players")
        else:
            print("✅ All required metrics are present in your Excel file!")
            print("   If metrics still aren't showing in the app, check:")
            print("   - Column names match exactly (including spaces and punctuation)")
            print("   - Values are numeric (not text)")
            print("   - Players have valid data (not all NaN)")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    # Path to existing Excel file
    excel_path = Path("/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Portland Thorns/Data/Advanced Search/Portland Thorns 2025 Long Shortlist.xlsx")
    
    if not excel_path.exists():
        print(f"❌ Excel file not found: {excel_path}")
        print("   Please update the path in the script or provide the correct path.")
        return
    
    check_excel_file(excel_path)

if __name__ == "__main__":
    main()

