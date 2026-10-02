from time import perf_counter

import httpx

URL = "http://127.0.0.1:8000/products?limit=10&offset=0"


def measure_request(client):
    start = perf_counter()

    response = client.get(URL)
    response.raise_for_status()
    elapsed = perf_counter() - start

    return elapsed


with httpx.Client() as client:
    cold_request_time = measure_request(client)
    print(f"Холодный запрос: {cold_request_time:.2f} сек")

    for request_number in range(1, 6):
        elapsed = measure_request(client)
        print(f"Прогретый запрос №{request_number}: {elapsed:.3f} сек.")
