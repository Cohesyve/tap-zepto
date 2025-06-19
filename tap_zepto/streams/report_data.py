import io
import json
from datetime import datetime, timedelta, date # Added date

import pandas as pd
import requests
import singer
from dateutil.parser import parse # Added parse

from tap_zepto.cache import stream_cache
# Updated import to include incorporate
from tap_zepto.state import (get_last_record_value_for_table,
                                   incorporate)
from tap_zepto.streams.base import ReportStream
from urllib.parse import unquote


LOGGER = singer.get_logger()  # noqa 


class ReportDataStream(ReportStream):
    API_METHOD = 'GET'
    # KEY_PROPERTIES will be defined in subclasses
    REPLICATION_METHOD = 'INCREMENTAL'  # Changed from FULL_TABLE
    REPLICATION_KEY = 'start_date'  # Field name for bookmarking

    @property
    def api_path(self):
        # return 'https://fcc.zepto.co.in/api/v1/reports/{report_id}/download'
        return ""
    

 
    def get_stream_data(self, result):

        report_url = result['data']['presignedS3Url']
        # # Decode unicode escape first
        # decoded_unicode = report_url.encode().decode('unicode_escape')

        # # Then decode percent-encoding (e.g. %2F → /)
        # decoded_url = unquote(decoded_unicode)

        # decoded_url = unquote(report_url)
        # LOGGER.info(f"In get stream data part  {decoded_url}")

        report_data = requests.get(report_url)
        if not report_data.ok:
            LOGGER.error(f"Failed to download report: {report_data.status_code}, {report_data.text}")
            return []

        # Log content-type
        LOGGER.info(f"Downloaded file content-type: {report_data.headers.get('Content-Type')}")

        # Save to disk for debugging (optional)
        # with open("debug_downloaded_file", "wb") as f:
        #     f.write(report_data.content)
        csv_file = pd.read_csv(io.BytesIO(report_data.content))


        results = []

        # campaign_name_lookup_dict = {
        #     'reportId': record['reportId']
        #     # Assumes stream_cache['campaigns'] is populated before this stream syncs
        #     for record in stream_cache.get('report', [])
        # }

        max_date_str_in_batch = None  # Stores max date as "MM/DD/YYYY" string

        try:
            # raw_records = csv_file.parse(self.REPORT_NAME).to_dict(orient='records')
            raw_records = csv_file.to_dict(orient='records')

        except Exception as e:
            LOGGER.error(f"Failed to parse Excel sheet '{self.REPORT_NAME}' for stream {self.TABLE}. Error: {e}")
            return []

        if not raw_records:
            LOGGER.info(f"No records found in report for stream {self.TABLE}, sheet {self.REPORT_NAME}.")
            return []

        for record in raw_records:
            # campaign_name = record.get('Campaign Name')
            # if campaign_name:
            #     campaign_id = campaign_name_lookup_dict.get(campaign_name)
            #     if campaign_id:
            #         record['Campaign ID'] = campaign_id
            #     else:
            #         LOGGER.warning(f"Campaign ID not found for campaign name: '{campaign_name}' in stream {self.TABLE}")
            # else: # It's possible some records might not have 'Campaign Name', though unlikely for these reports
            #     LOGGER.warning(f"'Campaign Name' not found in record: {record} in stream {self.TABLE}")

            transformed_record = self.transform_record(record)
            results.append(transformed_record)

            # Update max_date_str_in_batch from the REPLICATION_KEY field (e.g., 'Date')
            current_record_date_value = transformed_record.get(self.REPLICATION_KEY)

            if current_record_date_value:
                try:
                    current_date_obj = None
                    if isinstance(current_record_date_value, datetime):
                        current_date_obj = current_record_date_value.date()
                    elif isinstance(current_record_date_value, date):
                        current_date_obj = current_record_date_value
                    elif isinstance(current_record_date_value, str):
                        try:
                            current_date_obj = datetime.strptime(current_record_date_value, "%d-%m-%Y").date()
                        except ValueError:
                            current_date_obj = parse(current_record_date_value).date()
                    else:
                        LOGGER.warning(
                            f"Date field '{self.REPLICATION_KEY}' has unexpected type: {type(current_record_date_value)} for record: {transformed_record}"
                        )
                        continue  # Skip if date cannot be processed

                    if max_date_str_in_batch is None or \
                       current_date_obj > parse(max_date_str_in_batch).date():
                        max_date_str_in_batch = current_date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                except Exception as e:
                    LOGGER.error(
                        f"Error processing date '{current_record_date_value}' from field '{self.REPLICATION_KEY}' in stream {self.TABLE}. Record: {transformed_record}. Error: {e}"
                    )

        # After processing all records in the batch, update the state
        # Ensure state object exists in config; it's managed by the tap runner.
        current_state = self.state
        if max_date_str_in_batch and current_state is not None:
            LOGGER.info(f"Updating state for stream {self.TABLE} with {self.REPLICATION_KEY}: {max_date_str_in_batch}")
            self.state = incorporate(
                current_state,
                self.TABLE,
                self.REPLICATION_KEY,  # Field name, e.g., 'Date'
                max_date_str_in_batch  # Value, e.g., "MM/DD/YYYY"
            )
        elif current_state is None:
             LOGGER.warning(f"State object not found in config. Cannot update state for stream {self.TABLE}.")
        elif not max_date_str_in_batch and raw_records: # Processed records but no valid date found
            LOGGER.warning(f"No valid date found in batch to update state for stream {self.TABLE}.")

        return results


class ReportDEQInventoryStream(ReportDataStream):
    TABLE = 'report_deq_inventory'
    REPORT_NAME = "DEQ_INVENTORY"
    KEY_PROPERTIES = ['Date'] # Singer primary key

    def sync_data(self):

        reports = stream_cache.get('report', [])
        # LOGGER.info(f"inside sync data funk of ReportDEQInventoryStream {reports}")
        LOGGER.info(f"Full stream_cache: {json.dumps(stream_cache, indent=2, default=str)}")
        for report in reports:
            if(report['reportType']=='DEQ_Inventory'):
                LOGGER.info(f"syncing report id found {report}")
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                super().sync_data(url)



    
class ReportFillRateStream(ReportDataStream):
    TABLE = 'report_fill_rate'
    REPORT_NAME = "FILL_RATE"
    KEY_PROPERTIES = ['SKU ID'] # Singer primary key

    def sync_data(self):
        reports = stream_cache.get('report', [])
        for report in reports:

            if(report['reportType']=='Fill_Rate'):
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                return super().sync_data(url)



class ReportOOSVisibilityStream(ReportDataStream):
    TABLE = 'report_oos_visibility'
    REPORT_NAME = "OOS_Visibility"
    KEY_PROPERTIES = ['SKU ID'] # Singer primary key

    def sync_data(self):
        reports = stream_cache.get('report', [])
        for report in reports:
            if(report['reportType']=='OOS_Visibility'):
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                super().sync_data(url)



    
    
class ReportSKUAvailabilityStream(ReportDataStream):
    TABLE = 'report_sku_availability'
    REPORT_NAME = "SKU_AVAILABILITY"
    KEY_PROPERTIES = ['SKU ID'] # Singer primary key

    def sync_data(self):
        reports = stream_cache.get('report', [])
        for report in reports:
            if(report['reportType']=='SKU_Availability'):
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                super().sync_data(url)




class ReportOtifStream(ReportDataStream):
    TABLE = 'report_otif'
    REPORT_NAME = "OTIF"
    KEY_PROPERTIES = ['Vendor ID'] # Singer primary key

    def sync_data(self):
        reports = stream_cache.get('report', [])
        for report in reports:
            if(report['reportType']=='OTIF'):
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                super().sync_data(url)


    
    
class ReportInventoryStream(ReportDataStream):
    TABLE = 'report_inventory'
    REPORT_NAME = "INVENTORY"
    KEY_PROPERTIES = ['EAN'] # Singer primary key

    def sync_data(self):
        reports = stream_cache.get('report', [])
        for report in reports:
            if(report['reportType']=='Inventory'):
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                super().sync_data(url)



    
class ReportNonFBZStream(ReportDataStream):
    TABLE = 'report_non_fbz_sales_ledger'
    REPORT_NAME = "Non_FBZ_Sales_Ledger"
    KEY_PROPERTIES = ['Campaign ID', 'Date'] # Singer primary key

    def sync_data(self):
        reports = stream_cache.get('report', [])
        for report in reports:
            if(report['reportType']=='Non_FBZ_Sales_Ledger'):
                report_id=report['reportId']
                url=f"https://fcc.zepto.co.in/api/v1/reports/{report_id}/download"
                super().sync_data(url)

