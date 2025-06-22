#!/usr/bin/env python3

import readline

import argparse
import os
import ai21
from ai21.models.chat import ChatMessage
import signal
import sys
import json
from accuracy_tester import AccuracyTester
from retriever import Retriever


parser = argparse.ArgumentParser(description="Q&A system LLM demo to handle files and documents summary.")
parser.add_argument("--folder", '-f', default='./Automotive/Raw_PDFs/', type=str, help="Path to the folder containing the relevant files.")

args = parser.parse_args()

# ========== CONFIG ==========
AI21_API_KEY = "YOUR_AI21LABS_API_KEY"
os.environ["AI21_API_KEY"] = AI21_API_KEY
ai21.api_key = AI21_API_KEY
client = ai21.AI21Client(api_key=AI21_API_KEY)

EMBEDDING_MODEL_NAME = "intfloat/e5-small-v2"
VECTOR_DIM = 384



# ========== QUERYING ==========

# ========== LLM ANSWERING ==========
def llm_query(question, top_chunks):
    formatted_context = "\n\n".join([
        f"[Source: {chunk['source']}, Chunk #{chunk['chunk_id']}]\n{chunk['text']}" for chunk in top_chunks
    ])
    
    messages = [
        ChatMessage(role="system", content=(
            "You are a precise assistant. Use only the given context to answer. "
            "If the answer is not found in the context, say 'No Answer Found'."
        )),
        ChatMessage(role="user", content=(
            f"Context:\n{formatted_context}\n\n"
            f"Question: {question}\n\n"
            f"Answer (based only on the above context):"
        ))
    ]
    
    try:
        response = client.chat.completions.create(
            model="jamba-mini-1.6-2025-03",
            messages=messages,
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] {e}"
    

def save_chunk_map(chunks, filename):
    enriched_chunks = [
        {
            "id": i,
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"]
        }
        for i, chunk in enumerate(chunks)
    ]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(enriched_chunks, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved {len(enriched_chunks)} chunks to {filename}")



# ========== SIGNAL HANDLER ==========
def signal_handler(sig, frame):
    print("\n[INFO] Graceful shutdown requested. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# ========== MAIN PIPELINE ==========
def main():
    retriever = Retriever(args.folder)
    index = retriever.pre_retrieval()

    save_chunk_map(retriever.get_chunks(), "chunk_map.json")

    at = None

    while True:
        question = input("\nHi there! what can I assist you with? (If you wish to leave, please type 'exit'): ")
        if question.lower() == 'exit':
            print("Leaving...\nSee you next time!")
            if at:
                at.free_resource()
            break

        top_chunks = retriever.get_top_k_chunks(question, index)
        answer = llm_query(question, top_chunks)

        at = AccuracyTester(question)

        at.find_matching_chunks_by_keywords()

        if len(answer.strip()) == 0 or "not found" in answer.lower():
            print("\n[Answer]: No Answer Found")
        else:
            print("\n[Answer]:", answer)

        at.log_precision_test_json(top_chunks, answer)
        at.evaluate_precision_k_json(top_chunks, answer)


if __name__ == "__main__":
    main()
