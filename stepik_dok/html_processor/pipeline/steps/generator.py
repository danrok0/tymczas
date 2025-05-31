from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
from html_processor.utils.logger import log_info

def generate_pdf_reports(analyzed_data, output_dir, filename, overwrite=False):
    """Generates PDF reports from analyzed data.
    
    Args:
        analyzed_data: List of dictionaries containing the analyzed data
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
    title = f"Report for {filename}"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, height - inch, title)
    c.setFont("Helvetica", 12)
    
    y = height - 2*inch
    for row in analyzed_data:
        for key, value in row.items():
            text = f"{key}: {value}"
            c.drawString(inch, y, text)
            y -= 20
            if y < inch:  # Start a new page if we run out of space
                c.showPage()
                y = height - inch
                c.setFont("Helvetica", 12)
    
    c.save()
    log_info(f"Successfully generated: {report_path}")