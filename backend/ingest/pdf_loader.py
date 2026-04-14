import os
import pdfplumber
from config import DATA_DIR


def load_pdfs_from_folder(folder_path: str = DATA_DIR) -> list[dict]:
    """
    Reads all PDFs from the given folder.
    Returns a list of dicts: { "source": filename, "text": full extracted text }
    """
    documents = []

    if not os.path.exists(folder_path):
        print(f"[ERROR] Folder not found: {folder_path}")
        return documents

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

    if not pdf_files:
        print("[WARNING] No PDF files found in folder.")
        return documents

    for filename in pdf_files:
        filepath = os.path.join(folder_path, filename)
        print(f"[INFO] Reading: {filename}")

        text = extract_text_from_pdf(filepath)

        if text.strip():
            documents.append({
                "source": filename,
                "text": text
            })
            print(f"[OK] Extracted {len(text)} characters from {filename}")
        else:
            print(f"[SKIP] No text found in {filename}")

    print(f"\n[DONE] Loaded {len(documents)} PDF(s) successfully.")
    return documents


def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts and cleans text from a single PDF using pdfplumber.
    """
    full_text = []

    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                cleaned = clean_text(text)
                full_text.append(cleaned)

    return "\n".join(full_text)


def clean_text(text: str) -> str:
    """
    Basic cleaning: removes excess whitespace and blank lines.
    """
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned_lines)


# Quick test — run this file directly to verify it works
if __name__ == "__main__":
    docs = load_pdfs_from_folder()
    for doc in docs:
        print(f"\n--- {doc['source']} ---")
        print(doc['text'][:500])   # print first 500 chars as preview