import streamlit as st
import requests
import io
from docx import Document
from PyPDF2 import PdfReader
import logging
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import math
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
import os 
from dotenv import load_dotenv
import os

load_dotenv()

# Predefined API keys
API_KEYS = [os.getenv(f"API_KEY_{i}") for i in range(0, 11)]

MODEL_NAME = "llama-3.3-70b-versatile"
TRANSLATION_URL = "https://api.groq.com/openai/v1/chat/completions"

@dataclass
class APIKey:
    key: str
    used_tokens: int = 0
    invalid: bool = False

class ChunkProcessor:
    def __init__(self):
        self.api_keys = [APIKey(key) for key in API_KEYS]
        self.chunk_size = 8  # Maximum pages per chunk

    def get_next_api_key(self, chunk_index: int) -> APIKey:
        valid_keys = [key for key in self.api_keys if not key.invalid]
        if not valid_keys:
            raise RuntimeError("No valid API keys available.")
        return valid_keys[chunk_index % len(valid_keys)]

    def create_chunks(self, pages: List[str]) -> List[List[str]]:
        chunks = []
        total_pages = len(pages)

        num_chunks = min(len(self.api_keys), math.ceil(total_pages / 8))
        pages_per_chunk = math.ceil(total_pages / num_chunks)

        for i in range(0, total_pages, pages_per_chunk):
            chunk = pages[i:i + pages_per_chunk]
            if chunk:
                chunks.append(chunk)

        return chunks

    def process_chunk(self, chunk: List[str], chunk_index: int) -> Tuple[int, Dict]:
        try:
            api_key = self.get_next_api_key(chunk_index)
            combined_text = "\n".join(chunk)

            source_lang = detect(combined_text)
            target_lang = "English" if source_lang == "ne" else "Nepali"
            translated = self.translate_text(combined_text, target_lang, api_key)

            return chunk_index, {
                "original": combined_text,
                "translated": translated,
                "status": "success"
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                api_key.invalid = True
                return self.process_chunk(chunk, chunk_index)
            return chunk_index, {
                "original": "",
                "translated": "",
                "status": "error",
                "error": str(e)
            }
        except Exception as e:
            return chunk_index, {
                "original": "",
                "translated": "",
                "status": "error",
                "error": str(e)
            }

    def translate_text(self, text: str, target_lang: str, api_key: APIKey) -> str:
        headers = {
            'Authorization': f'Bearer {api_key.key}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": f"Translate the following text to {target_lang}:"},
                {"role": "user", "content": text}
            ]
        }

        response = requests.post(TRANSLATION_URL, json=data, headers=headers)
        response.raise_for_status()
        api_key.used_tokens += 1
        return response.json()['choices'][0]['message']['content']

class TranslationLogger:
    def __init__(self):
        self.logs = []

    def add_log(self, chunk_id, source_lang, target_lang, original, translated):
        self.logs.append({
            "chunk_id": chunk_id,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "original": original,
            "translated": translated
        })

    def get_log_df(self):
        return pd.DataFrame(self.logs)

def process_document(file_content: bytes):
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        pages = []

        for page in pdf_reader.pages:
            text = page.extract_text()
            if text.strip():
                pages.append(text)

        if not pages:
            return None

        processor = ChunkProcessor()
        chunks = processor.create_chunks(pages)

        results = {}
        total_chunks = len(chunks)
        progress_bar = st.progress(0)

        with ThreadPoolExecutor(max_workers=total_chunks) as executor:
            future_to_chunk = {
                executor.submit(processor.process_chunk, chunk, i): i 
                for i, chunk in enumerate(chunks)
            }
            completed_chunks = 0
            for future in as_completed(future_to_chunk):
                chunk_index, result = future.result()
                results[chunk_index] = result
                completed_chunks += 1
                progress_bar.progress(completed_chunks / total_chunks)

        merged_original = []
        merged_translated = []

        for i in range(len(chunks)):
            if results[i]["status"] == "success":
                merged_original.append(f"=== Chunk {i+1} ===\n{results[i]['original']}")
                merged_translated.append(f"=== Chunk {i+1} ===\n{results[i]['translated']}")

        return {
            "original": "\n\n---\n\n".join(merged_original),
            "translated": "\n\n---\n\n".join(merged_translated)
        }
    except Exception as e:
        return None

def main():
    st.title("TRANSLATOR")
    st.markdown(f"Using {MODEL_NAME} model for extraction and translation")

    translation_logger = TranslationLogger()

    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

    if uploaded_file is not None:
        file_content = uploaded_file.read()

        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                result = process_document(file_content)

                if result:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Original Content")
                        st.text_area("Original Metadata", result["original"], height=400)

                        st.download_button(
                            label="Download Original Content",
                            data=result["original"],
                            file_name="original_content.txt",
                            mime="text/plain"
                        )

                    with col2:
                        st.subheader("Translated Content")
                        st.text_area("Translated Metadata", result["translated"], height=400)

                        st.download_button(
                            label="Download Translated Content",
                            data=result["translated"],
                            file_name="translated_content.txt",
                            mime="text/plain"
                        )

                    st.subheader("Translation Logs")
                    log_df = translation_logger.get_log_df()
                    st.dataframe(log_df)

                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        log_df.to_excel(writer, index=False)
                    st.download_button(
                        label="Download Logs",
                        data=excel_buffer.getvalue(),
                        file_name="translation_logs.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

if __name__ == "__main__":
    main()
