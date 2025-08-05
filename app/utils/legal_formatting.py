from typing import Dict, Any, List

def format_irac_analysis(analysis: Dict[str, Any]) -> str:
    """Format IRAC analysis for display"""
    template = """
**ISSUE:**
{issue}

**RULE:**
{rule}

**APPLICATION:**
{application}

**CONCLUSION:**
{conclusion}

**KEY FACTS:**
{key_facts}

**LEGAL PRINCIPLES:**
{legal_principles}
"""
    
    key_facts = '\n'.join([f"• {fact}" for fact in analysis.get('key_facts', [])])
    legal_principles = '\n'.join([f"• {principle}" for principle in analysis.get('legal_principles', [])])
    
    return template.format(
        issue=analysis.get('issue', 'Not identified'),
        rule=analysis.get('rule', 'Not identified'),
        application=analysis.get('application', 'Not provided'),
        conclusion=analysis.get('conclusion', 'Not reached'),
        key_facts=key_facts or 'None identified',
        legal_principles=legal_principles or 'None identified'
    )

def format_case_brief(case: Dict[str, Any]) -> str:
    """Format a case brief for display"""
    template = """
**{case_name}**
{citation} ({year})

**FACTS:**
{facts}

**ISSUE:**
{issue}

**HOLDING:**
{holding}

**REASONING:**
{reasoning}

**RULE:**
{rule}
"""
    
    return template.format(
        case_name=case.get('case_name', 'Unknown Case'),
        citation=case.get('citation', 'Citation not available'),
        year=case.get('year', 'Year unknown'),
        facts=case.get('facts', 'Facts not provided'),
        issue=case.get('issue', 'Issue not identified'),
        holding=case.get('holding', 'Holding not provided'),
        reasoning=case.get('reasoning', 'Reasoning not provided'),
        rule=case.get('rule', 'Rule not identified')
    )

def format_legal_outline(topic: str, subtopics: List[str]) -> str:
    """Format a legal topic outline"""
    outline = f"# {topic}\n\n"
    
    for i, subtopic in enumerate(subtopics, 1):
        outline += f"{i}. {subtopic}\n"
    
    return outline

def format_statute_reference(statute: Dict[str, Any]) -> str:
    """Format a statute reference"""
    return f"{statute.get('title', 'Unknown Statute')} § {statute.get('section', 'N/A')} ({statute.get('jurisdiction', 'Unknown')} {statute.get('year', '')})"

def format_legal_question(question: str, answer: str, explanation: str = "") -> str:
    """Format a legal Q&A for educational purposes"""
    formatted = f"**Q:** {question}\n\n**A:** {answer}"
    
    if explanation:
        formatted += f"\n\n**Explanation:** {explanation}"
    
    return formatted