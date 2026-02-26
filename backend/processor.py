import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ESGImpact(BaseModel):
    category: str
    impact_score: int
    justification: str

class NewsAnalysis(BaseModel):
    summary: str
    impacts: List[ESGImpact]
    source_reliability: float

def analyze_news_content(raw_text: str):
    print(f"⚡ Using Groq AI (Llama 3.3) for analysis...")
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior ESG analyst. Analyze the text and return ONLY a valid JSON object matching this structure: {'summary': '...', 'impacts': [{'category': '...', 'impact_score': 0, 'justification': '...'}], 'source_reliability': 0.0}"
                },
                {"role": "user", "content": f"Analyze: {raw_text[:6000]}"}
            ],
            model="llama-3.3-70b-versatile", # UPDATED MODEL NAME
            response_format={"type": "json_object"}
        )

        result_json = json.loads(chat_completion.choices[0].message.content)
        
        # We validate with Pydantic, but return a DICT for the database
        validated_data = NewsAnalysis(**result_json)
        return validated_data.model_dump() # Convert to dict here!

    except Exception as e:
        print(f"❌ Groq Error: {e}")
        # Fallback dictionary (not an object) so the database can save it
        return {
            "summary": "AI Analysis Fallback: Technical limit reached.",
            "impacts": [{"category": "General", "impact_score": 0, "justification": "API Quota or Model Error."}],
            "source_reliability": 0.5
        }