import io
import logging
from typing import Optional
import re

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from various file formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
    
    def extract_text_from_file(self, file_path: str, filename: str) -> Optional[str]:
        """
        Extract text from a file based on its extension
        
        Args:
            file_path: Path to the file
            filename: Name of the file (to determine format)
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            file_extension = self._get_file_extension(filename)
            
            if file_extension == '.txt':
                return self._extract_from_txt(file_path)
            elif file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_from_word(file_path)
            else:
                logger.warning(f"Unsupported file format: {file_extension}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            return None
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        
        return self._clean_text(text)
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                    
                return self._clean_text(text)
                
        except ImportError:
            logger.error("PyPDF2 not installed. Cannot extract PDF text.")
            return None
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return None
    
    def _extract_from_word(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            import docx
            
            doc = docx.Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
            return self._clean_text(text)
            
        except ImportError:
            logger.error("python-docx not installed. Cannot extract Word text.")
            return None
        except Exception as e:
            logger.error(f"Error extracting Word text: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove empty lines
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported"""
        extension = '.' + self._get_file_extension(filename)
        return extension in self.supported_formats