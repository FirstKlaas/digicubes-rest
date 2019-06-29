import asyncio
from typing import Any

def init(api):

    @api.route("/user/{id}")
    async def moin(req, resp, *, id):
        resp.text = f"user, {id}"
