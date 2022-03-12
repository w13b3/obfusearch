#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ./src/rsstopics.py

from __future__ import annotations
from typing import *
from collections.abc import *
from pathlib import Path

import re
import random
import logging
from functools import partial
from concurrent.futures import ThreadPoolExecutor

import feedparser
from feedparser import FeedParserDict

from src import config
from src.config import Configuration


logger = logging.getLogger(__name__)


def bad_topic(topic: str, exclude_patterns: Sequence[str]) -> bool:
    """check if the `topic` is bad with the patterns in the `exclude_patterns` sequence
    returns True if the `topic` is bad
    """
    f = partial(re.search, string=topic.strip(), flags=re.IGNORECASE)
    return any(map(f, exclude_patterns))


def get_topics(config_json: Optional[Union[str, Path]] = None) -> Iterator[str]:
    data = Configuration(config_json)

    feeds = data.rss_feeds[:]  # copy of the rss_feeds
    random.shuffle(feeds)  # shuffle the feeds in-place

    # request all the feeds
    with ThreadPoolExecutor() as exc:
        f = partial(feedparser.parse, agent=random.choice(data.user_agents))
        results = exc.map(f, feeds)

    rss: FeedParserDict   # create a generator that returns every title
    topics: Generator[str] = (str(entry.title) for rss in results for entry in rss.entries)
    f = partial(bad_topic, exclude_patterns=data.exclude_regex)  # filter on bad topics
    for topic in filter(f, topics):
        logger.info(f'Topic: {topic}')
        yield topic


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    for item in get_topics(config.DEFAULT_CONFIG):
        print(item)

