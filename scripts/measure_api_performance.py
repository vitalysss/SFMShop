import socket
import time
from urllib.parse import urlparse

import requests


def measure_api_performance(url: str) -> dict:
    """Измерить производительность API endpoint."""

    hostname = urlparse(url).hostname

    if hostname is None:
        raise ValueError("Не удалось определить hostname из URL.")

    dns_start = time.time()
    ip_address = socket.gethostbyname(hostname)
    dns_time = time.time() - dns_start

    request_start = time.time()
    response = requests.get(url, timeout=10)
    total_time = time.time() - request_start

    server_time = response.elapsed.total_seconds()
    download_time = max(total_time - server_time, 0.0)
    response_size = len(response.content)

    results = {
        "dns_time": dns_time,
        "server_time": server_time,
        "download_time": download_time,
        "total_time": total_time,
        "status_code": response.status_code,
        "response_size": response_size,
    }

    print(f"IP-адрес: {ip_address}")
    print(f"DNS-запрос: {dns_time:.4f} сек.")
    print(f"Время до заголовков: {server_time:.4f} сек.")
    print(f"Загрузка тела ответа: {download_time:.4f} сек.")
    print(f"Общее время: {total_time:.4f} сек.")
    print(f"HTTP-статус: {response.status_code}")
    print(f"Размер ответа: {response_size} байт")

    return results


if __name__ == "__main__":
    measure_api_performance("http://localhost:8000/products?limit=10&offset=0")
