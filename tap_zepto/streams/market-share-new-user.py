

from tap_zepto.streams.base import BaseStream
from tap_zepto.cache import stream_cache
import singer
from datetime import date
# import urllib.parse

from tap_zepto.state import (get_last_record_value_for_table)
from datetime import datetime, timedelta, date # Added date


LOGGER = singer.get_logger()

class OverallConversionStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'overall_conversion'
    KEY_PROPERTIES = [ 'xaxisvalue','yaxisvalue']
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'start_date'

    @property
    def api_path(self):
        return '/brand-analytics-web/api/v1/market-share/'
    

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
        sync_end_date = sync_start_date + timedelta(days=150)

        if sync_end_date > today:
            sync_end_date = today

        from_date_str = sync_start_date.strftime('%Y-%m-%d')
        to_date_str = sync_end_date.strftime('%Y-%m-%d')


        # return {
        #     "brandIds": "4ef6e491-1881-4f88-866c-144c8e26def7",
        #     "brandNames": "Ecosys",
        #     "subcategoryNames": "Floor%2520%26%2520Surface%2520Cleaners%7CLiquid%2520Detergents%2520%26%2520Additives",
        #     "subcategoryIds": "d22a9423-0063-4102-9f09-57e79ff030e3,dfb37880-b40f-4783-9502-a56e12edbabc",
        #     "startDate": "2025-04-22",
        #     'cityIds': ','.join(city['cityID'] for city in stream_cache.get('cities', [])),
        #     "endDate": "2025-05-22",
        #     "viewType": "SUBCATEGORY",
        #     "aggregationLevel": "WEEK"
        #     }



        return {
            'brandIds': ','.join(brand['id'] for brand in stream_cache.get('brands', [])),
            'brandNames': ','.join(brand['name'] for brand in stream_cache.get('brands', [])),
            'subcategoryIds': ','.join(sc['subCategoryID'] for sc in all_subcategories),
            'subcategoryNames': '|'.join(sc['subCategoryName'] for sc in all_subcategories),
            'cityIds': ','.join(city['cityID'] for city in stream_cache.get('cities', [])),
            "startDate":from_date_str,
            "endDate":to_date_str,
            "viewType":"SUBCATEGORY",
            "aggregationLevel":"WEEK"
        }


  
    def get_stream_data(self, result):

        dataConfig = result['data']['metrics']['marketShareGMV']['dataConfig']
        # dataConfig = data['data']['metrics']['marketShareGMV']['dataConfig']
        yAxis =dataConfig['yAxis']
        xAxis =dataConfig['xAxis']

        graphData = result['data']['metrics']['marketShareGMV']['data']

        finalData=[]

        for node in graphData:
            xaxisLabel=xAxis
            xaxisValue=node[xAxis]

            for y in yAxis:
                yaxisLabel=y['key']
                # LOGGER.info
                value = node.get(yaxisLabel)
                yaxisValue = value if value else 0

                # yaxisValue= node[yaxisLabel] if node[yaxisLabel] and node[yaxisLabel] is not "null"  else 0
                finalData.append({
                "xaxisvalue":xaxisValue ,
                "xaxisLabel":xaxisLabel,
                "yaxisLabel": yaxisLabel,
                "yaxisvalue": yaxisValue
                })
                

        # print("this is final data ",finalData)
        return [
            self.transform_record(record)

            for record in finalData
        ]


    