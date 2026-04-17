import sys
import os
import json
import time
import httpx
import re

# Try to load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.pipeline import generate_answer
from vectordb.retriever import retrieve

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("\n❌ OPENAI_API_KEY not found!\n")
    sys.exit(1)


def test_openai_api():
    """Test if OpenAI API key is working"""
    print("\n🔍 Testing OpenAI API key...")
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Say 'OK'"}],
                "max_tokens": 10
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            print("✅ OpenAI API key is VALID")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def ask_chatgpt_with_context(question: str, context_chunks: list[dict]) -> str:
    """ChatGPT with context - with better error handling"""
    if not context_chunks:
        return "No context available to answer this question."
    
    context_text = ""
    for i, chunk in enumerate(context_chunks[:3]):
        context_text += f"\n{chunk['text']}\n"
    
    prompt = f"""Answer this health insurance question using ONLY the context below. Be brief and direct.

Context:
{context_text}

Question: {question}

Answer:"""
    
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 300
            },
            timeout=30.0
        )
        
        # Check if request was successful
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
        
        data = response.json()
        
        # Check if response has expected structure
        if "choices" not in data:
            return f"Unexpected response format: {list(data.keys())}"
        
        if not data["choices"]:
            return "No response from API"
        
        return data["choices"][0].get("message", {}).get("content", "No content").strip()
        
    except httpx.TimeoutException:
        return "Timeout: API took too long to respond"
    except Exception as e:
        return f"Error: {str(e)}"


def check_keywords_simple(answer: str, keywords: list) -> tuple:
    """Simple keyword check"""
    if not answer or answer.startswith("Error") or answer.startswith("API Error"):
        return 0.0, [], keywords
    
    answer_lower = answer.lower()
    matched = []
    missed = []
    
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in answer_lower:
            matched.append(kw)
        else:
            # Check for partial matches
            kw_words = kw_lower.split()
            found = False
            for word in kw_words:
                if len(word) > 3 and word in answer_lower:
                    found = True
                    break
            if found:
                matched.append(f"{kw}(partial)")
            else:
                missed.append(kw)
    
    # Count full matches only for score
    full_matches = [m for m in matched if '(partial)' not in m]
    score = len(full_matches) / len(keywords) if keywords else 0
    return score, matched, missed


def run_comparison():
    # First test the API
    if not test_openai_api():
        print("\n⚠️ OpenAI API not working. Please check your API key.")
        print("Get a valid key from: https://platform.openai.com/api-keys")
        return
    
    with open(os.path.join(os.path.dirname(__file__), "test_questions.json"), "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    # Test first 5 questions
    test_questions = questions[:5]
    
    results = []
    rag_scores = []
    gpt_scores = []
    
    print("\n" + "="*80)
    print("  RAG vs ChatGPT Comparison")
    print("="*80)
    
    for i, item in enumerate(test_questions):
        question = item["question"]
        keywords = item["expected_keywords"]
        
        print(f"\n[{i+1}/{len(test_questions)}] {question[:60]}...")
        
        # Get context once for both
        retrieved_chunks = retrieve(question, top_k=5)
        
        if not retrieved_chunks:
            print("  ⚠️ No context retrieved")
            continue
        
        # Get RAG answer
        rag_result = generate_answer(question)
        rag_answer = rag_result["answer"]
        
        # Get GPT answer with same context
        print("  Calling GPT...")
        time.sleep(0.5)  # Rate limit
        gpt_answer = ask_chatgpt_with_context(question, retrieved_chunks)
        
        # Score both
        rag_score, rag_matched, rag_missed = check_keywords_simple(rag_answer, keywords)
        gpt_score, gpt_matched, gpt_missed = check_keywords_simple(gpt_answer, keywords)
        
        rag_scores.append(rag_score)
        gpt_scores.append(gpt_score)
        
        print(f"  RAG Score: {rag_score*100:.0f}%")
        print(f"  GPT Score: {gpt_score*100:.0f}%")
        print(f"  GPT Answer Preview: {gpt_answer[:150]}...")
        
        results.append({
            "question": question,
            "rag_answer": rag_answer,
            "gpt_answer": gpt_answer,
            "rag_score": rag_score,
            "gpt_score": gpt_score,
            "rag_matched": rag_matched,
            "rag_missed": rag_missed,
            "gpt_matched": gpt_matched,
            "gpt_missed": gpt_missed
        })
    
    # Summary
    if rag_scores:
        avg_rag = sum(rag_scores) / len(rag_scores) * 100
        avg_gpt = sum(gpt_scores) / len(gpt_scores) * 100
    else:
        avg_rag = avg_gpt = 0
    
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    print(f"  RAG Keyword Accuracy: {avg_rag:.1f}%")
    print(f"  GPT Keyword Accuracy: {avg_gpt:.1f}%")
    print(f"  RAG wins: {avg_rag > avg_gpt}")
    print("="*80 + "\n")
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "comparison_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "rag_accuracy": f"{avg_rag:.1f}%",
                "gpt_accuracy": f"{avg_gpt:.1f}%",
                "rag_wins": avg_rag > avg_gpt
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    run_comparison()




