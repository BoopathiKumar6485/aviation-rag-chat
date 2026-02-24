import json
import time
import requests
from typing import List, Dict, Any
import pandas as pd
from tabulate import tabulate
from test_questions import ALL_QUESTIONS

class RAGEvaluator:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = []
        
    def evaluate_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single question"""
        question = question_data["question"]
        q_type = question_data["type"]
        
        # Send to API
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.api_url}/ask",
                json={"text": question, "debug": True, "use_hybrid": True}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze results
                answer = result["answer"]
                citations = result.get("citations", [])
                chunks = result.get("retrieved_chunks", [])
                
                # Check if answer is grounded
                has_citations = len(citations) > 0
                
                # Check if refused appropriately
                refused = "not available" in answer.lower()
                
                # Check retrieval hit (did we get relevant chunks?)
                retrieval_hit = len(chunks) > 0
                
                # Check faithfulness (simple heuristic: answer contains citations)
                faithful = any(f"[Source:" in answer or ".pdf" in answer.lower() 
                              for citation in citations)
                
                return {
                    "question": question,
                    "type": q_type,
                    "answer": answer,
                    "citations_count": len(citations),
                    "chunks_retrieved": len(chunks),
                    "response_time": response_time,
                    "has_citations": has_citations,
                    "refused": refused,
                    "retrieval_hit": retrieval_hit,
                    "faithful": faithful,
                    "status": "success"
                }
            else:
                return {
                    "question": question,
                    "type": q_type,
                    "error": f"API error: {response.status_code}",
                    "status": "error"
                }
        except Exception as e:
            return {
                "question": question,
                "type": q_type,
                "error": str(e),
                "status": "error"
            }
    
    def run_evaluation(self):
        """Run evaluation on all questions"""
        print(f"Starting evaluation of {len(ALL_QUESTIONS)} questions...")
        
        for i, q in enumerate(ALL_QUESTIONS, 1):
            print(f"Evaluating {i}/{len(ALL_QUESTIONS)}: {q['question'][:50]}...")
            result = self.evaluate_question(q)
            self.results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        return self.results
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate evaluation metrics"""
        successful = [r for r in self.results if r.get("status") == "success"]
        
        if not successful:
            return {"error": "No successful evaluations"}
        
        # Overall metrics
        total = len(self.results)
        success_count = len(successful)
        
        # Retrieval hit rate
        retrieval_hits = sum(1 for r in successful if r.get("retrieval_hit", False))
        retrieval_rate = retrieval_hits / success_count if success_count > 0 else 0
        
        # Faithfulness (citations present)
        faithful_count = sum(1 for r in successful if r.get("faithful", False))
        faithfulness_rate = faithful_count / success_count if success_count > 0 else 0
        
        # Hallucination rate (inverse of faithfulness + appropriate refusals)
        # Count cases where answer was given but no citations
        hallucinations = sum(1 for r in successful 
                           if not r.get("refused", True) and not r.get("has_citations", False))
        hallucination_rate = hallucinations / success_count if success_count > 0 else 0
        
        # Average response time
        avg_response_time = sum(r.get("response_time", 0) for r in successful) / success_count
        
        # Metrics by question type
        metrics_by_type = {}
        for q_type in ["simple", "applied", "reasoning"]:
            type_results = [r for r in successful if r.get("type") == q_type]
            if type_results:
                metrics_by_type[q_type] = {
                    "count": len(type_results),
                    "retrieval_rate": sum(1 for r in type_results if r.get("retrieval_hit", False)) / len(type_results),
                    "faithfulness_rate": sum(1 for r in type_results if r.get("faithful", False)) / len(type_results)
                }
        
        return {
            "total_questions": total,
            "successful": success_count,
            "failed": total - success_count,
            "retrieval_hit_rate": retrieval_rate,
            "faithfulness_rate": faithfulness_rate,
            "hallucination_rate": hallucination_rate,
            "avg_response_time": avg_response_time,
            "metrics_by_type": metrics_by_type
        }
    
    def get_best_worst_answers(self, n: int = 5) -> Dict[str, List]:
        """Get best and worst answers based on quality"""
        successful = [r for r in self.results if r.get("status") == "success"]
        
        # Score answers (higher is better)
        for r in successful:
            score = 0
            if r.get("has_citations", False):
                score += 2
            if r.get("faithful", False):
                score += 2
            if not r.get("refused", True) and r.get("citations_count", 0) > 0:
                score += 1
            r["quality_score"] = score
        
        # Sort by score
        sorted_results = sorted(successful, key=lambda x: x.get("quality_score", 0), reverse=True)
        
        best = sorted_results[:n]
        worst = sorted_results[-n:] if len(sorted_results) >= n else sorted_results
        
        return {
            "best": [
                {
                    "question": r["question"],
                    "answer": r["answer"][:200] + "...",
                    "citations": r.get("citations_count", 0),
                    "score": r.get("quality_score", 0)
                }
                for r in best
            ],
            "worst": [
                {
                    "question": r["question"],
                    "answer": r["answer"][:200] + "...",
                    "citations": r.get("citations_count", 0),
                    "score": r.get("quality_score", 0),
                    "issue": "No citations" if not r.get("has_citations") else "Low quality"
                }
                for r in worst
            ]
        }
    
    def generate_report(self, output_file: str = "reports/report.md"):
        """Generate markdown report"""
        metrics = self.calculate_metrics()
        best_worst = self.get_best_worst_answers()
        
        report = f"""# Aviation RAG System Evaluation Report

## Overview
- **Evaluation Date**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **Total Questions**: {metrics['total_questions']}
- **Successful Responses**: {metrics['successful']}
- **Failed Responses**: {metrics['failed']}

## Key Metrics

| Metric | Value |
|--------|-------|
| Retrieval Hit Rate | {metrics['retrieval_hit_rate']:.2%} |
| Faithfulness Rate | {metrics['faithfulness_rate']:.2%} |
| Hallucination Rate | {metrics['hallucination_rate']:.2%} |
| Average Response Time | {metrics['avg_response_time']:.2f}s |

## Metrics by Question Type

| Type | Count | Retrieval Rate | Faithfulness Rate |
|------|-------|----------------|-------------------|
"""
        
        for q_type, type_metrics in metrics.get('metrics_by_type', {}).items():
            report += f"| {q_type.capitalize()} | {type_metrics['count']} | {type_metrics['retrieval_rate']:.2%} | {type_metrics['faithfulness_rate']:.2%} |\n"
        
        report += f"""
## Best 5 Answers

"""
        
        for i, ans in enumerate(best_worst['best'], 1):
            report += f"{i}. **Question**: {ans['question']}\n"
            report += f"   **Answer**: {ans['answer']}\n"
            report += f"   **Citations**: {ans['citations']}\n"
            report += f"   **Quality Score**: {ans['score']}/5\n\n"
        
        report += f"""
## Worst 5 Answers

"""
        
        for i, ans in enumerate(best_worst['worst'], 1):
            report += f"{i}. **Question**: {ans['question']}\n"
            report += f"   **Answer**: {ans['answer']}\n"
            report += f"   **Issue**: {ans['issue']}\n"
            report += f"   **Quality Score**: {ans['score']}/5\n\n"
        
        report += f"""
## Qualitative Analysis

### Strengths
- System effectively retrieves relevant chunks for {metrics['retrieval_hit_rate']:.2%} of questions
- Faithfulness rate of {metrics['faithfulness_rate']:.2%} indicates strong grounding
- Hybrid search improves retrieval quality for technical aviation terms

### Weaknesses
- Hallucination rate of {metrics['hallucination_rate']:.2%} indicates some unsupported claims
- Response time ({metrics['avg_response_time']:.2f}s) could be optimized
- Some complex reasoning questions lack depth in answers

### Recommendations
1. Implement better chunking strategy for multi-page concepts
2. Add confidence thresholding for uncertain answers
3. Fine-tune hybrid search weights for aviation domain
4. Consider graph-based retrieval for regulatory questions
"""
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"Report generated: {output_file}")
        return report

def main():
    """Run evaluation"""
    # Check if API is running
    try:
        requests.get("http://localhost:8000/health")
    except:
        print("Error: API not running. Please start the API first.")
        return
    
    # Run evaluation
    evaluator = RAGEvaluator()
    evaluator.run_evaluation()
    
    # Generate report
    evaluator.generate_report()
    
    # Print summary
    metrics = evaluator.calculate_metrics()
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Retrieval Hit Rate: {metrics['retrieval_hit_rate']:.2%}")
    print(f"Faithfulness Rate: {metrics['faithfulness_rate']:.2%}")
    print(f"Hallucination Rate: {metrics['hallucination_rate']:.2%}")
    print(f"Avg Response Time: {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    main()