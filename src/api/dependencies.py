from fastapi import Request


async def get_db(request: Request):
    pool = request.app.state.db_pool

    async with pool.acquire() as conn:
        yield conn
