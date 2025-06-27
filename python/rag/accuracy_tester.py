import json
import os

# ========== Testing ==========

class AccuracyTester:
    """
    Class for evaluating the accuracy of retrieved document chunks of the RAG pipeline. Using Precision@k method.

    Attributes:
        question (str): The input question being evaluated.
        chunk_map_path (str): Path to JSON mapping of all available chunks.
        precision_test_path (str): File to which precision logs will be saved.
        keywords (List[str]): Filtered keywords from the question.
        matches (List[dict]): Chunks identified as relevant matches.
        precision_log (List[dict]): Stored logs for precision evaluations.

    Methods:
        find_matching_chunks_by_keywords(): Identifies relevant chunks using keyword hits.
        log_precision_test(top_chunks, answer, k): Logs precision test results to a JSON file.
        evaluate_precision_k(top_chunks, answer, k): Computes and prints Precision@k.
        free_resource(): Cleans up the generated chunk_map & precision files.
    """

    def __init__(self, question, chunk_map_path="chunk_map.json", precision_test_path="precision_test_log.json"):
        self.question = question
        self.chunk_map_path = f"assets/{chunk_map_path}"
        with open(self.chunk_map_path, "r", encoding="utf-8") as f:
            self.chunk_map = json.load(f)

        self.keywords = [word for word in self.question.lower().split() if len(word) > 3]

        self.matches = []

        self.precision_test_path = f"assets/{precision_test_path}"
        if os.path.exists(self.precision_test_path):
            with open(self.precision_test_path, "r", encoding="utf-8") as f:
                self.precision_log = json.load(f)
        else:
            self.precision_log = []
        

    def evaluate_answer(self, top_chunks, answer, k=5):
        self._find_matching_chunks_by_keywords()
        self._log_precision_test(top_chunks, answer, k)
        self._evaluate_precision_k(top_chunks, answer, k)
    

    def _find_matching_chunks_by_keywords(self, min_hits=1):
        """
        Identifies chunks that match the question based on keyword overlap.

        Args:
            min_hits (int): Minimum number of keyword matches required.
    """
        for chunk in self.chunk_map:
            text = chunk["text"].lower()
            hits = sum(kw in text for kw in self.keywords)
            if hits >= min_hits:
                self.matches.append(chunk)


    def _log_precision_test(self, top_chunks, answer, k):
        """
        Logs the precision test result to a JSON file.

        Args:
            top_chunks (list): List of retrieved chunks.
            answer (str): Answer returned by the LLM.
            k (int): Number of top chunks considered in evaluation.
        """

        entry = {
            "question": self.question,
            "retrieved_chunks": [chunk["chunk_id"] for chunk in top_chunks[:k]],
            "relevant_chunks": [match["chunk_id"] for match in self.matches],
            "answer": answer.strip()
        }

        self.precision_log.append(entry)

        with open(self.precision_test_path, "w", encoding="utf-8") as f:
            json.dump(self.precision_log, f, indent=2, ensure_ascii=False)


    def _evaluate_precision_k(self, top_chunks, answer, k):
        """
        Evaluates and prints Precision@k using keyword overlap with the generated answer.

        Args:
            top_chunks (list): List of retrieved chunks.
            answer (str): Generated answer.
            k (int): Number of top retrieved chunks to consider.
        """

        if not answer.strip() or "no answer found" in answer.lower():
            return 0.0

        answer_keywords = [word for word in answer.lower().split() if len(word) > 3]
        retrieved_ids = set(chunk["chunk_id"] for chunk in top_chunks[:k])

        true_positives = 0
        for chunk in self.chunk_map:
            if chunk["chunk_id"] in retrieved_ids:
                chunk_text = chunk["text"].lower()
                if any(kw in chunk_text for kw in answer_keywords):
                    true_positives += 1

        precision = min(true_positives, k) / k
        print(f"\n📈 Precision@5: {precision:.2f}")
    

    def free_resource(self):
        """
        Cleans up generated precision-related files.
        """

        os.remove(self.chunk_map_path)
        os.remove(self.precision_test_path)
