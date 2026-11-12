import time
import uuid
import logging
from src.config import APP_MODE, GIGACHAT_CREDENTIALS
from gigachat import GigaChat
from gigachat.models import ChatCompletionRequest, ChatMessage

logger = logging.getLogger(__name__)

def ask_gigachat(messages):
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] Начало запроса к нейросети")
    start_time = time.time()

    if APP_MODE == "mock":
        time.sleep(1)
        answer = '{"category": "network", "priority": "high", "summary": "Не подключается VPN", "recommended_steps": ["Проверить сеть", "Перезапустить клиент"], "needs_human": false}'
        logger.info(f"[{request_id}] Успешный ответ (mock) за {time.time() - start_time:.2f} сек")
        return answer

    if not GIGACHAT_CREDENTIALS:
        raise ValueError("Ошибка: GIGACHAT_CREDENTIALS не задан")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            sdk_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            request = ChatCompletionRequest(messages=sdk_messages)
            
            with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False, model="GigaChat-2") as client:
                response = client.chat.create(request)
                content = response.messages[0].content
                
                if isinstance(content, list):
                    content = "".join([c.text for c in content if hasattr(c, 'text')])
                
                logger.info(f"[{request_id}] Успешный ответ за {time.time() - start_time:.2f} сек")
                return str(content)
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return f"Ошибка при запросе: {e}"