import datetime
import re
import logging
from fpdf import FPDF
from django.utils.html import strip_tags
from html import unescape

logger = logging.getLogger(__name__)


class PDFExportService:
    """Service for exporting content to PDF format using fpdf2"""
    
    def __init__(self):
        # Initialize PDF with proper settings
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.set_margins(left=20, top=20, right=20)
        
    def export_notes_to_pdf(self, title: str, date: datetime.datetime = datetime.datetime.now(), content: str = None, filename_prefix: str = "notizen"):
        """Export notes to PDF with given title, date and content"""
        if not content:
            raise ValueError("Keine Notizen zum Export verfügbar.")
            
        try:
            # Add a page
            self.pdf.add_page()
            
            # Add title
            self._add_title(title, date)
            
            # Add content using HTML rendering
            self._add_html_content(content)
            
            # Generate filename
            filename = self._generate_filename(filename_prefix, date, title)
            
            # Generate PDF output - use dest='S' to get bytes
            pdf_output = self.pdf.output(dest='S')
            logger.info(f"PDF generated successfully, size: {len(pdf_output)} bytes")
            
            # Convert bytearray to bytes for Django compatibility
            if isinstance(pdf_output, bytearray):
                pdf_output = bytes(pdf_output)
            
            return {
                'content': pdf_output,
                'filename': filename,
                'content_type': 'application/pdf'
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Exportieren der Notizen als PDF: {str(e)}")
            raise Exception(f"Fehler beim Exportieren der Notizen als PDF: {str(e)}")
    
    def _add_title(self, title: str, date: datetime.datetime):
        """Add title to PDF"""
        # Set font for title
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.set_text_color(0, 0, 0)
        
        # Add title
        pdf_title = f"{title} ({date.strftime('%d.%m.%Y')})"
        self.pdf.cell(0, 10, pdf_title, ln=True, align="C")
        self.pdf.ln(10)  # Add space after title
    
    def _add_html_content(self, content: str):
        """Add HTML content to PDF using fpdf2's write_html method"""
        if not content:
            self.pdf.set_font("Arial", "", 11)
            self.pdf.cell(0, 10, "Keine Inhalte verfügbar", ln=True)
            return
            
        logger.info(f"Adding HTML content to PDF: {len(content)} characters")
        
        # Clean and prepare HTML content
        html_content = self._prepare_html_content(content)
        
        try:
            # Use fpdf2's built-in HTML rendering
            self.pdf.write_html(html_content)
            
        except Exception as e:
            logger.error(f"Error rendering HTML content: {str(e)}")
            # Fallback to plain text if HTML rendering fails
            self._add_plain_text_content(content)
    
    def _prepare_html_content(self, content: str) -> str:
        """Prepare HTML content for fpdf2 rendering"""
        if not content:
            return ""
            
        # Log the raw content for debugging
        logger.info(f"Raw HTML content: {content[:200]}...")
        
        # First, unescape HTML entities
        content = unescape(content)
        
        # Remove potentially problematic tags that fpdf2 doesn't support
        # Remove script tags and their content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and their content
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove unsupported tags but keep their content
        unsupported_tags = ['div', 'span', 'section', 'article', 'header', 'footer', 'nav', 'aside']
        for tag in unsupported_tags:
            content = re.sub(f'<{tag}[^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(f'</{tag}>', '', content, flags=re.IGNORECASE)
        
        # Ensure content is wrapped in proper HTML structure
        if not content.strip().startswith('<'):
            # If it's plain text, wrap it in paragraphs
            content = f"<p>{content}</p>"
        
        # Wrap in a basic HTML structure for better rendering
        html_content = f"""
        <html>
        <body>
            {content}
        </body>
        </html>
        """
        
        # Log the prepared content for debugging
        logger.info(f"Prepared HTML content: {html_content[:200]}...")
        
        return html_content
    
    def _add_plain_text_content(self, content: str):
        """Fallback method to add plain text content"""
        logger.info("Using fallback plain text rendering")
        
        # Clean HTML content to plain text
        clean_content = self._clean_html_to_text(content)
        
        # Set font for content
        self.pdf.set_font("Arial", "", 11)
        
        # Split content into paragraphs and add to PDF
        paragraphs = clean_content.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Use multi_cell for automatic text wrapping
                self.pdf.multi_cell(0, 6, paragraph)
                self.pdf.ln(4)  # Add space between paragraphs
    
    def _clean_html_to_text(self, html_content: str) -> str:
        """Clean HTML content to plain text as fallback"""
        if not html_content:
            return ""
            
        # Unescape HTML entities
        content = unescape(html_content)
        
        # Convert common HTML elements to text equivalents
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<p[^>]*>', '\n', content)
        content = re.sub(r'</p>', '\n', content)
        content = re.sub(r'<div[^>]*>', '\n', content)
        content = re.sub(r'</div>', '\n', content)
        
        # Handle lists
        content = re.sub(r'<ul[^>]*>', '\n', content)
        content = re.sub(r'</ul>', '\n', content)
        content = re.sub(r'<ol[^>]*>', '\n', content)
        content = re.sub(r'</ol>', '\n', content)
        content = re.sub(r'<li[^>]*>', '• ', content)
        content = re.sub(r'</li>', '\n', content)
        
        # Remove any remaining HTML tags
        content = strip_tags(content)
        
        # Clean up whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple newlines to double
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
        content = content.strip()
        
        return content
    
    def _generate_filename(self, prefix: str, date: datetime.datetime, title: str = None) -> str:
        """Generate a clean filename for the PDF"""
        filename = f"{prefix}_{date.strftime('%Y%m%d')}"
        if title:
            # Clean filename by removing special characters
            clean_title = re.sub(r"[^\w\s-]", "", title).strip()
            clean_title = re.sub(r"[-\s]+", "-", clean_title)
            if clean_title:
                filename += f"_{clean_title}"
        filename += ".pdf"
        return filename 