import io
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file's bytes using PyPDF.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        cleaned_text = text.strip()
        if not cleaned_text:
            # Fallback if PyPDF returns nothing (e.g. image-only PDF)
            return "This PDF file contains no selectable text. It might be scanned or image-based."
        return cleaned_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return f"Error extracting text: {str(e)}"
