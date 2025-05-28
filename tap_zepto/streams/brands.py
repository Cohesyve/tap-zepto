from tap_zepto.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class BrandsStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'brands'
    KEY_PROPERTIES = ['id']
    CACHE = True

    @property
    def api_path(self):
        return '/api/v1/brands'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['brands']
        ]
