import re
from typing import List, Dict, Any

def clean_legal_text(text: str) -> str:
    """Clean and normalize legal text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and citations patterns
    text = re.sub(r'\[\d+\]|\(\d+\)', '', text)
    
    # Clean up common legal formatting
    text = re.sub(r'(\w+)\s*v\.\s*(\w+)', r'\1 v. \2', text)
    
    return text.strip()

def extract_case_citations(text: str) -> List[str]:
    """Extract legal citations from text"""
    citation_patterns = [
        r'\d+\s+\w+\s+\d+',  # Basic citation pattern
        r'\d+\s+\w+\.?\s*\d*d?\s+\d+',  # Reporter citations
        r'\d+\s+U\.S\.\s+\d+',  # US Reports
        r'\d+\s+S\.Ct\.\s+\d+',  # Supreme Court Reporter
    ]
    
    citations = []
    for pattern in citation_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        citations.extend(matches)
    
    return list(set(citations))

def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    """Extract key legal phrases from text"""
    # Simple keyword extraction - in production use more sophisticated NLP
    legal_terms = [
        'due process', 'reasonable doubt', 'burden of proof', 'prima facie',
        'habeas corpus', 'res judicata', 'stare decisis', 'mens rea',
        'actus reus', 'negligence', 'breach of contract', 'consideration',
        'promissory estoppel', 'statute of limitations', 'injunctive relief'
    ]
    
    found_phrases = []
    text_lower = text.lower()
    
    for term in legal_terms:
        if term in text_lower:
            found_phrases.append(term)
    
    return found_phrases[:max_phrases]

def summarize_case_facts(text: str, max_sentences: int = 3) -> str:
    """Create a brief summary of case facts"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Simple heuristic: prefer sentences with legal keywords
    legal_keywords = ['plaintiff', 'defendant', 'court', 'contract', 'tort', 'negligence']
    
    scored_sentences = []
    for sentence in sentences:
        score = sum(1 for keyword in legal_keywords if keyword.lower() in sentence.lower())
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True)
    top_sentences = [s[1] for s in scored_sentences[:max_sentences]]
    
    return '. '.join(top_sentences) + '.'

def format_legal_citation(case_name: str, citation: str, year: int) -> str:
    """Format a legal citation properly"""
    return f"{case_name}, {citation} ({year})"