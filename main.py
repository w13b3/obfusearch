#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ./main.py

from __future__ import annotations
from typing import *
from collections.abc import *
from pathlib import Path

import asyncio
import logging
import random
from itertools import count

import httpx
from httpx import Response, AsyncClient

from src import rsstopics
from src import webconnect
from src.config import Configuration


logger = logging.getLogger(__name__)
counter = count()


def chunk(seq: Iterable, num: int):
    seq = iter(seq)
    while True:
        try:
            res = []
            for _ in range(num):
                res.append(next(seq))
            yield res
        except StopIteration:
            break


async def log_request(request: httpx.Request) -> None:
    logger.info(f"Request {next(counter)}: {request.url}")


async def log_response(response: httpx.Response) -> None:
    logger.info(f"Response HTTP {response.status_code}: {response.url}")


async def navigate(lock, client, url, **opts) -> Response:
    async with lock:
        await asyncio.sleep(random.randrange(5, 35))
        return await webconnect.navigate(client, url, **opts)


async def main(config_json: Optional[Union[str, Path]] = None) -> None:
    lock = asyncio.Semaphore(value=2)  # total connections
    event_hooks = {'request': [log_request], 'response': [log_response]}
    client: AsyncClient = httpx.AsyncClient(http2=True, event_hooks=event_hooks, follow_redirects=True)
    while True:
        try:
            # chop the received topics in chunks
            for topics in chunk(rsstopics.get_topics(config_json), 10):
                tasks = []
                for topic in topics:
                    c = Configuration(config_json)
                    url = webconnect.create_query_url(
                        random.choice(c.search_engines),
                        topic
                    )
                    user_agent = random.choice(Configuration(config_json).user_agents)
                    tasks.append(
                        asyncio.create_task(navigate(lock, client, url.strip(), headers={'User-Agent': user_agent}))
                    )
                    await asyncio.sleep(random.randrange(2, 5))

                for awaitable in asyncio.as_completed(tasks):
                    resp: Response = await awaitable
                    logger.info(f"visited {resp.url}")
                    logger.info(f"received {len(resp.content)} bytes of content")

        except KeyboardInterrupt:
            break
        except Exception as err:
            logger.exception(err)

    await client.aclose()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s_%(levelname)s %(name)s %(funcName)s: %(message)s')
    asyncio.run(main())
