from tap_zepto.streams.base import BaseStream
from tap_zepto.cache import stream_cache

import singer
import json
import pandas as pd
import io
import requests

LOGGER = singer.get_logger()  # noqa


class ProductPerformanceStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'product_performance'
    KEY_PROPERTIES = ['productVariantId', 'startDate', 'endDate']
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'startDate'

    @property
    def api_path(self):
        return '/brand-analytics-web/api/v1/sales-analytics/product-performance'
    
    def get_params(self):

        all_subcategories = []
        for category in stream_cache.get('category_mapping', []):
            for sub_category in category.get('subcategoryList', []):
                all_subcategories.append({
                    'subCategoryID': sub_category['subcategoryID'],
                    'subCategoryName': sub_category['subcategoryName']
                })

        return {
            'startDate': "2025-01-01",
            'endDate': "2025-05-26",
            'brandIds': ','.join(brand['id'] for brand in stream_cache.get('brands', [])),
            'brandNames': ','.join(brand['name'] for brand in stream_cache.get('brands', [])),
            'subCategoryIds': ','.join(subcategory['subCategoryID'] for subcategory in all_subcategories),
            'subCategoryNames': '|'.join(subcategory['subCategoryName'] for subcategory in all_subcategories),
            'cityIds': ','.join(city['cityID'] for city in stream_cache.get('cities', [])),
        }

    def get_stream_data(self, result):
        params = self.get_params()
        start_date = params['startDate']
        end_date = params['endDate']

        return [
            self.transform_record(
            {**record, 'startDate': start_date, 'endDate': end_date}
            )
            for record in result['data']['data']
        ]
