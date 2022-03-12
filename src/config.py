#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ./src/config.py

from __future__ import annotations
from typing import Union, Optional

import json
import logging
import dataclasses
import importlib.resources as pkg_resources
from pathlib import Path

DEFAULT_CONFIG = "sources.json"

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Data:
    exclude_regex: list
    search_queries: list
    search_engines: list
    rss_feeds: list
    user_agents: list

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class _Configuration:
    _source_path: Union[str, Path] = Path
    _mtime: float = 0
    _data: Data = Data

    @property
    def data(self) -> Data:
        return self._data

    @property
    def source_path(self) -> Path:
        return Path(self._source_path)

    @source_path.setter
    def source_path(self, value: Union[str, Path]) -> None:
        self._source_path = Path(value)

    @staticmethod
    def _object_hook(obj_pairs: list[tuple, ...]) -> Data:
        """hook for object pairs to `Data` class"""
        return Data(**dict(obj_pairs))

    def __init__(self, config_json: Optional[Union[str, Path]] = None) -> None:
        self._source_path = config_json

    def __call__(self, config_json: Optional[Union[str, Path]] = None) -> Data:
        config_json = config_json or self.source_path
        with pkg_resources.path("dat", config_json) as path:
            if self._mtime != path.stat().st_mtime:
                logger.debug('read in the updated config file')
                self._mtime = path.stat().st_mtime
                self._data = json.loads(path.read_bytes(),
                                        object_pairs_hook=self._object_hook)
        return self.data


# singleton
Configuration = _Configuration(DEFAULT_CONFIG)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    a = Configuration()
    print(a)
