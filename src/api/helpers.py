from src.services.cache_service import invalidate_product_cache
from src.services.log_service import save_log


def invalidate_cache_safely(product_id: int) -> None:
    try:
        invalidate_product_cache(product_id)
    except Exception as error:
        print("Не удалось очистить Redis-кэш:", error)


def write_log_safely(log_data: dict) -> None:
    try:
        save_log(log_data)
    except Exception as error:
        print("Не удалось записать лог для MongoDB", error)
