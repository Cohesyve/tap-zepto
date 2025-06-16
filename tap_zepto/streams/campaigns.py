from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache
import singer
# from datetime import date
from datetime import datetime, timedelta, date # Added date

from tap_zepto.state import (get_last_record_value_for_table)


LOGGER = singer.get_logger()

class CampaignStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'campaigns'
    KEY_PROPERTIES = ['campaign_id', 'start_date']
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'start_date'

    @property
    def api_path(self):
        return '/ads-bff/api/v1/campaigns'

    def get_params(self,brand_id):
        # brand_id = '4ef6e491-1881-4f88-866c-144c8e26def7'  
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
            sync_start_date = datetime.strptime(from_date_str, '%Y-%m-%dT%H:%M:%SZ').date()  # Parse initial start date with time

        today = date.today()
        sync_end_date = sync_start_date + timedelta(days=180)

        if sync_end_date > today:
            sync_end_date = today

        from_date_str = sync_start_date.strftime('%Y-%m-%d')
        to_date_str = sync_end_date.strftime('%Y-%m-%d')


        return {
            "selectedBrand": brand_id,
            "from_date": from_date_str,  
            "to_date": to_date_str,
            "categoryType": "sponsored_products",
            "brand_id": brand_id,
            "campaign_category": "sponsored_products",
            "sort_order": "ASC",
            "date_field": "",
            "campaign_sub_types": ""
        }
    
    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}?page={int(skip)}&limit={int(count)}"
        return url


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

        for record in result["data"].get("campaigns", []):
            transformed_record = self.transform_record(record)
            LOGGER.info(f"Transformed record: {record}")
            results.append(transformed_record)

        return results


    
    
    # def get_records(self, result):
    #     page = 1
    #     limit = 10
    #     has_next = True

    #     while has_next:
    #         params = self.get_params(page, limit)
    #         response = self.request_api(
    #             method=self.API_METHOD,
    #             path=self.api_path,
    #             params=params
    #         )

    #         campaigns = response['data'].get('campaigns', [])
    #         has_next = response['data'].get('has_next', False)

    #         LOGGER.info(f"Fetched {len(campaigns)} campaigns from page {page}")

    #         for record in campaigns:
    #             record['startDate'] = params['from_date']
    #             record['endDate'] = params['to_date']
    #             yield self.transform_record(record)

    #         page += 1
