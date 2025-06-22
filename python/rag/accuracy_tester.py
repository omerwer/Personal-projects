import json
import os

# ========== Testing ==========

class AccuracyTester:
    def __init__(self, question, chunk_map_path="chunk_map.json", precision_test_path="precision_test_log.json"):
        self.question = question
        self.chunk_map_path = chunk_map_path
        with open(chunk_map_path, "r", encoding="utf-8") as f:
            self.chunk_map = json.load(f)

        self.keywords = [word for word in self.question.lower().split() if len(word) > 3]

        self.matches = []

        self.precision_test_path = precision_test_path
        if os.path.exists(precision_test_path):
            with open(precision_test_path, "r", encoding="utf-8") as f:
                self.precision_log = json.load(f)
        else:
            self.precision_log = []
        

    def find_matching_chunks_by_keywords(self, min_hits=1):
        for chunk in self.chunk_map:
            text = chunk["text"].lower()
            hits = sum(kw in text for kw in self.keywords)
            if hits >= min_hits:
                self.matches.append(chunk)


    def log_precision_test_json(self, top_chunks, answer, k=5):
        entry = {
            "question": self.question,
            "retrieved_chunks": [chunk["chunk_id"] for chunk in top_chunks[:k]],
            "relevant_chunks": [match["chunk_id"] for match in self.matches],
            "answer": answer.strip()
        }

        self.precision_log.append(entry)

        with open(self.precision_test_path, "w", encoding="utf-8") as f:
            json.dump(self.precision_log, f, indent=2, ensure_ascii=False)


    # Precision@K - also need to check RAGAS option
    def evaluate_precision_k_json(self, top_chunks, answer, k=5):
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

        # ⚠️ Cap true_positives to k to avoid precision > 1
        precision = min(true_positives, k) / k
        print(f"\n📈 Precision@5: {precision:.2f}")
    

    def free_resource(self):
        os.remove(self.chunk_map_path)
        os.remove(self.precision_test_path)
