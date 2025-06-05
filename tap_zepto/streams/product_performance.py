from urllib.parse import quote
from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache

import singer
import json
import pandas as pd
import io
import requests

LOGGER = singer.get_logger()  # noqa


class ProductPerformanceStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'product_performance'
    KEY_PROPERTIES = ['productVariantId', 'startDate', 'endDate']
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'startDate'

    @property
    def api_path(self):
        return '/brand-analytics-web/api/v1/sales-analytics/product-performance'
    # 'https://fcc.zepto.co.in/brand-analytics-web/api/v1/sales-analytics/product-performance'
    # 'https://fcc.zepto.co.in/brand-analytics-web/api/v1/sales-analytics/product-performance'
    
    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}?offset={int(skip)}&limit={int(count)}"
        return url

    def get_headers(self):
        return {
            "x-proxy-target":"brand-analytics"
        }
    
    def get_params(self):

        all_subcategories = []
        for category in stream_cache.get('category_mapping', []):
            for sub_category in category.get('subcategoryList', []):
                all_subcategories.append({
                    'subCategoryID': sub_category['subcategoryID'],
                    'subCategoryName': sub_category['subcategoryName']
                })

        # return { 

        #         'viewType': 'top_selling',
        #         'startDate': '2025-01-01',
        #         'endDate': '2025-05-26',
        #         'brandIds': '4ef6e491-1881-4f88-866c-144c8e26def7',
        #         'brandNames': 'Ecosys',
        #         'subcategoryIds': 'd22a9423-0063-4102-9f09-57e79ff030e3,dfb37880-b40f-4783-9502-a56e12edbabc',
        #         'subcategoryNames': 'Floor%20&%20Surface%20Cleaners|Liquid%20Detergents%20&%20Additives',
        #         'cityIds': 'facade53-8330-4ebe-b07e-55319220a301,449216c9-1760-4194-a9d4-06f5b3ddb7db,81f24084-8358-4d11-8b79-1acd7efd6a91,7e926d2f-adad-4e5a-956f-f07fffa54164,98141024-d057-49da-a307-82d88308db5d,963e4758-abc3-4766-a26c-bdc4d0c30bd2,c5b3d670-f20e-4cae-a6b7-42e17b8fb08d,f938d139-3cb7-4b78-8980-b88178659225,58b4b3e5-572d-491d-a9a3-66a5560e4291,82c98de3-2610-47d9-ab70-251330bcb704,15862867-2c01-4699-8cfe-2a2d19bee4f1,3eb31521-2060-4beb-b6fb-18ba88b6adda'
        #     }
                
        

        return {
            'viewType': 'top_selling',
            'startDate': '2025-01-01',
            'endDate': '2025-05-26',
            'brandIds': ','.join(brand['id'] for brand in stream_cache.get('brands', [])),
            'brandNames': ','.join(brand['name'] for brand in stream_cache.get('brands', [])),
            'subcategoryIds': ','.join(sc['subCategoryID'] for sc in all_subcategories),
            'subcategoryNames': '|'.join(sc['subCategoryName'] for sc in all_subcategories),
            'cityIds': ','.join(city['cityID'] for city in stream_cache.get('cities', [])),
        }


   

    def sync_data(self):
        # brands = stream_cache.get('brands', [])
        # if not brands:
            # raise Exception("No brands found in cache. Make sure BrandsStream runs before CampaignStream.")

        # for brand in brands:
            # brand_id = brand.get('id') 

            # params = self.get_params( brand_id)

        self.sync_child_data( params=self.get_params(),paginated=True)

            
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
