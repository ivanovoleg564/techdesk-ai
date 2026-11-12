import json
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")

def split_into_chunks(text, chunk_size=800, overlap=120):
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть больше 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap должен быть от 0 до chunk_size - 1")

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space != -1 and (end - last_space) < 100:
                end = last_space
                
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
            
        if end == len(text):
            break
            
        start = end - overlap
    return chunks

def build_chunks():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    chunks_file = CHUNKS_DIR / "chunks.jsonl"
    
    total_docs = 0
    total_chunks = 0
    empty_chunks = 0
    duplicate_chunks = 0
    min_size = 999999
    max_size = 0
    seen_texts = set()
    
    with open(chunks_file, "w", encoding="utf-8") as f:
        for filepath in PROCESSED_DIR.glob("*"):
            if filepath.name == "manifest.json" or not filepath.is_file():
                continue
                
            total_docs += 1
            text = filepath.read_text(encoding="utf-8")
            parts = split_into_chunks(text)
            
            for index, part in enumerate(parts):
                if not part.strip():
                    empty_chunks += 1
                    continue
                    
                if part in seen_texts:
                    duplicate_chunks += 1
                seen_texts.add(part)
                
                size = len(part)
                if size < min_size: min_size = size
                if size > max_size: max_size = size
                
                chunk_data = {
                    "chunk_id": f"{filepath.stem}_{index}",
                    "source": str(filepath),
                    "title": filepath.name,
                    "category": "general",
                    "chunk_index": index,
                    "text": part
                }
                
                f.write(json.dumps(chunk_data, ensure_ascii=False) + "\n")
                total_chunks += 1

    report = {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "empty_chunks": empty_chunks,
        "duplicate_chunks": duplicate_chunks,
        "min_chunk_size": min_size if total_chunks > 0 else 0,
        "max_chunk_size": max_size if total_chunks > 0 else 0
    }
    
    report_file = CHUNKS_DIR / "report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    return report

if __name__ == "__main__":
    print("Запуск разбивки на фрагменты...")
    res = build_chunks()
    print(f"Готово! Обработано документов: {res['total_documents']}")
    print(f"Создано фрагментов: {res['total_chunks']}")
    print("Проверьте папку data/chunks")