
import sys
import os
import json
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.pipeline import generate_answer
from vectordb.retriever import retrieve

# Paths
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "test_questions.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "eval_results.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "eval_report.txt")


def calculate_answer_accuracy(answer: str, keywords: list) -> float:
    """
    Paper's Answer Accuracy (binary): 1.0 if answer contains core keywords, 0.0 otherwise
    """
    if not keywords:
        return 1.0
    
    answer_lower = answer.lower()
    
    # Check if at least 60% of keywords are present
    matched = 0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in answer_lower:
            matched += 1
        else:
            # Partial match for multi-word keywords
            kw_words = kw_lower.split()
            if len(kw_words) > 1:
                hits = sum(1 for word in kw_words if len(word) > 3 and word in answer_lower)
                if hits / len(kw_words) >= 0.6:
                    matched += 0.8
    
    # Binary: 1.0 if >= 60% of keywords matched, else 0.0 (matches paper's binary metric)
    return 1.0 if (matched / len(keywords)) >= 0.6 else 0.0


def calculate_relevance(answer: str, keywords: list) -> float:
    """
    Paper's Relevance: How relevant is the answer? (0-1 scale, paper shows 0.88-1.00)
    """
    if not keywords:
        return 1.0
    
    answer_lower = answer.lower()
    matched = 0
    
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in answer_lower:
            matched += 1
        else:
            kw_words = kw_lower.split()
            if len(kw_words) > 1:
                hits = sum(1 for word in kw_words if len(word) > 3 and word in answer_lower)
                if hits / len(kw_words) >= 0.6:
                    matched += 0.7
            elif len(kw_words) == 1 and len(kw_words[0]) > 3:
                if kw_words[0] in answer_lower:
                    matched += 0.7
    
    return round(matched / len(keywords), 2)


def calculate_context_recall(question: str, retrieved_chunks: list, keywords: list) -> float:
    """
    Paper's Context Recall: Did retrieval get relevant context?
    """
    if not retrieved_chunks:
        return 0.0
    
    context_text = " ".join([chunk.get("text", "") for chunk in retrieved_chunks]).lower()
    
    if not keywords:
        return 1.0
    
    found = 0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in context_text:
            found += 1
        else:
            kw_words = kw_lower.split()
            if len(kw_words) > 1:
                hits = sum(1 for word in kw_words if len(word) > 3 and word in context_text)
                if hits / len(kw_words) >= 0.5:
                    found += 0.7
    
    return round(found / len(keywords), 2)


def calculate_faithfulness(answer: str, retrieved_chunks: list) -> float:
    """
    Paper's Faithfulness: Is answer grounded in retrieved context?
    """
    if not retrieved_chunks:
        return 0.0
    
    context_text = " ".join([chunk.get("text", "") for chunk in retrieved_chunks]).lower()
    answer_words = answer.lower().split()
    
    if not answer_words:
        return 0.0
    
    grounded = sum(1 for word in answer_words if len(word) > 2 and word in context_text)
    return round(grounded / len(answer_words), 2)


def categorize_question(question_text: str, qid: int) -> str:
    """
    Categorize questions into paper's 4 categories based on content
    """
    text_lower = question_text.lower()
    
    if any(term in text_lower for term in ["regulation", "irdai", "law", "legal", "compliance", "mandatory", "grievance", "ombudsman"]):
        return "Insurance Laws and Regulations"
    elif any(term in text_lower for term in ["renewal", "grace period", "free look", "portability", "add family", "policy period", "lapse"]):
        return "Policy Administration and Contract Validity"
    elif any(term in text_lower for term in ["waiting period", "pre-existing", "exclusion", "definition", "clause", "interpretation", "not covered"]):
        return "Interpretation of Insurance Clauses"
    else:
        return "Principles and Fundamentals of Insurance"


def run_evaluation():
    """Run evaluation with all 4 paper metrics"""
    
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    # Initialize category buckets
    categories = {
        "Insurance Laws and Regulations": [],
        "Policy Administration and Contract Validity": [],
        "Interpretation of Insurance Clauses": [],
        "Principles and Fundamentals of Insurance": []
    }
    
    # Categorize questions
    for q in questions:
        category = categorize_question(q["question"], q["id"])
        q["category"] = category
        categories[category].append(q)
    
    results_by_category = {}
    
    print(f"\n{'='*80}")
    print(f"  RAG Evaluation with Paper's 4 Metrics")
    print(f"  Total questions: {len(questions)}")
    print(f"{'='*80}\n")
    
    for category, cat_questions in categories.items():
        if not cat_questions:
            continue
        
        print(f"\n📁 {category} ({len(cat_questions)} questions)")
        print("-"*80)
        
        category_metrics = {
            "answer_accuracy": [],
            "relevance": [],
            "context_recall": [],
            "faithfulness": []
        }
        
        for i, item in enumerate(cat_questions):
            qid = item["id"]
            question = item["question"]
            keywords = item["expected_keywords"]
            
            print(f"  [{i+1}/{len(cat_questions)}] Q{qid}: {question[:50]}...")
            
            start = time.time()
            
            # Get retrieved chunks
            retrieved_chunks = retrieve(question, top_k=5)
            
            # Get RAG answer
            rag_result = generate_answer(question)
            answer = rag_result["answer"]
            
            elapsed = round(time.time() - start, 2)
            
            # Calculate all 4 metrics
            answer_accuracy = calculate_answer_accuracy(answer, keywords)
            relevance = calculate_relevance(answer, keywords)
            context_recall = calculate_context_recall(question, retrieved_chunks, keywords)
            faithfulness = calculate_faithfulness(answer, retrieved_chunks)
            
            category_metrics["answer_accuracy"].append(answer_accuracy)
            category_metrics["relevance"].append(relevance)
            category_metrics["context_recall"].append(context_recall)
            category_metrics["faithfulness"].append(faithfulness)
            
            print(f"     Acc: {answer_accuracy:.2f} | Rel: {relevance:.2f} | Rec: {context_recall:.2f} | Faith: {faithfulness:.2f} | Time: {elapsed}s")
        
        # Calculate category averages
        results_by_category[category] = {
            "query_count": len(cat_questions),
            "answer_accuracy": round(sum(category_metrics["answer_accuracy"]) / len(cat_questions), 2),
            "relevance": round(sum(category_metrics["relevance"]) / len(cat_questions), 2),
            "context_recall": round(sum(category_metrics["context_recall"]) / len(cat_questions), 2),
            "faithfulness": round(sum(category_metrics["faithfulness"]) / len(cat_questions), 2)
        }
    
    # Calculate weighted averages
    total_questions = sum(m["query_count"] for m in results_by_category.values())
    weighted_accuracy = sum(m["answer_accuracy"] * m["query_count"] for m in results_by_category.values()) / total_questions
    weighted_relevance = sum(m["relevance"] * m["query_count"] for m in results_by_category.values()) / total_questions
    weighted_recall = sum(m["context_recall"] * m["query_count"] for m in results_by_category.values()) / total_questions
    weighted_faithfulness = sum(m["faithfulness"] * m["query_count"] for m in results_by_category.values()) / total_questions
    
    # Print table matching paper's Table 1
    print("\n" + "="*80)
    print("  RESULTS (Paper Table 1 Format)")
    print("="*80)
    print(f"\n{'Category':<45} {'Count':<6} {'Accuracy':<10} {'Relevance':<10} {'Recall':<10} {'Faithfulness':<10}")
    print("-"*80)
    
    for category, metrics in results_by_category.items():
        print(f"{category:<45} {metrics['query_count']:<6} {metrics['answer_accuracy']:<10.2f} {metrics['relevance']:<10.2f} {metrics['context_recall']:<10.2f} {metrics['faithfulness']:<10.2f}")
    
    print("-"*80)
    print(f"{'TOTAL/WEIGHTED AVG':<45} {total_questions:<6} {weighted_accuracy:<10.2f} {weighted_relevance:<10.2f} {weighted_recall:<10.2f} {weighted_faithfulness:<10.2f}")
    print("="*80)
    
    # # Compare with paper
    # print("\n📊 COMPARISON WITH PAPER'S TABLE 1:")
    # print("-"*70)
    # print(f"  {'Metric':<20} {'Your RAG':<12} {'Paper RAG':<12} {'Paper ChatGPT':<15}")
    # print("-"*60)
    # print(f"  {'Answer Accuracy':<20} {weighted_accuracy:<12.2f} {0.90:<12} {0.78:<15}")
    # print(f"  {'Relevance':<20} {weighted_relevance:<12.2f} {0.98:<12} {0.88:<15}")
    # print(f"  {'Context Recall':<20} {weighted_recall:<12.2f} {0.94:<12} {'N/A':<15}")
    # print(f"  {'Faithfulness':<20} {weighted_faithfulness:<12.2f} {0.96:<12} {'N/A':<15}")
    
    # Save results
    summary = {
        "total_questions": total_questions,
        "weighted_averages": {
            "answer_accuracy": weighted_accuracy,
            "relevance": weighted_relevance,
            "context_recall": weighted_recall,
            "faithfulness": weighted_faithfulness
        },
        "by_category": results_by_category,
        "paper_comparison": {
            "paper_rag": {"accuracy": 0.90, "relevance": 0.98, "context_recall": 0.94, "faithfulness": 0.96},
            "paper_chatgpt": {"accuracy": 0.78, "relevance": 0.88}
        }
    }
    
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Save report
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("RAG INSURANCE CHATBOT — PAPER METRICS EVALUATION\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total Questions: {total_questions}\n\n")
        f.write(f"{'Metric':<25} {'Your Score':<12} {'Paper RAG':<12} {'Paper ChatGPT':<15}\n")
        f.write("-"*65 + "\n")
        f.write(f"{'Answer Accuracy':<25} {weighted_accuracy:<12.2f} {0.90:<12} {0.78:<15}\n")
        f.write(f"{'Relevance':<25} {weighted_relevance:<12.2f} {0.98:<12} {0.88:<15}\n")
        f.write(f"{'Context Recall':<25} {weighted_recall:<12.2f} {0.94:<12} {'N/A':<15}\n")
        f.write(f"{'Faithfulness':<25} {weighted_faithfulness:<12.2f} {0.96:<12} {'N/A':<15}\n")
    
    print(f"\n✅ Results saved to: {RESULTS_PATH}")
    print(f"✅ Report saved to: {REPORT_PATH}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    run_evaluation()