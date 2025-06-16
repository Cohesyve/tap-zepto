from urllib.parse import quote
from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache

from tap_zepto.state import (get_last_record_value_for_table)
from datetime import datetime, timedelta, date # Added date


import singer

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
        
        # to_date = date.today().strftime("%Y-%m-%d")
        from_date_str = self.config.get('start_date')  # Default start date if no state
        # Ensure state is available in config, default to empty dict if None for get_last_record_value_for_table
        current_state = self.state
        
        last_sync_date_obj = get_last_record_value_for_table(current_state, self.TABLE)

        LOGGER.info(f"Last sync date for stream {self.TABLE}: {last_sync_date_obj}")

        if last_sync_date_obj:
            # last_sync_date_obj is a datetime.date object from state.py
            sync_start_date = last_sync_date_obj + timedelta(days=1)
        else:
            sync_start_date = datetime.strptime(from_date_str, '%Y-%m-%dT%H:%M:%SZ').date()  # Parse initial start date

        today = date.today()
        sync_end_date = sync_start_date + timedelta(days=180)

        if sync_end_date > today:
            sync_end_date = today

        from_date_str = sync_start_date.strftime('%Y-%m-%d')
        to_date_str = sync_end_date.strftime('%Y-%m-%d')

        

        return {
            'viewType': 'top_selling',
            'startDate': from_date_str,
            'endDate': to_date_str,
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
