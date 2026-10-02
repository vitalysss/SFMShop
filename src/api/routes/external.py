import httpx
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)

from src.api.auth import TokenData, get_current_user
from src.api.schemas import ExchangeRateResponse
from src.services.external_api_service import ExternalAPIService

router = APIRouter(tags=["external"])


@router.get(
    "/exchange-rate",
    response_model=ExchangeRateResponse,
)
async def get_exchange_rate(
    request: Request,
    base: str = Query(min_length=3, max_length=3),
    target: str = Query(min_length=3, max_length=3),
    current_user: TokenData = Depends(get_current_user),
):
    service = ExternalAPIService(request.app.state.http_client)

    try:
        rate = await service.get_exchange_rate(
            base,
            target,
        )
    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис курсов валют временно недоступен",
        )

    return ExchangeRateResponse(
        base=base.upper(),
        target=target.upper(),
        rate=rate,
    )
