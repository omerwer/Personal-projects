from sentence_transformers import SentenceTransformer
import os
import json
import fitz # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
import markdown2
import faiss
import pickle
import numpy as np


class Retriever:
    def __init__(self, data_folder_path, embedding_model_name="intfloat/e5-small-v2", embedding_vector_dim=384):
        self.data_folder_path = data_folder_path
        self.all_chunks = []
        self.file_map = {}

        self.model = SentenceTransformer(embedding_model_name, trust_remote_code=True)

        self.vector_dim = embedding_vector_dim

    def get_chunks(self):
        return self.all_chunks

    def pre_retrieval(self):
        self._load_files_and_extract_data()

        return self._create_embeddings()


    def _load_files_and_extract_data(self):
        print("[INFO] Loading and processing documents...")
        for fname in os.listdir(self.data_folder_path):
            if fname.endswith((".pdf", ".md", ".txt")):
                fpath = os.path.join(self.data_folder_path, fname)
                text = self._extract_text(fpath)
                chunks = self._chunk_text(text, fname)
                self.file_map.update({i + len(self.all_chunks): fname for i in range(len(chunks))})
                self.all_chunks.extend(chunks)

        print(f"[INFO] Total Chunks: {len(self.all_chunks)}")


    def _extract_text(self, file_path):
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            return "\n".join([page.get_text() for page in doc])
        elif file_path.endswith(".md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return markdown2.markdown(f.read())
        elif file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_path.endswith(".json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)  # flatten and pretty-print for chunking
        else:
            raise ValueError("Unsupported file format")
        
    def _chunk_text(self, text, source_file):
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        raw_chunks = splitter.split_text(text)
        return [{"text": chunk, "source": source_file, "chunk_id": i} for i, chunk in enumerate(raw_chunks)]
    

    def _create_embeddings(self):
        index = None
        # Then decide whether to load or build the index
        if os.path.exists("embeddings.index") and os.path.exists("chunks.pkl"):
            print("[INFO] Loading cached FAISS index...")
            index = faiss.read_index("embeddings.index")
            with open("chunks.pkl", "rb") as f:
                self.all_chunks = pickle.load(f)
        else:
            print("[INFO] Generating embeddings and building index...")
            # If needed, prepare chunks here or earlier in the script
            embeddings = self._embed_chunks(self.all_chunks, self.model)
            index = self._build_embeddings_database(embeddings)
            faiss.write_index(self.index, "embeddings.index")
            with open("chunks.pkl", "wb") as f:
                pickle.dump(self.all_chunks, f)
        
        return index


    def _embed_chunks(self):
        texts = [chunk["text"] for chunk in self.all_chunks]
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True, batch_size=32)
    

    def _build_embeddings_database(self, embeddings):
        index = faiss.IndexFlatL2(self.vector_dim)
        index.add(np.array(embeddings))
        return index
    
    def get_top_k_chunks(self, question, index, k=5):
        question_vec = self.model.encode([question])[0]
        _, I = index.search(np.array([question_vec]), k)
        return [self.all_chunks[i] for i in I[0]]