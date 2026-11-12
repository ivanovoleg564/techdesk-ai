from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(filename: str) -> str:
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Ошибка: Файл шаблона не найден -> {filepath}")
    return filepath.read_text(encoding="utf-8")

def render_prompt(question: str, context: str = "") -> str:
    template = load_prompt("ticket_analysis.txt")
    try:
        return template.format(question=question, context=context)
    except KeyError as e:
        raise KeyError(f"Ошибка: В шаблоне не хватает переменной {e}")