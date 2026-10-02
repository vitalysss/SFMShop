import asyncio

import httpx


class ExternalAPIService:
    def __init__(
        self,
        client: httpx.AsyncClient,
        retries: int = 3,
    ):
        self.client = client
        self.retries = retries

    async def get_exchange_rate(
        self,
        base: str,
        target: str,
    ) -> float:
        url = "https://api.frankfurter.app/latest"

        for attempt in range(self.retries):
            try:
                response = await self.client.get(
                    url,
                    params={
                        "from": base.upper(),
                        "to": target.upper(),
                    },
                    timeout=5.0,
                )
                response.raise_for_status()

                data = response.json()
                rate = data["rates"].get(target.upper())

                if rate is None:
                    raise ValueError("Курс валюты отсутствует в ответе API")

                return float(rate)

            except (
                httpx.RequestError,
                httpx.HTTPStatusError,
                ValueError,
                KeyError,
            ):
                if attempt == self.retries - 1:
                    raise

                await asyncio.sleep(2**attempt)

        raise RuntimeError("Не удалось получить курс валют")
