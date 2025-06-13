from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
from html_processor.utils.logger import log_info
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

pdfmetrics.registerFont(TTFont('Arial', os.path.join(os.path.dirname(__file__), '../../Arial.ttf')))

def generate_pdf_reports(analyzed_data, output_dir, filename, overwrite=False):
    """Generates PDF reports from analyzed data.
    
    Args:
        analyzed_data: Dictionary containing the analyzed data
        output_dir: Directory where PDF files will be saved
        filename: Original HTML filename to base the PDF name on
        overwrite: If True, overwrites existing PDF files
    """
    log_info(f"Generating PDF report for: {filename}")
    report_name = filename.replace('.html', '_report.pdf')
    report_path = os.path.join(output_dir, report_name)
    if os.path.exists(report_path) and not overwrite:
        log_info(f"Skipping existing report: {report_path}")
        return
        
    # Create the PDF canvas
    c = canvas.Canvas(report_path, pagesize=pagesizes.A4)
    width, height = pagesizes.A4
    
    # Add title
    title = analyzed_data.get('title', f"Raport dla {filename}")
    c.setFont("Arial", 16)
    c.drawString(inch, height - inch, title)
    y = height - 1.5*inch
    c.setFont("Arial", 12)

    # Render all content in order
    content = analyzed_data.get('content', [])
    for elem in content:
        if elem['type'] == 'heading':
            c.setFont("Arial", 14)
            if y < inch + 20:
                c.showPage()
                y = height - inch
            c.drawString(inch, y, elem['text'])
            y -= 25
            c.setFont("Arial", 12)
        elif elem['type'] == 'paragraph':
            if y < inch + 20:
                c.showPage()
                y = height - inch
            c.drawString(inch, y, elem['text'])
            y -= 20
        elif elem['type'] == 'table':
            if elem['rows']:
                headers = elem['headers']
                table_data_formatted = [headers] + [[str(row.get(h, '')) for h in headers] for row in elem['rows']]
                col_widths = [max(80, min(150, width/len(headers)-20)) for _ in headers]
                table = Table(table_data_formatted, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,-1), 'Arial'),
                    ('FONTSIZE', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ]))
                table.wrapOn(c, width-2*inch, height-2*inch)
                table_height = table._height
                if y - table_height < inch:
                    c.showPage()
                    y = height - inch
                    c.setFont("Arial", 12)
                table.drawOn(c, inch, y - table_height)
                y = y - table_height - 20
        elif elem['type'] == 'footer':
            c.setFont("Arial", 10)
            if y < inch + 20:
                c.showPage()
                y = height - inch
            c.drawString(inch, inch, elem['text'])

    c.save()
    log_info(f"Successfully generated: {report_path}")