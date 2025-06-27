#!/usr/bin/env python3

import readline

import argparse
import os
import sys
import json
import time
import psutil
import signal

import ai21
from ai21.models.chat import ChatMessage

from retriever import Retriever
from accuracy_tester import AccuracyTester

import openai
from datasets import Dataset
from ragas.metrics import context_precision, context_recall, answer_relevancy, faithfulness
from ragas import evaluate



parser = argparse.ArgumentParser(description="Q&A system LLM demo to handle files and documents summary.")
parser.add_argument("--folder", '-f', default='./raw_pdfs', type=str, help="Path to the folder containing the relevant files.")

args = parser.parse_args()

# ------------- ATTRIBUTES ------------- #

AI21_API_KEY = "AI21_API_KEY"
ai21.api_key = AI21_API_KEY
client = ai21.AI21Client(api_key=AI21_API_KEY)

EMBEDDING_MODEL_NAME = "intfloat/e5-small-v2" # other options - [all-MiniLM-L6-v2, 384] or [nomic-ai/nomic-embed-text-v1, 768]
VECTOR_DIM = 384

OPENAI_API_KEY = "OPENAI_API_KEY"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --------------------------------------- #

# --------- AI21 LABS LLM QUERY --------- #

def llm_query(question, top_chunks, ragas=False, ragas_data=None):
    """
    Sends a question and relevant document chunks to AI21 Labs's LLM and returns the generated answer.

    Args:
        question (str): The user's input question.
        top_chunks (list): List of top-k relevant chunks retrieved from the index.
        ragas (bool): Whether to run RAGAS evaluation.
        ragas_data (dict): The source for the RAGAS data that will be populate 'contexts' and 'answer' fields.

    Returns:
        str: The generated answer from the LLM.
    """

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
        answer = response.choices[0].message.content.strip()
        if ragas:
            ragas_data['contexts'] = [chunk['text'] for chunk in top_chunks]
            ragas_data['answer'] = answer

        return answer

    except Exception as e:
        return f"[ERROR] {e}"

# --------------------------------------- #

# ---------------- RAGAS ---------------- #

def run_ragas_accuracy_check(input_json, retriever, index):
    """
    Runs the RAGAS evaluation pipeline on a predefined set of questions.

    Args:
        input_json (str): Path to the RAGAS dataset JSON file.
        retriever (Retriever): The Retriever instance used to fetch document chunks.
        index (faiss.Index): FAISS index used for retrieval.

    Side Effects:
        - Populates RAGAS evaluation metrics and prints results.
    
    IMPORTANT NOTE:
        - This function can only be used for those who have enough ___, mostly available for paying ChatGPT subscribers.
    """

    with open(f"assets/{input_json}", 'r') as file:
        try:
            data = json.load(file)

            for i in range(len(data)):
                question = data[i]['question']
                top_chunks = retriever.get_top_k_chunks(data[i]['question'], index)
                llm_query(question, top_chunks, True, data[i])
        
            dataset = Dataset.from_list(data)

            result = evaluate(
                dataset,
                metrics=[context_precision, context_recall, answer_relevancy, faithfulness]
            )

            print(result)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# --------------------------------------- #

# ---------- HELPER FUNCTIONS ----------- #

def exit_rag(accuracy_tester, retriever, index):
    """
    Handles graceful shutdown, including optional RAGAS evaluation and cleanup.

    Args:
        accuracy_tester (AccuracyTester): To be able to clean up some json files.
        retriever (Retriever): The retriever instance used during the session.
        index (faiss.Index): The FAISS index used during the session.
    """

    finish = False
    if not accuracy_tester:
        finish = True
        
    while not finish:
        yes_or_no = input("\nDo you want to run RAGAS evaluation? [Y/N or Yes/No]? ")
        if yes_or_no.lower() == "yes" or yes_or_no.lower() == "y":
            finish = True
            run_ragas_accuracy_check("./ragas_dataset.json", retriever, index)
        elif yes_or_no.lower() == "n" or yes_or_no.lower() == "no":
            finish = True
        else:
            print("Please type Y/N or Yes/No only as an answer")

    print("Leaving...\nSee you next time!")
    if accuracy_tester:
        accuracy_tester.free_resource()
    
    exit(0)


def save_chunk_map(chunks, filename):
    """
    Saves the retrieved text chunks with their metadata to a JSON file.

    Args:
        chunks (list): List of dictionaries representing the text chunks.
        filename (str): Destination JSON file path.
    """

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


def signal_handler(sig, frame):
    """
    Handles SIGINT for graceful shutdown via Ctrl+C.

    Args:
        sig (int): Signal number.
        frame (frame): Stack frame.
    """

    print("\n[INFO] Graceful shutdown requested. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# --------------------------------------- #

# ---------------- START ---------------- #

def main():
    retriever = Retriever(args.folder, embedding_model_name=EMBEDDING_MODEL_NAME, embedding_vector_dim=VECTOR_DIM)
    index = retriever.pre_retrieval()

    save_chunk_map(retriever.get_chunks(), "./assets/chunk_map.json")

    at = None

    while True:
        question = input("\nHi there! what can I assist you with? (If you wish to leave, please type 'exit'): ")
        if question.lower() == 'exit':
            exit_rag(at, retriever, index)

        top_chunks = retriever.get_top_k_chunks(question, index)
        start = time.time()
        answer = llm_query(question, top_chunks)
        end = time.time()

        if len(answer.strip()) == 0 or "not found" in answer.lower():
            print("\n[Answer]: No Answer Found")
        else:
            print("\n[Answer]:", answer)

        print(f"🕒 Response Time: {end - start:.2f} seconds")
        
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024
        print(f"🧠 RAM Usage: {mem_mb:.2f} MB")

        at = AccuracyTester(question)
        at.evaluate_answer(top_chunks, answer)


if __name__ == "__main__":
    main()
