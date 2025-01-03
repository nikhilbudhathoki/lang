import streamlit as st
import requests
import io
from PyPDF2 import PdfReader
import logging
from langdetect import detect
from typing import Tuple, Optional, List
import json
from tenacity import retry, stop_after_attempt, wait_exponential

# API Configuration
from dotenv import load_dotenv
import os

load_dotenv()


# Predefined API keys
API_KEYS = [os.getenv(f"API_KEY_{i}") for i in range(9, 11)]

MODEL_NAME = "llama-3.3-70b-versatile"
MAX_CHUNK_SIZE = 4000  # Maximum text chunk size for API processing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors."""
    pass

class MetadataExtractor:
    def __init__(self):
        self.api_keys = API_KEYS.copy()  # Create a copy to preserve original keys
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.current_key_index = 0

    def _get_next_api_key(self) -> str:
        """Get the next available API key using rotation."""
        if not self.api_keys:
            raise APIError("No API keys available.")
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self.api_keys[self.current_key_index]

    def _chunk_text(self, text: str, chunk_size: int = MAX_CHUNK_SIZE) -> List[str]:
        """Split text into manageable chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # Add 1 for space
            if current_length + word_length > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_api_request(self, messages: List[dict]) -> dict:
        """Make API request with retry logic."""
        api_key = self._get_next_api_key()
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            "model": MODEL_NAME,
            "messages": messages,
        }

        try:
            response = requests.post(self.url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")

    def detect_language(self, text: str) -> str:
        """Detect the language of the given text with error handling."""
        try:
            return detect(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "unknown"

    def extract_metadata(self, text: str) -> str:
        """Extract metadata with improved chunk handling."""
        chunks = self._chunk_text(text)
        results = []

        for chunk in chunks:
            messages = [
                {
                    "role": "system",
                    "content": """Extract and organize the following metadata in JSON format:
                    - title
                    - author
                    - publication_date
                    - keywords (as array)
                    - summary (brief)"""
                },
                {"role": "user", "content": chunk}
            ]

            try:
                response = self._make_api_request(messages)
                metadata = response["choices"][0]["message"]["content"]
                results.append(metadata)
            except Exception as e:
                logger.error(f"Metadata extraction failed for chunk: {e}")
                continue

        return "\n\n".join(results)

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text with improved error handling."""
        chunks = self._chunk_text(text)
        translated_chunks = []

        for chunk in chunks:
            messages = [
                {"role": "system", "content": f"Translate the following text to {target_lang}:"},
                {"role": "user", "content": chunk}
            ]

            try:
                response = self._make_api_request(messages)
                translated_chunk = response["choices"][0]["message"]["content"]
                translated_chunks.append(translated_chunk)
            except Exception as e:
                logger.error(f"Translation failed for chunk: {e}")
                continue

        return "\n".join(translated_chunks)

def process_pdf(file_content: bytes) -> Tuple[Optional[str], Optional[str]]:
    """Process PDF with enhanced error handling."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        pages = []
        
        for page in pdf_reader.pages:
            try:
                text = page.extract_text()
                if text.strip():
                    pages.append(text)
            except Exception as e:
                logger.error(f"Error extracting text from page: {e}")
                continue

        if not pages:
            raise ValueError("No extractable text found in the document.")

        extractor = MetadataExtractor()
        detected_language = extractor.detect_language(pages[0])
        combined_text = "\n\n".join(pages)
        metadata = extractor.extract_metadata(combined_text)

        return metadata, detected_language

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise

def main():
   
    st.title(" Contextual Metadata Extractor")
    st.markdown(f"Using `{MODEL_NAME}` for extraction and analysis")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file:
        try:
            file_content = uploaded_file.read()
            
            if st.button("Extract Metadata", key="extract"):
                with st.spinner("Processing document..."):
                    try:
                        metadata, detected_language = process_pdf(file_content)
                        
                        if metadata:
                            st.success("Metadata extracted successfully!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("Extracted Metadata")
                                st.text_area("Original", metadata, height=400)
                            
                            with col2:
                                st.subheader("Translation Options")
                                st.write(f"Detected Language: {detected_language}")
                                
                                target_language = st.selectbox(
                                    "Select target language",
                                    ["English", "Nepali", "Spanish", "French", "German"]
                                )
                                
                                if st.button("Translate", key="translate"):
                                    with st.spinner(f"Translating to {target_language}..."):
                                        extractor = MetadataExtractor()
                                        translated = extractor.translate_text(metadata, target_language)
                                        st.text_area(
                                            f"Translated ({target_language})",
                                            translated,
                                            height=400
                                        )
                    
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
                        logger.exception("Document processing failed")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            logger.exception("File reading failed")

if __name__ == "__main__":
    main()
