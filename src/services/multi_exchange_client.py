import requests


class MultiExchangeClient:
    def __init__(self, api_urls: list[str]):
        self.api_urls = api_urls

    def get_exchange_rate(self, base: str, target: str) -> float | None:
        for api_url in self.api_urls:
            try:
                print(f"Пробуем {api_url}")
                response = requests.get(f"{api_url}/{base}", timeout=5)
                response.raise_for_status()

                data = response.json()

                rate = data.get("rates", {}).get(target)

                if rate is not None:
                    print(f"Курс получен: {rate}")
                    return rate

            except requests.RequestException as e:
                print(f"API {api_url} недоступен: {e}")
                continue
        return None


if __name__ == "__main__":
    client = MultiExchangeClient(
        [
            "http://127.0.0.1:9998",
            "http://127.0.0.1:9999",
        ]
    )

    rate = client.get_exchange_rate("USD", "RUB")
    print(f"Результат: {rate}")
