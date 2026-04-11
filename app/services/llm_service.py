from groq import Groq
from typing import Dict, Any
from ..config.settings import GROQ_API_KEY, LLM_FALLBACK


client = Groq(api_key=GROQ_API_KEY)


def call_llm(prompt: str) -> str:
    """Call Groq LLM"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def safe_parse_json(text: str, fallback: Dict[str, Any] = None) -> Dict[str, Any]:
    """Safe JSON parsing for LLM responses with fallback"""
    if fallback is None:
        fallback = LLM_FALLBACK
    
    text = text.replace("```json", "").replace("```", "").strip()
    if not text:
        return fallback
    
    import json
    try:
        return json.loads(text)
    except:
        return fallback
