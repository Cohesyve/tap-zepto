from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache

import singer
import json
from datetime import date

LOGGER = singer.get_logger()  # noqa


class WalletStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'wallet_details'
    KEY_PROPERTIES = ['current_balance']
    CACHE = True

    @property
    def api_path(self):
        return '/ads-brand-service/api/v1/wallet/details'
    
    def get_params(self,brand_id):
        to_date = date.today().strftime("%Y-%m-%d")


        return {
            "start_date":"2025-01-01",
            "end_date":to_date,
            "all_brands":"false",
            "brand_ids":brand_id
        }
    



    def sync_data(self):
        brands = stream_cache.get('brands', [])
        if not brands:
            raise Exception("No brands found in cache. Make sure BrandsStream runs before Walletstream.")

        for brand in brands:
            brand_id = brand.get('id') 

            params = self.get_params(brand_id)

            self.sync_child_data( params=params,paginated=False)

    
    def get_stream_data(self, result):
        return [
            self.transform_record(result)
        ]
