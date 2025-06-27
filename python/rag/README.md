# 🔍 Retrieval-Augmented Generation (RAG) Question Answering System

This is a Python-based **RAG pipeline** designed for question answering over local documents (PDF, Markdown, TXT, JSON). It combines **document retrieval**, **semantic chunking**, **embedding-based search**, **LLM-based generation** (via AI21 Jamba), and **evaluation** using both **Precision\@k** and **RAGAS** metrics.

---

## 🚀 Features

* 📄 Ingests and chunks documents (PDF, `.md`, `.txt`, `.json`)
* 🤖 Embeds text using `SentenceTransformers` and indexes with `FAISS`
* 🧠 Queries LLM (AI21 Jamba) using top-k retrieved chunks
* ✅ Evaluates answer quality using:

  * Precision\@k (chunk-level relevance)
  * RAGAS (context precision, recall, faithfulness, answer relevancy)
* 📦 Caches FAISS index and embeddings for faster subsequent loads
* 📊 Logs evaluation data for audit and research

---

## 📁 Project Structure

```
.
├── run_rag.py                 # Main entry point (interactive CLI)
├── retriever.py              # Document loader, chunker, embedder, retriever
├── accuracy_tester.py        # Precision@k evaluation utility
├── assets/
│   ├── embeddings.index      # Saved FAISS index
│   ├── chunks.pkl            # Saved metadata for chunks
│   ├── chunk_map.json        # Metadata of all chunks for evaluation
│   ├── precision_test_log.json # Logs for Precision@k testing
│   └── ragas_dataset.json    # (Optional) RAGAS-formatted dataset
├── sentence_transformer/     # Local cache of embedding model
└── Automotive/Raw_PDFs/      # (Default) Folder for source documents
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/rag-pipeline.git
cd rag-pipeline
```

### 2. Create a virtual environment and activate it

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary>📦 <b>Dependencies (partial list)</b></summary>

* `sentence-transformers`
* `faiss-cpu`
* `markdown2`
* `PyMuPDF` (`fitz`)
* `langchain`
* `ragas`
* `psutil`
* `openai`
* `ai21`

</details>

---

## 🔐 API Keys

Set your API keys for AI21 and OpenAI before running the app:

```bash
export AI21_API_KEY=your_ai21_key
export OPENAI_API_KEY=your_openai_key
```

You can also replace the placeholders directly in `run_rag.py`:

```python
AI21_API_KEY = "your_ai21_key"
OPENAI_API_KEY = "your_openai_key"
```

---

## ▶️ Running the App

```bash
python run_rag.py --folder ./path/to/your/docs
```

You'll be prompted with:

```
Hi there! what can I assist you with?
```

Ask a question based on your uploaded documents. To exit, type `exit`.

---

## 📊 Evaluation Methods

### ✅ Precision\@k

* Compares overlap between retrieved chunks and keywords in the LLM’s answer.
* Logs question, top-k chunks, relevant chunks, and LLM response.

### 📈 RAGAS (Optional)

* Evaluates:

  * `context_precision`
  * `context_recall`
  * `answer_relevancy`
  * `faithfulness`
* You’ll be prompted upon exiting whether to run RAGAS evaluation using `assets/ragas_dataset.json`.

---

## 📌 Code Overview

### `Retriever`

* Loads `.pdf`, `.md`, `.txt`, `.json`
* Chunks using `RecursiveCharacterTextSplitter`
* Embeds using `SentenceTransformer`
* Stores/reloads FAISS index

### `AccuracyTester`

* Matches question keywords to chunk texts
* Evaluates answer's chunk relevance via Precision\@k
* Writes detailed evaluation log to `precision_test_log.json`

### `run_rag.py`

* CLI interface for user input
* Manages retrieval + generation
* Integrates with both evaluation systems
* Tracks response latency and memory

---

## 📄 Example Output

```
Hi there! what can I assist you with? (If you wish to leave, please type 'exit'): What are the main causes of engine failure?

[Answer]: The main causes of engine failure include overheating, oil starvation, and detonation...

🕒 Response Time: 3.25 seconds
🫠 RAM Usage: 212.54 MB

📈 Precision@5: 0.80
```

---

## 🧪 Sample Dataset for RAGAS (Optional)

To run RAGAS evaluation:

1. Create or update `assets/ragas_dataset.json`:

```json
[
  {
    "question": "What are common sensor failures in modern vehicles?",
    "answer": "",
    "gt_answer": "Common sensor failures include oxygen sensor failure, mass airflow sensor issues, etc.",
    "source": "Vehicle_Troubleshooting.pdf"
  }
]
```

2. Exit the app and choose `Y` when prompted to run RAGAS.

---

## 🧹 Cleanup

Temporary and evaluation files are saved to:

* `assets/chunk_map.json`
* `assets/precision_test_log.json`

Use:

```python
AccuracyTester.free_resource()
```

Or let the app handle it on exit.

---

## ❓ Troubleshooting

* **Q**: I get an error on FAISS index load.
  **A**: Try deleting `assets/embeddings.index` and `assets/chunks.pkl` and rerun.

* **Q**: Answer quality is poor.
  **A**: Try increasing chunk size or using a higher-quality embedding model.

---

## 📄 License

MIT License

---

## 🙌 Acknowledgements

* [SentenceTransformers](https://www.sbert.net/)
* [FAISS by Facebook AI](https://github.com/facebookresearch/faiss)
* [AI21 Labs](https://www.ai21.com/)
* [LangChain](https://www.langchain.com/)
* [RAGAS Evaluation Toolkit](https://github.com/explodinggradients/ragas)

---

## ✨ Future Enhancements

* Add support for multi-modal inputs
* Web UI using Streamlit or Gradio
* Plug-and-play support for other LLMs (Anthropic, Mistral, etc.)
* Better ground truth dataset generation for RAGAS

---

