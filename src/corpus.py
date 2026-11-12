import json
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def clean_text(text):
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\xa0", " ")
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)

def process_raw_documents():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    for filepath in RAW_DIR.glob("*"):
        if filepath.suffix.lower() not in [".txt", ".md"]:
            continue
            
        text = filepath.read_text(encoding="utf-8")
        
        if not text.strip():
            manifest.append({"source": str(filepath), "title": filepath.name, "status": "skipped_empty"})
            continue
            
        cleaned = clean_text(text)
        
        out_path = PROCESSED_DIR / filepath.name
        out_path.write_text(cleaned, encoding="utf-8")
        
        manifest.append({
            "source": str(filepath),
            "title": filepath.name,
            "category": "general",
            "size": len(cleaned),
            "status": "processed"
        })
        
    manifest_path = PROCESSED_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    return manifest

if __name__ == "__main__":
    print("Запуск обработки документов...")
    res = process_raw_documents()
    print(f"Успешно обработано файлов: {len(res)}")
    print("Проверьте папку data/processed")