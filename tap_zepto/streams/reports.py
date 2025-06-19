from urllib.parse import quote
from tap_zepto.streams.base import ChildStream
from tap_zepto.cache import stream_cache
from datetime import datetime, timedelta, date # Added date

from tap_zepto.state import (get_last_record_value_for_table)
import json

import singer

LOGGER = singer.get_logger()  # noqa


class ReportStream(ChildStream):
    API_METHOD = 'POST'
    TABLE = 'report'
    KEY_PROPERTIES = ['reportId' ]
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'startDate'
    CACHE=True

    @property
    def api_path(self):
        return '/api/v1/reports/request'

    
    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        # url = f"{base_url}?page={int(skip)}&page_size={int(count)}"
        return base_url

    # def get_headers(self):
    #     return {
    #         "x-proxy-target":"brand-analytics"
    #     }
    

    def get_body(self,reportType):
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
        sync_end_date = sync_start_date + timedelta(days=7)

        if sync_end_date > today:
            sync_end_date = today

        from_date_str = sync_start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        to_date_str = sync_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        LOGGER.info(f"Stream {self.TABLE}: Fetching data from {from_date_str} to {to_date_str}")
        
        postData={
            "reportType":reportType,
            "reportPayload":{
                "startDate":from_date_str,
                "endDate":to_date_str
            }
        }
        return postData
        

   

    def sync_data(self):
        reportTypes=[
                    "DEQ_Inventory",
                    # "Sales",
                    "Fill_Rate",
                    # "ASN",
                    "OOS_Visibility",
                    "SKU_Availability",
                    "OTIF",
                    "Inventory",
                    "Non_FBZ_Sales_Ledger"
                    ]
            
        for rType in reportTypes:
            bodyParams = self.get_body(rType.upper())
            LOGGER.info(f"these are body params for {rType} {bodyParams}")
            typeData={"reportType":rType}
            self.sync_child_data( body=bodyParams,paginated=False,context=typeData)

       
            
        
    def get_stream_data(self, result,context):
        results = []
        record = result["data"]
        record['reportType']=context['reportType']
        transformed_record = self.transform_record(record)
        results.append(transformed_record)
        LOGGER.info(f"Transformed record: {results}")

        # for record in result["data"]:
        #     transformed_record = self.transform_record(record)
        #     LOGGER.info(f"Transformed record: {record}")
        #     results.append(transformed_record)

        return results

