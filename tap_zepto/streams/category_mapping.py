from tap_zepto.streams.base import BaseStream
from tap_zepto.cache import stream_cache

import singer
import json

LOGGER = singer.get_logger()  # noqa


class CategoryMappingStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'category_mapping'
    KEY_PROPERTIES = ['categoryId']
    REPLICATION_METHOD = 'FULL_TABLE'
    CACHE = True

    @property
    def api_path(self):
        return '/api/v1/commons/brand-category-mapping'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['data']['brandCategoryList'][0]['categoryList']
        ]
