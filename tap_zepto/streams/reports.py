from urllib.parse import quote
from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache

from tap_zepto.state import (get_last_record_value_for_table)

import singer

LOGGER = singer.get_logger()  # noqa


class ReportStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'report'
    KEY_PROPERTIES = ['brand_id', 'id', ]
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'startDate'

    @property
    def api_path(self):
        return '/ads-analytics-service/api/v1/reports'
    
    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}?page={int(skip)}&page_size={int(count)}"
        return url

    def get_headers(self):
        return {
            "x-proxy-target":"brand-analytics"
        }
    
    def get_params(self,brandid):
        return {
            'brand_id':brandid
        }


   

    def sync_data(self):
        brands = stream_cache.get('brands', [])
        if not brands:
            raise Exception("No brands found in cache. Make sure BrandsStream runs before CampaignStream.")

        for brand in brands:
            brand_id = brand.get('id') 
            params = self.get_params( brand_id)
            self.sync_child_data( params=params,paginated=True)

            
            
        
    def get_stream_data(self, result):
        results = []

        for record in result["data"].get("reports", []):
            transformed_record = self.transform_record(record)
            LOGGER.info(f"Transformed record: {record}")
            results.append(transformed_record)

        return results
