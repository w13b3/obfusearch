#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ./src/webconnect.py

from __future__ import annotations
from collections.abc import AsyncIterable, Sequence
from typing import Optional

import asyncio
import logging
from urllib.parse import quote

import httpx
from httpx import Request, Response, AsyncClient


logger = logging.getLogger(__name__)


def create_query_url(search_engine: str, query: str) -> str:
    query = quote(str(query))
    try:
        return str(search_engine) % query
    except TypeError:
        logger.error(f"couldn't join {search_engine!r} and {query!r}")
        return str(search_engine)


async def navigate(client: AsyncClient,
                       url: str,
                       **client_opts: Optional
                       ) -> Response:
    resp = Response(404, content=b'', request=Request('GET', url))
    try:
        # follow_redirects option is default False
        resp: Response = await client.get(url, **client_opts)
        resp.raise_for_status()
    except httpx.HTTPError as err:
        logger.error(f"couldn't open: {err.request.url!r}")
    return resp


async def iter_web_content(urls: Sequence[str],
                           http2: bool = False,
                           **client_opts: Optional
                           ) -> AsyncIterable[Response]:
    async with httpx.AsyncClient(http2=http2) as client:
        client: httpx.AsyncClient
        for url in urls:
            resp = await navigate(client, url, **client_opts)
            if resp.is_error:
                continue  # next url in for-loop
            else:
                yield resp



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    async def main():
        urls = ['https://www.example.com', 'https://python.org']
        async for resp in iter_web_content(urls, follow_redirects=True):
            print(resp.content)


    asyncio.run(main())
