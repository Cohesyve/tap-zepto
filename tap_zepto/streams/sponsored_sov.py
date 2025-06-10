from typing import Optional
from tap_zepto.streams.base import BaseStream

from tap_zepto.state import (get_last_record_value_for_table)
from datetime import datetime, timedelta, date # Added date


import singer
import json

LOGGER = singer.get_logger()  # noqa


class SponsoredSOVStream(BaseStream):
    API_METHOD = 'POST'
    TABLE = 'sponsored_sov'
    KEY_PROPERTIES = ['keyword']
    REPLICATION_METHOD = 'FULL_TABLE'
    CACHE = False

    @property
    def api_path(self):
        return '/adservice/v1/campaigns/sponsored-sov'
    
    def get_body(self):
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
            sync_start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()  # Parse initial start date

        today = date.today()
        sync_end_date = sync_start_date + timedelta(days=180)

        if sync_end_date > today:
            sync_end_date = today

        from_date_str = sync_start_date.strftime('%Y-%m-%d')
        to_date_str = sync_end_date.strftime('%Y-%m-%d')


        return {
            "from_date": from_date_str,
            "to_date":to_date_str,
            "campaign_types":[
                "PRODUCT_LISTING",
                "BANNER_LISTING",
                "PRODUCT_RECOMMENDATION",
                "SEARCH_SUGGESTION",
                "BRAND_BOOSTER"
            ]
        }

    def get_stream_data(self, result):
        results = []

        for record in result["data"].get("sponsored_sov", []):
            transformed_record = self.transform_record(record)
            LOGGER.info(f"Transformed record: {record}")
            results.append(transformed_record)

        return results
