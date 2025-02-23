from fastapi import Request, HTTPException
from redis import Redis, RedisError
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging

logger = logging.getLogger(__name__)

# Создаем функцию для получения Redis клиента
def get_redis_client():
    return Redis(
        host=os.getenv('REDIS_HOST', 'redis'),  # Используем имя сервиса по умолчанию
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True,
        socket_connect_timeout=2,  # Таймаут подключения
        socket_timeout=2,  # Таймаут операций
        retry_on_timeout=True,  # Повторять при таймауте
        max_connections=10  # Максимум соединений
    )

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        times: int = 100,
        seconds: int = 60,
        exclude_paths: set = None
    ):
        super().__init__(app)
        self.times = times
        self.seconds = seconds
        self.exclude_paths = exclude_paths or set()
        self.redis_client = get_redis_client()

    async def dispatch(self, request: Request, call_next):
        # Пропускаем исключенные пути
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        try:
            # Получаем IP клиента
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"

            # Пробуем выполнить операции с Redis
            try:
                requests = self.redis_client.incr(key)
                if requests == 1:
                    self.redis_client.expire(key, self.seconds)
                ttl = self.redis_client.ttl(key)
            except RedisError as e:
                logger.error(f"Redis error: {e}")
                # При ошибке Redis пропускаем запрос
                return await call_next(request)

            # Проверяем лимит
            if requests > self.times:
                headers = {
                    "X-RateLimit-Limit": str(self.times),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(ttl),
                    "Retry-After": str(ttl)
                }
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers=headers
                )

            response = await call_next(request)

            # Добавляем заголовки в ответ
            response.headers["X-RateLimit-Limit"] = str(self.times)
            response.headers["X-RateLimit-Remaining"] = str(max(self.times - requests, 0))
            response.headers["X-RateLimit-Reset"] = str(ttl)

            return response

        except Exception as e:
            logger.error(f"Unexpected error in rate limit middleware: {e}")
            # При любой другой ошибке пропускаем запрос
            return await call_next(request)