from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Takes list of { "source": filename, "text": full_text }
    Returns list of { "source": filename, "chunk_id": int, "text": chunk_text }
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []

    for doc in documents:
        chunks = splitter.split_text(doc["text"])

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": i,
                "text": chunk
            })

        print(f"[INFO] {doc['source']} → {len(chunks)} chunks")

    print(f"\n[DONE] Total chunks created: {len(all_chunks)}")
    return all_chunks


# Quick test
if __name__ == "__main__":
    from ingest.pdf_loader import load_pdfs_from_folder

    docs = load_pdfs_from_folder()
    chunks = chunk_documents(docs)

    # Preview first 2 chunks
    print("\n--- Preview: first 2 chunks ---")
    for chunk in chunks[:2]:
        print(f"\nSource: {chunk['source']} | Chunk ID: {chunk['chunk_id']}")
        print(f"Length: {len(chunk['text'])} chars")
        print(f"Text: {chunk['text'][:200]}...")