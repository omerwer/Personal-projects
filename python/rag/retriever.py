import os
import json
import pickle
import markdown2
import numpy as np

from sentence_transformers import SentenceTransformer
import fitz # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss


class Retriever:
    """
    A class responsible for loading, chunking, embedding, and indexing documents for retrieval.

    Attributes:
        data_folder_path (str): Path to the directory containing the documents.
        all_chunks (list): List of all text chunks extracted from the documents.
        model (SentenceTransformer): text embedding model.
        vector_dim (int): Embedding vectors dimension.

    Methods:
        get_chunks(): Returns the list of all extracted text chunks.
        pre_retrieval(): Loads documents, extracts and chunks text, and prepares the FAISS (Facebook AI Similarity Serach) index.
        get_top_k_chunks(question, index, k=NUM): Returns the top-k most relevant chunks for a query.
    """

    def __init__(self, data_folder_path, embedding_model_name="intfloat/e5-small-v2", embedding_vector_dim=384, device="cpu"):
        self.data_folder_path = data_folder_path
        self.all_chunks = []

        os.makedirs("./sentence_transformer", exist_ok=True)
        os.makedirs("./assets", exist_ok=True)

        self.model = SentenceTransformer(embedding_model_name, device=device, trust_remote_code=True, cache_folder="./sentence_transformer")

        self.vector_dim = embedding_vector_dim

    def get_chunks(self):
        return self.all_chunks

    def pre_retrieval(self):
        self._load_files_and_extract_data()
        return self._create_embeddings()


    def _load_files_and_extract_data(self):
        """
        Loads and processes files from the specified data folder.
        Extracts text and splits it into manageable chunks.
        Supports .pdf, .md, .txt, and .json file formats.
        """

        print("[INFO] Loading and processing documents...")
        for file_name in os.listdir(self.data_folder_path):
            if file_name.endswith((".pdf", ".md", ".txt")):
                file_path = os.path.join(self.data_folder_path, file_name)
                text = self._extract_text(file_path)
                chunks = self._chunk_text(text, file_name)
                self.all_chunks.extend(chunks)

        print(f"[INFO] Total Chunks: {len(self.all_chunks)}")


    def _extract_text(self, file_path):
        """
        Extracts raw text from a supported file format.

        Args:
            file_path (str): Full path to the document.

        Returns:
            str: Extracted text content.
        """

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
                return json.dumps(data, indent=2)
        else:
            raise ValueError("Unsupported file format")
        
    def _chunk_text(self, text, source_file):
        """
        Splits text into overlapping chunks using LangChain's RecursiveCharacterTextSplitter.

        Args:
            text (str): The full text to chunk.
            source_file (str): Source file name to tag each chunk.

        Returns:
            List[dict]: A list of dicts where there is one dict for each chunk'.
        """

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        raw_chunks = splitter.split_text(text)
        return [{"text": chunk, "source": source_file, "chunk_id": i} for i, chunk in enumerate(raw_chunks)]
    

    def _create_embeddings(self):
        """
        Creates or loads a FAISS index of embeddings for all text chunks for similarity matching.

        If cached index and chunk files exist in the `./assets` directory,
        it loads them directly to avoid recomputation. Otherwise, it generates
        embeddings using the SentenceTransformer model and builds a new FAISS index,
        which is then saved for future use.

        Returns:
            faiss.Index: A FAISS index containing vector representations of the text chunks.

        Side Effects:
            - Loads or saves the FAISS index to './assets/embeddings.index'.
            - Loads or saves chunk metadata to './assets/chunks.pkl'.
        """

        index = None
        if os.path.exists("./assets/embeddings.index") and os.path.exists("./assets/chunks.pkl"):
            print("[INFO] Loading cached FAISS index...")
            index = faiss.read_index("./assets/embeddings.index")
            with open("./assets/chunks.pkl", "rb") as f:
                self.all_chunks = pickle.load(f)
        else:
            print("[INFO] Generating embeddings and building index...")
            embeddings = self._embed_chunks()
            index = self._build_embeddings_database(embeddings)
            faiss.write_index(index, "./assets/embeddings.index")
            with open("./assets/chunks.pkl", "wb") as f:
                pickle.dump(self.all_chunks, f)
        
        return index


    def _embed_chunks(self):
        """
        Embeds all currently loaded chunks using the embedding model.

        Returns:
            np.ndarray: The text embeddings.
        """

        texts = [chunk["text"] for chunk in self.all_chunks]
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True, batch_size=32)
    

    def _build_embeddings_database(self, embeddings):
        """
        Builds and returns a FAISS index using the provided embeddings.

        Args:
            embeddings (np.ndarray): Numpy array of chunk embeddings.

        Returns:
            faiss.Index: A FAISS index for similarity search.
        """

        index = faiss.IndexFlatL2(self.vector_dim)
        index.add(np.array(embeddings))
        return index
    
    def get_top_k_chunks(self, question, index, k=5):
        """
        Returns the top k chunks with the highest similarity.

        Args:
            embeddings (np.ndarray): Numpy array of chunk embeddings.

        Returns:
            faiss.Index: A FAISS index for similarity search.
        """

        question_vec = self.model.encode([question])[0]
        _, I = index.search(np.array([question_vec]), k)
        return [self.all_chunks[i] for i in I[0]]