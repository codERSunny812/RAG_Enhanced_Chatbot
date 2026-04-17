import sys
import os
import json
import time
import httpx

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.pipeline import generate_answer
from vectordb.retriever import retrieve
from config import OLLAMA_URL, OLLAMA_MODEL


def ask_llama_no_rag(question: str) -> str:
    """Ask Llama without any context (pure LLM knowledge)"""
    prompt = f"""You are an Indian health insurance advisor. Answer this question based ONLY on your general knowledge.

Question: {question}

Answer:"""
    
    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30.0
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error: {str(e)}"


def calculate_answer_accuracy(answer: str, keywords: list) -> float:
    """Binary accuracy: 1.0 if >=60% keywords present"""
    if not keywords:
        return 1.0
    
    answer_lower = answer.lower()
    matched = 0
    
    for kw in keywords:
        if kw.lower() in answer_lower:
            matched += 1
        else:
            kw_words = kw.lower().split()
            if len(kw_words) > 1:
                hits = sum(1 for word in kw_words if len(word) > 3 and word in answer_lower)
                if hits / len(kw_words) >= 0.6:
                    matched += 0.8
    
    return 1.0 if (matched / len(keywords)) >= 0.6 else 0.0


def calculate_relevance(answer: str, keywords: list) -> float:
    """Relevance score (0-1)"""
    if not keywords:
        return 1.0
    
    answer_lower = answer.lower()
    matched = 0
    
    for kw in keywords:
        if kw.lower() in answer_lower:
            matched += 1
        else:
            kw_words = kw.lower().split()
            if len(kw_words) > 1:
                hits = sum(1 for word in kw_words if len(word) > 3 and word in answer_lower)
                if hits / len(kw_words) >= 0.6:
                    matched += 0.7
    
    return round(matched / len(keywords), 2)


def calculate_context_recall(retrieved_chunks: list, keywords: list) -> float:
    """Context recall: do retrieved chunks contain keywords?"""
    if not retrieved_chunks:
        return 0.0
    
    context_text = " ".join([chunk.get("text", "") for chunk in retrieved_chunks]).lower()
    
    if not keywords:
        return 1.0
    
    found = 0
    for kw in keywords:
        if kw.lower() in context_text:
            found += 1
        else:
            kw_words = kw.lower().split()
            if len(kw_words) > 1:
                hits = sum(1 for word in kw_words if len(word) > 3 and word in context_text)
                if hits / len(kw_words) >= 0.5:
                    found += 0.7
    
    return round(found / len(keywords), 2)


def calculate_faithfulness(answer: str, retrieved_chunks: list) -> float:
    """Faithfulness: is answer grounded in context?"""
    if not retrieved_chunks:
        return 0.0
    
    context_text = " ".join([chunk.get("text", "") for chunk in retrieved_chunks]).lower()
    answer_words = answer.lower().split()
    
    if not answer_words:
        return 0.0
    
    grounded = sum(1 for word in answer_words if len(word) > 2 and word in context_text)
    return round(grounded / len(answer_words), 2)


def categorize_question(question_text: str) -> str:
    """Categorize questions into paper's 4 categories"""
    text_lower = question_text.lower()
    
    if any(term in text_lower for term in ["regulation", "irdai", "law", "legal", "grievance", "ombudsman"]):
        return "Insurance Laws and Regulations"
    elif any(term in text_lower for term in ["renewal", "grace period", "free look", "portability", "add family"]):
        return "Policy Administration and Contract Validity"
    elif any(term in text_lower for term in ["waiting period", "pre-existing", "exclusion", "definition"]):
        return "Interpretation of Insurance Clauses"
    else:
        return "Principles and Fundamentals of Insurance"


def run_local_comparison():
    with open(os.path.join(os.path.dirname(__file__), "test_questions.json"), "r") as f:
        questions = json.load(f)
    
    # Use first 20 questions
    test_questions = questions[:40]
    
    # Initialize categories
    categories = {
        "Insurance Laws and Regulations": {"questions": [], "rag_accuracy": [], "rag_relevance": [], "rag_faith": [], "llama_accuracy": [], "llama_relevance": []},
        "Policy Administration and Contract Validity": {"questions": [], "rag_accuracy": [], "rag_relevance": [], "rag_faith": [], "llama_accuracy": [], "llama_relevance": []},
        "Interpretation of Insurance Clauses": {"questions": [], "rag_accuracy": [], "rag_relevance": [], "rag_faith": [], "llama_accuracy": [], "llama_relevance": []},
        "Principles and Fundamentals of Insurance": {"questions": [], "rag_accuracy": [], "rag_relevance": [], "rag_faith": [], "llama_accuracy": [], "llama_relevance": []}
    }
    
    print("\n" + "="*80)
    print("  RAG vs Local Llama (No RAG) - With Paper Metrics")
    print("="*80)
    
    for i, item in enumerate(test_questions):
        question = item["question"]
        keywords = item["expected_keywords"]
        category = categorize_question(question)
        
        print(f"\n[{i+1}/{len(test_questions)}] {question[:50]}...")
        
        # Get retrieved chunks
        retrieved_chunks = retrieve(question, top_k=5)
        
        # RAG answer
        rag_result = generate_answer(question)
        rag_answer = rag_result["answer"]
        
        # Llama answer (no RAG)
        print("  Asking Llama (no context)...")
        llama_answer = ask_llama_no_rag(question)
        
        # Calculate metrics
        rag_accuracy = calculate_answer_accuracy(rag_answer, keywords)
        rag_relevance = calculate_relevance(rag_answer, keywords)
        rag_faith = calculate_faithfulness(rag_answer, retrieved_chunks)
        llama_accuracy = calculate_answer_accuracy(llama_answer, keywords)
        llama_relevance = calculate_relevance(llama_answer, keywords)
        
        categories[category]["questions"].append(item)
        categories[category]["rag_accuracy"].append(rag_accuracy)
        categories[category]["rag_relevance"].append(rag_relevance)
        categories[category]["rag_faith"].append(rag_faith)
        categories[category]["llama_accuracy"].append(llama_accuracy)
        categories[category]["llama_relevance"].append(llama_relevance)
        
        print(f"  RAG - Acc: {rag_accuracy:.2f} | Rel: {rag_relevance:.2f} | Faith: {rag_faith:.2f}")
        print(f"  Llama - Acc: {llama_accuracy:.2f} | Rel: {llama_relevance:.2f}")
        
        time.sleep(0.5)
    
    # Print results by category (matching paper's Table 1 format)
    print("\n" + "="*80)
    print("  RESULTS BY CATEGORY (Paper Table 1 Format)")
    print("="*80)
    print(f"\n{'Category':<45} {'Count':<6} {'RAG Acc':<10} {'RAG Rel':<10} {'Llama Acc':<10} {'Llama Rel':<10}")
    print("-"*80)
    
    for category, data in categories.items():
        if not data["questions"]:
            continue
        
        count = len(data["questions"])
        avg_rag_acc = sum(data["rag_accuracy"]) / count
        avg_rag_rel = sum(data["rag_relevance"]) / count
        avg_llama_acc = sum(data["llama_accuracy"]) / count
        avg_llama_rel = sum(data["llama_relevance"]) / count
        
        print(f"{category:<45} {count:<6} {avg_rag_acc:<10.2f} {avg_rag_rel:<10.2f} {avg_llama_acc:<10.2f} {avg_llama_rel:<10.2f}")
    
    # Overall averages
    all_rag_acc = []
    all_rag_rel = []
    all_llama_acc = []
    all_llama_rel = []
    
    for data in categories.values():
        all_rag_acc.extend(data["rag_accuracy"])
        all_rag_rel.extend(data["rag_relevance"])
        all_llama_acc.extend(data["llama_accuracy"])
        all_llama_rel.extend(data["llama_relevance"])
    
    avg_rag_acc = sum(all_rag_acc) / len(all_rag_acc) if all_rag_acc else 0
    avg_rag_rel = sum(all_rag_rel) / len(all_rag_rel) if all_rag_rel else 0
    avg_llama_acc = sum(all_llama_acc) / len(all_llama_acc) if all_llama_acc else 0
    avg_llama_rel = sum(all_llama_rel) / len(all_llama_rel) if all_llama_rel else 0
    
    print("-"*80)
    print(f"{'OVERALL AVERAGE':<45} {len(all_rag_acc):<6} {avg_rag_acc:<10.2f} {avg_rag_rel:<10.2f} {avg_llama_acc:<10.2f} {avg_llama_rel:<10.2f}")
    print("="*80)
    
    # Improvement summary
    print("\n📊 RAG IMPROVEMENT OVER PURE LLAMA:")
    print("-"*50)
    print(f"  Answer Accuracy Improvement: {(avg_rag_acc - avg_llama_acc) * 100:.1f}%")
    print(f"  Relevance Improvement: {(avg_rag_rel - avg_llama_rel) * 100:.1f}%")
    print(f"  RAG Faithfulness Score: {sum(all_rag_faith)/len(all_rag_faith) if 'all_rag_faith' in dir() else 0:.2f}")
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "local_comparison_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "rag_accuracy": f"{avg_rag_acc*100:.1f}%",
                "rag_relevance": f"{avg_rag_rel*100:.1f}%",
                "llama_accuracy": f"{avg_llama_acc*100:.1f}%",
                "llama_relevance": f"{avg_llama_rel*100:.1f}%",
                "improvement_accuracy": f"{(avg_rag_acc - avg_llama_acc)*100:.1f}%",
                "improvement_relevance": f"{(avg_rag_rel - avg_llama_rel)*100:.1f}%"
            },
            "by_category": {cat: {"count": len(data["questions"]), "rag_accuracy": sum(data["rag_accuracy"])/len(data["questions"]) if data["questions"] else 0} 
                           for cat, data in categories.items() if data["questions"]}
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    run_local_comparison()