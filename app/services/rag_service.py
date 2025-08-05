import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import List, Dict, Any
import json
import os

class RAGService:
    def __init__(self):
        # Use persistent ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        try:
            self.collection = self.client.get_collection("legal_cases")
        except:
            self.collection = self.client.create_collection("legal_cases")
            self._load_initial_data()
    
    def _load_initial_data(self):
        """Load initial legal cases from data files"""
        data_dir = "data/cases"
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(data_dir, filename), 'r') as f:
                        cases = json.load(f)
                        for case in cases:
                            self.add_case(case)
    
    def add_case(self, case: Dict[str, Any]):
        """Add a legal case to the vector database"""
        case_text = f"{case.get('case_name', '')} {case.get('facts', '')} {case.get('holding', '')} {case.get('reasoning', '')}"
        embedding = self.model.encode([case_text])
        
        try:
            self.collection.add(
                embeddings=embedding.tolist(),
                documents=[case_text],
                metadatas=[case],
                ids=[case.get('id', str(hash(case_text)))]
            )
        except Exception as e:
            print(f"Error adding case: {e}")
    
    def search_similar_cases(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar legal cases"""
        try:
            query_embedding = self.model.encode([query])
            
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            return [
                {
                    "case": metadata,
                    "similarity": 1.0,  # ChromaDB doesn't return similarity scores directly
                    "text": document
                }
                for metadata, document in zip(results['metadatas'][0], results['documents'][0])
            ]
        except Exception as e:
            print(f"Error searching cases: {e}")
            return []
    
    def get_context_for_query(self, query: str, topic: str = None) -> List[str]:
        """Get relevant context for a legal query"""
        search_query = f"{topic} {query}" if topic else query
        similar_cases = self.search_similar_cases(search_query, n_results=3)
        
        context = []
        for case in similar_cases:
            case_info = case['case']
            context.append(f"Case: {case_info.get('case_name', 'Unknown')}\n"
                         f"Facts: {case_info.get('facts', '')}\n"
                         f"Holding: {case_info.get('holding', '')}")
        
        return context

rag_service = RAGService()