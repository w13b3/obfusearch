#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ./src/config.py

from __future__ import annotations
from typing import Union, Optional

import json
import logging
import dataclasses
from pathlib import Path

# ./dat/sources.json
DEFAULT_CONFIG = Path(__file__).parent.parent / "dat" / "sources.json"

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _Data:
    exclude_regex: list
    search_engines: list
    rss_feeds: list
    user_agents: list

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class _Configuration:
    _source_path: Union[str, Path] = Path
    _mtime: float = 0
    _data: _Data = _Data

    @property
    def data(self) -> _Data:
        return self._data

    @property
    def source_path(self) -> Path:
        return Path(self._source_path)

    @source_path.setter
    def source_path(self, value: Union[str, Path]) -> None:
        self._source_path = Path(value)

    @staticmethod
    def _object_hook(obj_pairs: list[tuple, ...]) -> _Data:
        """hook for object pairs to `Data` class"""
        return _Data(**dict(obj_pairs))

    def __init__(self, config_json: Optional[Union[str, Path]] = None) -> None:
        """
        :param config_json: json-file like ./dat/sources_template.json
        :type: str or Path
        """
        self._source_path = Path(config_json)

    def __call__(self, config_json: Optional[Union[str, Path]] = None) -> _Data:
        path = Path(config_json or self.source_path)
        # if sources are updated, read in sources again and update _Data
        # this way there is no need to stop the program if the sources are updated
        if self._mtime != path.stat().st_mtime:
            logger.debug('read in the updated config file')
            self._mtime = path.stat().st_mtime
            try:  # read in new data and update only if the json is valid
                data = json.loads(path.read_bytes(), object_pairs_hook=self._object_hook)
                self._data = data
            except json.JSONDecodeError as err:
                logger.exception(err)
        return self.data


# singleton
Configuration = _Configuration(DEFAULT_CONFIG)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(Configuration(DEFAULT_CONFIG))
