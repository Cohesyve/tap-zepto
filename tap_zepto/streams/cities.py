from typing import Optional
from tap_zepto.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class CitiesStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'cities'
    KEY_PROPERTIES = ['cityID']
    REPLICATION_METHOD = 'FULL_TABLE'
    CACHE = True

    @property
    def api_path(self):
        return '/api/v1/filter/city-list'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['data']['cityList']
        ]
