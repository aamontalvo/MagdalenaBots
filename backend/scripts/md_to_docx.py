#!/usr/bin/env python3
"""
Convert MD to DOCX with proper formatting
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Read MD file
md_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\INFORME_ACTIVIDADES_FEBRERO_2026.md'
output_path = r'C:\Users\alexa\Documents\PERSONAL PROJECTS\MagdalenaBot\INFORME_ACTIVIDADES_FEBRERO_2026.docx'

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Create document
doc = Document()

# Set up styles
style = doc.styles['Heading 1']
font = style.font
font.size = Pt(16)
font.bold = True
font.color.rgb = RGBColor(0x2E, 0x5E, 0xAA)

style = doc.styles['Heading 2']
font = style.font
font.size = Pt(14)
font.bold = True
font.color.rgb = RGBColor(0x2E, 0x5E, 0xAA)

style = doc.styles['Heading 3']
font = style.font
font.size = Pt(12)
font.bold = True

# Parse and convert
lines = content.split('\n')
i = 0
in_table = False
table_lines = []

while i < len(lines):
    line = lines[i].strip()
    
    if not line:
        i += 1
        continue
    
    # Horizontal rule
    if line == '---':
        doc.add_paragraph()
        i += 1
        continue
    
    # Heading 1
    if line.startswith('# ') and not line.startswith('## '):
        text = line[2:]
        doc.add_heading(text, level=1)
        i += 1
        continue
    
    # Heading 2
    if line.startswith('## '):
        text = line[3:]
        doc.add_heading(text, level=2)
        i += 1
        continue
    
    # Heading 3
    if line.startswith('### '):
        text = line[4:]
        doc.add_heading(text, level=3)
        i += 1
        continue
    
    # Table handling
    if line.startswith('|'):
        if not in_table:
            in_table = True
            table_lines = []
        table_lines.append(line)
        i += 1
        
        # Check if next line is not a table row
        if i >= len(lines) or not lines[i].strip().startswith('|'):
            # Process table
            in_table = False
            if len(table_lines) >= 2:  # Header + separator + at least one row
                # Parse table
                rows_data = []
                for j, row_line in enumerate(table_lines):
                    if '---' in row_line:  # Skip separator row
                        continue
                    cells = [c.strip() for c in row_line.split('|')[1:-1]]
                    rows_data.append(cells)
                
                if rows_data:
                    # Create table
                    table = doc.add_table(rows=1, cols=len(rows_data[0]))
                    table.style = 'Table Grid'
                    
                    # Header row
                    hdr_cells = table.rows[0].cells
                    for j, cell_text in enumerate(rows_data[0]):
                        hdr_cells[j].text = cell_text
                        for paragraph in hdr_cells[j].paragraphs:
                            for run in paragraph.runs:
                                run.bold = True
                                run.font.size = Pt(10)
                    
                    # Data rows
                    for row_data in rows_data[1:]:
                        row_cells = table.add_row().cells
                        for j, cell_text in enumerate(row_data):
                            row_cells[j].text = cell_text
                            for paragraph in row_cells[j].paragraphs:
                                for run in paragraph.runs:
                                    run.font.size = Pt(9)
                    
                    doc.add_paragraph()
        continue
    else:
        in_table = False
    
    # Bold text **text**
    if '**' in line:
        p = doc.add_paragraph()
        parts = line.split('**')
        for j, part in enumerate(parts):
            if j % 2 == 1:  # Odd parts are bold
                run = p.add_run(part)
                run.bold = True
            else:
                p.add_run(part)
    # Bullet list
    elif line.startswith('- ') or line.startswith('1. '):
        # Handle list items
        p = doc.add_paragraph(line[2:], style='List Bullet' if line.startswith('- ') else 'List Number')
    # Regular paragraph
    else:
        doc.add_paragraph(line)
    
    i += 1

# Save document
doc.save(output_path)
print(f"Documento Word generado: {output_path}")
