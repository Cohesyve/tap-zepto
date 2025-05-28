from typing import Optional
from tap_zepto.streams.base import BaseStream

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
        return {
            "from_date": "1/1/2025",
            "to_date":"5/15/2025",
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
