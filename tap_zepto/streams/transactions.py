

from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache
import singer
# import datetime
from datetime import date

LOGGER = singer.get_logger()

class TransactionStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'transactions'
    KEY_PROPERTIES = ['id', 'brand_id','created_at']
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'start_date'

    @property
    def api_path(self):
        return '/ads-brand-service/api/v1/wallet/transactions'

    def get_params(self,brand_id):
        to_date = date.today().strftime("%Y-%m-%d")


        return {
            "start_date":"2025-01-01",
            "end_date":to_date,
            "all_brands":"false",
            "brand_ids":brand_id
        }

    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}?page={int(skip)}&page_size={int(count)}"
        return url


    def sync_data(self):
        brands = stream_cache.get('brands', [])
        if not brands:
            raise Exception("No brands found in cache. Make sure BrandsStream runs before TransactionStream.")

        for brand in brands:
            brand_id = brand.get('id') 

            params = self.get_params(brand_id)

            self.sync_child_data( params=params,paginated=True)

            
        
    def get_stream_data(self, result):
        results = []

        for record in result["data"].get("transactions", []):
            transformed_record = self.transform_record(record)
            LOGGER.info(f"Transformed record: {record}")
            results.append(transformed_record)

        return results



