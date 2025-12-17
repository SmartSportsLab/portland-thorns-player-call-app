# PDF Export Process Documentation

This document explains how PDF exports work in the Streamlit application, including the technical implementation, code patterns, and how to add PDF export functionality to new features.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites & Setup](#prerequisites--setup)
3. [PDF Export Paths](#pdf-export-paths)
   - [Call Log PDF](#1-call-log-pdf)
   - [Player Summary PDF](#2-player-summary-pdf)
   - [Performance Metrics (Not Yet Implemented)](#3-performance-metrics-not-yet-implemented)
4. [Technical Implementation](#technical-implementation)
5. [Adding PDF Export to New Features](#adding-pdf-export-to-new-features)
6. [Code Patterns & Examples](#code-patterns--examples)

---

## Overview

The app uses **ReportLab** to generate PDFs programmatically. PDFs are created in memory using `BytesIO` buffers, then made available for download via Streamlit's `st.download_button()`.

**Key Libraries:**
- `reportlab` - PDF generation
- `matplotlib` - Chart/visualization creation
- `BytesIO` - In-memory file handling
- `PIL/Pillow` - Image handling for embedding charts

---

## Prerequisites & Setup

### 1. Install Required Libraries

```python
pip install reportlab pillow matplotlib
```

### 2. Import Statements

```python
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
```

### 3. Check PDF Availability

```python
PDF_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
```

---

## PDF Export Paths

### 1. Call Log PDF

**Location:** Log a Call page  
**Trigger:** User saves a call log entry  
**Function:** `generate_call_log_pdf(entry)`

#### Process Flow

1. **User Action:** User fills out call log form and clicks "Save Call Log"
2. **PDF Generation:** On save, `generate_call_log_pdf(entry)` is called
3. **PDF Creation:**
   - Creates `BytesIO` buffer in memory
   - Uses `SimpleDocTemplate` with letter size and reduced margins
   - Builds PDF with multiple sections
4. **Session State Storage:**
   ```python
   pdf_bytes = generate_call_log_pdf(new_entry)
   if pdf_bytes:
       st.session_state['pdf_download_data'] = pdf_bytes
       st.session_state['pdf_download_filename'] = pdf_filename
       st.session_state['show_pdf_download'] = True
   ```
5. **Download Button:** Appears outside the form for user to download

#### PDF Structure

The Call Log PDF includes:
- **Title:** "Call Log Report - {Player Name}"
- **Call Information:** Date, type, duration, team, conference, position, participants
- **Agent Assessment:** Agent name, relationship, scores, notes
- **Player Notes:** Free-form notes
- **Player Assessment:** Ratings (Communication, Maturity, Coachability, etc.)
- **Personality & Self Awareness:** How they carry themselves, view themselves, etc.
- **Key Talking Points:** Interest level, timeline, salary expectations, other opportunities
- **Red Flags & Assessment:** Severity, flags, recommendation, summary
- **Next Steps:** Follow-up needed, action items
- **Footer:** Call notes and creation timestamp

#### Code Pattern

```python
def generate_call_log_pdf(entry):
    """Generate PDF from call log entry using ReportLab."""
    if not PDF_AVAILABLE:
        return None
    
    try:
        # 1. Create PDF buffer in memory
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                              rightMargin=0.3*inch, leftMargin=0.3*inch,
                              topMargin=0.3*inch, bottomMargin=0.3*inch)
        
        # 2. Container for PDF elements
        elements = []
        
        # 3. Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=8,
        )
        # ... more styles
        
        # 4. Add content to elements list
        title = Paragraph(f"Call Log Report - {player_name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.05*inch))
        
        # Add tables, paragraphs, etc.
        # ...
        
        # 5. Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None
```

#### Usage in Streamlit

```python
# After saving call log
pdf_bytes = generate_call_log_pdf(new_entry)
if pdf_bytes:
    player_name_safe = new_entry['Player Name'].replace('/', '_')
    pdf_filename = f"Call_Log_{player_name_safe}_{datetime.now().strftime('%Y%m%d')}.pdf"
    st.session_state['pdf_download_data'] = pdf_bytes
    st.session_state['pdf_download_filename'] = pdf_filename
    st.session_state['show_pdf_download'] = True

# Download button (outside form)
if st.session_state.get('show_pdf_download', False):
    pdf_bytes = st.session_state.get('pdf_download_data')
    pdf_filename = st.session_state.get('pdf_download_filename', 'call_log.pdf')
    if pdf_bytes:
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True,
            key="pdf_download_btn"
        )
    st.session_state['show_pdf_download'] = False
```

---

### 2. Player Summary PDF

**Location:** Player Summaries page  
**Trigger:** User clicks "Download Player Summary PDF" button  
**Function:** `generate_player_summary_pdf()`

#### Process Flow

1. **Radar Chart Generation:** When viewing a player, radar charts are generated and saved to session state:
   ```python
   # Call radar chart
   call_radar_buffer = BytesIO()
   fig_pdf.savefig(call_radar_buffer, format='png', dpi=150, bbox_inches='tight')
   call_radar_buffer.seek(0)
   st.session_state['call_radar_chart'] = call_radar_buffer.getvalue()
   
   # Video radar chart (similar process)
   st.session_state['video_radar_chart'] = video_radar_buffer.getvalue()
   ```

2. **User Action:** User clicks "Download Player Summary PDF"
3. **PDF Generation:** `generate_player_summary_pdf()` is called with:
   - Player data
   - Call history DataFrame
   - Video reviews DataFrame
   - Radar chart image bytes (if available)
4. **PDF Creation:** Builds comprehensive PDF with embedded charts
5. **Download:** PDF bytes returned and displayed via download button

#### PDF Structure

The Player Summary PDF includes:
- **Title:** "Player Summary - {Player Name}"
- **Summary Metrics:** Total calls, rank, percentile, average rating, recommendation
- **Average Assessment Ratings:** Communication, Maturity, Coachability, etc.
- **Assessment Grade Distribution:** Count of each grade
- **Key Information:** Agent, interest level, salary expectations, red flags
- **Call History:** Table of all calls with dates, types, grades, recommendations
- **Video Reviews:** Summary, history, and latest review details (if available)
- **Radar Charts:** Separate pages for call and video radar charts (if available)

#### Embedding Charts in PDF

```python
# Add Radar Charts if available
if call_radar_chart_bytes:
    elements.append(PageBreak())  # New page for chart
    elements.append(Paragraph("Phone Call Performance Radar Chart", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Create Image from bytes
    call_radar_img = Image(BytesIO(call_radar_chart_bytes), width=5*inch, height=5*inch)
    elements.append(call_radar_img)
    elements.append(Spacer(1, 0.15*inch))
```

#### Saving Matplotlib Figures for PDF

```python
# Create figure with white background for PDF
fig_pdf = plt.figure(figsize=(6, 6))
ax_pdf = fig_pdf.add_subplot(111, projection='polar')
ax_pdf.set_facecolor('white')
fig_pdf.patch.set_facecolor('white')

# ... plot data with colors adjusted for white background ...

# Save to BytesIO buffer
radar_buffer = BytesIO()
fig_pdf.savefig(radar_buffer, format='png', dpi=150, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
radar_buffer.seek(0)
chart_bytes = radar_buffer.getvalue()
plt.close(fig_pdf)

# Store in session state
st.session_state['radar_chart'] = chart_bytes
```

---

### 3. Performance Metrics (Not Yet Implemented)

**Current Status:** The Performance Metrics page displays radar charts but does not have PDF export functionality.

**To Add PDF Export:**

1. **Save radar chart to buffer:**
   ```python
   # After creating the radar chart figure
   performance_radar_buffer = BytesIO()
   fig.savefig(performance_radar_buffer, format='png', dpi=150, 
               bbox_inches='tight', facecolor='white', edgecolor='none')
   performance_radar_buffer.seek(0)
   st.session_state['performance_radar_chart'] = performance_radar_buffer.getvalue()
   plt.close(fig)
   ```

2. **Create PDF generation function:**
   ```python
   def generate_performance_metrics_pdf(player_name, player_data, radar_chart_bytes=None):
       # Similar structure to other PDF functions
       # Include player data, metrics, and embedded radar chart
   ```

3. **Add download button:**
   ```python
   if st.button("Download Performance Metrics PDF"):
       radar_bytes = st.session_state.get('performance_radar_chart')
       pdf_bytes = generate_performance_metrics_pdf(selected_player, player_data, radar_bytes)
       if pdf_bytes:
           st.download_button("Download PDF", data=pdf_bytes, 
                            file_name=f"performance_{player_name}.pdf",
                            mime="application/pdf")
   ```

---

## Technical Implementation

### PDF Document Structure

```python
# 1. Create buffer
pdf_buffer = BytesIO()

# 2. Create document template
doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                      rightMargin=0.3*inch, leftMargin=0.3*inch,
                      topMargin=0.3*inch, bottomMargin=0.3*inch)

# 3. Define styles
styles = getSampleStyleSheet()
custom_style = ParagraphStyle(
    'CustomStyle',
    parent=styles['Normal'],
    fontSize=8,
    textColor=colors.HexColor('#333333'),
    spaceAfter=3,
)

# 4. Build elements list
elements = []
elements.append(Paragraph("Title", title_style))
elements.append(Spacer(1, 0.1*inch))
elements.append(Table(data, colWidths=[...]))
# ... more elements

# 5. Build PDF
doc.build(elements)
pdf_buffer.seek(0)
return pdf_buffer.getvalue()
```

### Common PDF Elements

#### Paragraphs

```python
from reportlab.lib.utils import simpleSplit

# Basic paragraph
para = Paragraph("Text content", style)
elements.append(para)

# With HTML formatting
para = Paragraph("<b>Bold</b> and <i>italic</i> text", style)
elements.append(para)

# Escape HTML in user input
from html import escape
safe_text = escape(user_input)
para = Paragraph(safe_text, style)
```

#### Tables

```python
# Table data (list of lists)
table_data = [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
    ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3'],
]

# Create table
table = Table(table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch])

# Style table
table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),  # Header background
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))

elements.append(table)
```

#### Images (Charts)

```python
from reportlab.platypus import Image

# From bytes
chart_img = Image(BytesIO(chart_bytes), width=5*inch, height=5*inch)
elements.append(chart_img)

# From file path
img = Image('path/to/image.png', width=4*inch, height=3*inch)
elements.append(img)
```

#### Spacing and Page Breaks

```python
from reportlab.platypus import Spacer, PageBreak

# Add vertical space
elements.append(Spacer(1, 0.1*inch))  # 0.1 inch spacing

# Force new page
elements.append(PageBreak())
```

### Style Definitions

```python
# Title style
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#8B0000'),
    spaceAfter=10,
)

# Heading style
heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=10,
    textColor=colors.HexColor('#333333'),
    spaceAfter=6,
    spaceBefore=8,
)

# Normal text style
normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=8,
    spaceAfter=3,
)

# Small text style
small_style = ParagraphStyle(
    'CustomSmall',
    parent=styles['Normal'],
    fontSize=7,
    textColor=colors.HexColor('#666666'),
)
```

---

## Adding PDF Export to New Features

### Step-by-Step Guide

1. **Create PDF Generation Function**
   ```python
   def generate_feature_pdf(data, chart_bytes=None):
       if not PDF_AVAILABLE:
           return None
       
       try:
           pdf_buffer = BytesIO()
           doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                                 rightMargin=0.3*inch, leftMargin=0.3*inch,
                                 topMargin=0.3*inch, bottomMargin=0.3*inch)
           
           elements = []
           styles = getSampleStyleSheet()
           
           # Add content
           # ...
           
           doc.build(elements)
           pdf_buffer.seek(0)
           return pdf_buffer.getvalue()
       except Exception as e:
           st.error(f"Error generating PDF: {e}")
           return None
   ```

2. **Save Charts/Visualizations to Session State**
   ```python
   # After creating matplotlib figure
   chart_buffer = BytesIO()
   fig.savefig(chart_buffer, format='png', dpi=150, 
               bbox_inches='tight', facecolor='white', edgecolor='none')
   chart_buffer.seek(0)
   st.session_state['feature_chart'] = chart_buffer.getvalue()
   plt.close(fig)
   ```

3. **Add Download Button**
   ```python
   if st.button("Download PDF"):
       chart_bytes = st.session_state.get('feature_chart')
       pdf_bytes = generate_feature_pdf(data, chart_bytes)
       
       if pdf_bytes:
           st.download_button(
               "Download PDF",
               data=pdf_bytes,
               file_name=f"feature_{datetime.now().strftime('%Y%m%d')}.pdf",
               mime="application/pdf",
               use_container_width=True
           )
   ```

### Best Practices

1. **Error Handling:** Always wrap PDF generation in try/except blocks
2. **Memory Management:** Close matplotlib figures after saving (`plt.close(fig)`)
3. **White Background:** Use white backgrounds for charts intended for PDF
4. **DPI:** Use 150 DPI for good quality without excessive file size
5. **File Naming:** Include timestamps or unique identifiers in filenames
6. **Session State:** Clear session state after download to prevent memory buildup
7. **Text Escaping:** Always escape user input to prevent HTML injection
8. **Page Breaks:** Use `PageBreak()` for large charts or new sections

---

## Code Patterns & Examples

### Complete Example: Simple Data Export PDF

```python
def generate_data_export_pdf(df, title="Data Export"):
    """Generate a simple PDF with a data table."""
    if not PDF_AVAILABLE:
        return None
    
    try:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Convert DataFrame to table
        table_data = [df.columns.tolist()]  # Header
        for _, row in df.iterrows():
            table_data.append([str(val) for val in row.values])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch] * len(df.columns))
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

# Usage
if st.button("Export to PDF"):
    pdf_bytes = generate_data_export_pdf(my_dataframe, "My Data Export")
    if pdf_bytes:
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="data_export.pdf",
            mime="application/pdf"
        )
```

### Example: PDF with Chart

```python
def generate_chart_pdf(title, chart_bytes):
    """Generate PDF with embedded chart."""
    if not PDF_AVAILABLE:
        return None
    
    try:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                              rightMargin=0.3*inch, leftMargin=0.3*inch,
                              topMargin=0.3*inch, bottomMargin=0.3*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_para = Paragraph(title, styles['Heading1'])
        elements.append(title_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Chart image
        if chart_bytes:
            chart_img = Image(BytesIO(chart_bytes), width=5*inch, height=5*inch)
            elements.append(chart_img)
        
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error: {e}")
        return None
```

---

## Troubleshooting

### Common Issues

1. **PDF not generating:**
   - Check if `PDF_AVAILABLE` is `True`
   - Verify ReportLab is installed: `pip install reportlab`
   - Check error messages in Streamlit console

2. **Charts not appearing in PDF:**
   - Ensure chart is saved with white background
   - Check that `BytesIO` buffer is properly created and seeked to 0
   - Verify DPI is set (150 is recommended)

3. **Text overflow:**
   - Use `truncate_text()` helper function for long text
   - Adjust column widths in tables
   - Use smaller font sizes if needed

4. **Memory issues:**
   - Close matplotlib figures after saving: `plt.close(fig)`
   - Clear session state after download
   - Use appropriate DPI (not too high)

5. **Encoding errors:**
   - Escape HTML in user input
   - Handle special characters properly
   - Use UTF-8 encoding

---

## Summary

The PDF export system uses:
- **ReportLab** for PDF generation
- **BytesIO** for in-memory file handling
- **Matplotlib** for chart creation
- **Session state** for passing data between function calls
- **Streamlit download buttons** for user downloads

Key patterns:
1. Create PDF generation function
2. Save charts to session state as bytes
3. Build PDF with ReportLab elements
4. Return PDF bytes
5. Display download button with PDF bytes

This system is flexible and can be extended to any feature that needs PDF export functionality.






