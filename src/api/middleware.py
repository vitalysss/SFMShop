import time

from fastapi import Request

from src.services.log_service import log_service


async def log_requests(request: Request, call_next):
    start_time = time.time()
    log_service.info(
        "Запрос: %s %s",
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        process_time = time.time() - start_time

        log_service.exception(
            "Ошибка запроса: %s %s, время: %.3f секунд",
            request.method,
            request.url.path,
            process_time,
        )

        raise

    process_time = time.time() - start_time

    if response.status_code >= 500:
        log_service.error(
            "Ответ: %s, время %.3f секунд",
            response.status_code,
            process_time,
        )
    elif response.status_code >= 400:
        log_service.warning(
            "Ответ: %s, время %.3f секунд",
            response.status_code,
            process_time,
        )
    else:
        log_service.info(
            "Ответ: %s, время %.3f секунд",
            response.status_code,
            process_time,
        )

    response.headers["X-Process-Time"] = str(process_time)

    return response
