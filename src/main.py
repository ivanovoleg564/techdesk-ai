from src.llm_client import ask_gigachat
from src.prompts import load_prompt
from src import history
from src.logging_config import setup_logging
from src.schemas import parse_ticket_analysis
from src.corpus import process_raw_documents
from src.chunking import build_chunks
import json
from pathlib import Path

def chat_session(is_new=True):
    if is_new:
        history.start_new_session()
    else:
        session_id = input("Введите ID сессии: ").strip()
        if history.load_session(session_id):
            print("Сессия успешно загружена!")
        else:
            print("Сессия не найдена. Создана новая.")
            history.start_new_session()
            
    print(f"Ваш ID сессии: {history.current_session_id}")
    print("Источник ответа: без поиска по корпусу (retrieval будет добавлен позже).")
    print("Введите /exit для выхода, /reset для очистки истории.\n")
    
    system_prompt = load_prompt("system.txt")
    
    while True:
        user_input = input("Вы: ")
        
        if user_input.lower() == "/exit":
            print("Возврат в главное меню.")
            break
        elif user_input.lower() == "/reset":
            history.reset_history()
            print("Бот: История очищена.\n")
            history.save_session()
            continue
        
        if not user_input.strip():
            continue
            
        messages = history.get_messages_for_request(system_prompt, user_input)
        
        max_attempts = 2
        for attempt in range(max_attempts):
            print("Бот думает...")
            answer = ask_gigachat(messages)
            
            if answer.startswith("Ошибка при запросе:"):
                print(f"Бот: {answer}\n")
                answer_to_save = answer
                break

            try:
                analysis = parse_ticket_analysis(answer)
                print(f"Бот (Категория: {analysis.category}, Приоритет: {analysis.priority}):")
                print(f"Проблема: {analysis.summary}")
                print("Шаги решения:")
                for step in analysis.recommended_steps:
                    print(f"- {step}")
                print(f"Нужен человек: {'Да' if analysis.needs_human else 'Нет'}\n")
                answer_to_save = answer
                break
                
            except ValueError as e:
                if attempt == 0:
                    print("Нейросеть ошиблась в формате. Просим исправить...")
                    messages.append({"role": "assistant", "content": answer})
                    messages.append({"role": "user", "content": f"Ты вернул неверный JSON. Ошибка: {e}. Верни ТОЛЬКО правильный JSON с полями category, priority, summary, recommended_steps, needs_human."})
                else:
                    print(f"Бот: {answer}\n")
                    print(f"Система: Данные так и не прошли проверку.\n")
                    answer_to_save = "Ошибка валидации"
        
        history.add_message("user", user_input)
        history.add_message("assistant", answer_to_save)
        history.save_session()

def show_stats():
    report_path = Path("data/chunks/report.json")
    if not report_path.exists():
        print("Статистика не найдена. Сначала подготовьте корпус.\n")
        return
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    print("\n--- Статистика корпуса ---")
    print(f"Всего документов: {report.get('total_documents', 0)}")
    print(f"Всего фрагментов: {report.get('total_chunks', 0)}")
    print(f"Мин. размер фрагмента: {report.get('min_chunk_size', 0)} символов")
    print(f"Макс. размер фрагмента: {report.get('max_chunk_size', 0)} символов")
    print("--------------------------\n")

def main():
    setup_logging()
    while True:
        print("=== TechDesk AI ===")
        print("1. Начать новый чат")
        print("2. Продолжить сессию")
        print("3. Подготовить корпус (очистка + нарезка)")
        print("4. Показать статистику корпуса")
        print("5. Выход")
        
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "1":
            chat_session(is_new=True)
        elif choice == "2":
            chat_session(is_new=False)
        elif choice == "3":
            print("Очистка документов...")
            process_raw_documents()
            print("Нарезка на фрагменты...")
            res = build_chunks()
            print(f"Готово! Создано фрагментов: {res['total_chunks']}\n")
        elif choice == "4":
            show_stats()
        elif choice == "5":
            print("До свидания!")
            break
        else:
            print("Неверный ввод. Попробуйте снова.\n")

if __name__ == "__main__":
    main()