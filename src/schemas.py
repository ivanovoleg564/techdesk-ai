import json
import re
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError, field_validator

class TicketAnalysis(BaseModel):
    category: Literal["access", "network", "software", "hardware", "other"]
    priority: Literal["low", "normal", "high", "critical"]
    summary: str = Field(min_length=5, max_length=160)
    recommended_steps: List[str] = Field(min_length=1, max_length=5)
    needs_human: bool

    @field_validator('recommended_steps', mode='before')
    @classmethod
    def extract_steps(cls, v):
        if isinstance(v, list):
            result = []
            for item in v:
                if isinstance(item, dict):
                    text = item.get("step") or item.get("description") or item.get("action") or item.get("explanation") or str(item)
                    result.append(text)
                else:
                    result.append(str(item))
            return result
        return v

    @field_validator('category', mode='before')
    @classmethod
    def fix_category(cls, v):
        v_lower = str(v).lower()
        if v_lower in ["access", "network", "software", "hardware", "other"]:
            return v_lower
            
        if "vpn" in v_lower or "сеть" in v_lower or "сети" in v_lower: return "network"
        if "пароль" in v_lower or "доступ" in v_lower: return "access"
        if "программа" in v_lower or "по" in v_lower or "софт" in v_lower: return "software"
        if "принтер" in v_lower or "компьютер" in v_lower or "железо" in v_lower: return "hardware"
        return "other"

    @field_validator('priority', mode='before')
    @classmethod
    def fix_priority(cls, v):
        v_lower = str(v).lower()
        if v_lower in ["low", "normal", "high", "critical"]:
            return v_lower
            
        if "средн" in v_lower: return "normal"
        if "высок" in v_lower or "критич" in v_lower: return "high"
        if "низк" in v_lower: return "low"
        return "normal"

def parse_ticket_analysis(text: str) -> TicketAnalysis:
    if not isinstance(text, str):
        raise ValueError(f"Ожидалась строка, но получено: {type(text)}")
    clean_text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\s*```$', '', clean_text)
    clean_text = clean_text.strip()
    try:
        return TicketAnalysis.model_validate_json(clean_text)
    except (ValidationError, json.JSONDecodeError) as e:
        raise ValueError(f"Ошибка валидации: {e}")