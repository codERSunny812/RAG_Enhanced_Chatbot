import sys
import os
import json
import time

# So it can find backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.pipeline import generate_answer
from rouge_score import rouge_scorer

# Paths
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "test_questions.json")
RESULTS_PATH   = os.path.join(os.path.dirname(__file__), "eval_results.json")
REPORT_PATH    = os.path.join(os.path.dirname(__file__), "eval_report.txt")


def check_keywords(answer: str, keywords: list[str]) -> dict:
    answer_lower = answer.lower()
    matched = []
    missed  = []

    for kw in keywords:
        kw_lower = kw.lower()
        # Direct match
        if kw_lower in answer_lower:
            matched.append(kw)
        # Partial match — every word in keyword appears in answer
        elif all(word in answer_lower for word in kw_lower.split()):
            matched.append(kw)
        else:
            missed.append(kw)

    score = len(matched) / len(keywords) if keywords else 0
    return {"matched": matched, "missed": missed, "score": round(score, 2)}


def check_faithfulness(answer: str, sources: list[dict]) -> bool:
    """
    Faithful if:
    - Answer is not the fallback message
    - At least 3 sources were retrieved (means retrieval worked)
    - Answer length is reasonable (not a one-word dodge)
    """
    if "could not find" in answer.lower():
        return False
    if len(answer.strip()) < 30:
        return False
    if len(sources) >= 3:
        return True
    return False


def run_evaluation():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    results     = []
    total       = len(questions)
    keyword_scores   = []
    faithfulness_scores = []

    print(f"\n{'='*60}")
    print(f"  RAG Evaluation — {total} questions")
    print(f"{'='*60}\n")

    for i, item in enumerate(questions):
        qid      = item["id"]
        question = item["question"]
        keywords = item["expected_keywords"]

        print(f"[{i+1}/{total}] Q{qid}: {question[:60]}...")

        start = time.time()
        result = generate_answer(question)
        elapsed = round(time.time() - start, 2)

        answer  = result["answer"]
        sources = result["sources"]

        kw_result   = check_keywords(answer, keywords)
        faithful    = check_faithfulness(answer, sources)

        keyword_scores.append(kw_result["score"])
        faithfulness_scores.append(1 if faithful else 0)

        print(f"  Keyword score : {kw_result['score']} | Faithful: {faithful} | Time: {elapsed}s")

        results.append({
            "id":              qid,
            "question":        question,
            "answer":          answer,
            "sources":         sources,
            "keyword_score":   kw_result["score"],
            "matched":         kw_result["matched"],
            "missed":          kw_result["missed"],
            "faithful":        faithful,
            "response_time_s": elapsed
        })

    # Summary metrics
    avg_keyword     = round(sum(keyword_scores) / total, 3)
    avg_faithfulness = round(sum(faithfulness_scores) / total, 3)
    avg_time        = round(sum(r["response_time_s"] for r in results) / total, 2)

    summary = {
        "total_questions":        total,
        "avg_keyword_score":      avg_keyword,
        "avg_faithfulness_score": avg_faithfulness,
        "avg_response_time_s":    avg_time,
        "keyword_score_pct":      f"{round(avg_keyword * 100, 1)}%",
        "faithfulness_pct":       f"{round(avg_faithfulness * 100, 1)}%",
    }

    # Save full results JSON
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)

    # Save readable text report
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("RAG INSURANCE CHATBOT — EVALUATION REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Questions    : {total}\n")
        f.write(f"Keyword Accuracy   : {summary['keyword_score_pct']}\n")
        f.write(f"Faithfulness Score : {summary['faithfulness_pct']}\n")
        f.write(f"Avg Response Time  : {avg_time}s\n\n")
        f.write("="*60 + "\n\n")

        for r in results:
            f.write(f"Q{r['id']}: {r['question']}\n")
            f.write(f"Keyword Score : {r['keyword_score']} | Faithful: {r['faithful']}\n")
            f.write(f"Matched       : {r['matched']}\n")
            f.write(f"Missed        : {r['missed']}\n")
            f.write(f"Answer        : {r['answer'][:300]}...\n")
            f.write("-"*60 + "\n\n")

    # Print final summary
    print(f"\n{'='*60}")
    print(f"  EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"  Keyword Accuracy   : {summary['keyword_score_pct']}")
    print(f"  Faithfulness Score : {summary['faithfulness_pct']}")
    print(f"  Avg Response Time  : {avg_time}s")
    print(f"\n  Results saved to   : evaluation/eval_results.json")
    print(f"  Report saved to    : evaluation/eval_report.txt")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_evaluation()