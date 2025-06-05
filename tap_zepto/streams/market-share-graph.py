

from tap_zepto.streams.base import BaseStream
from tap_zepto.cache import stream_cache
import singer
from datetime import date
# import urllib.parse


LOGGER = singer.get_logger()

class MarketShareGraphStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'campaigns'
    KEY_PROPERTIES = ['campaign_id', 'start_date']
    REPLICATION_METHOD = 'INCREMENTAL'
    REPLICATION_KEY = 'start_date'

    @property
    def api_path(self):
        return '/brand-analytics-web/api/v1/market-share/gmv-and-units'

    def get_params(self,brand_id):
        # brand_id = '4ef6e491-1881-4f88-866c-144c8e26def7'  
        to_date = date.today().strftime("%Y-%m-%d")


        return {
        "brandIds":brand_id,
        "brandNames":"",
        "subcategoryNames":"",
        "subcategoryIds":"",
        "cityIds":"facade53-8330-4ebe-b07e-55319220a301,449216c9-1760-4194-a9d4-06f5b3ddb7db,81f24084-8358-4d11-8b79-1acd7efd6a91,7e926d2f-adad-4e5a-956f-f07fffa54164,98141024-d057-49da-a307-82d88308db5d,963e4758-abc3-4766-a26c-bdc4d0c30bd2,c5b3d670-f20e-4cae-a6b7-42e17b8fb08d,f938d139-3cb7-4b78-8980-b88178659225,58b4b3e5-572d-491d-a9a3-66a5560e4291,82c98de3-2610-47d9-ab70-251330bcb704,15862867-2c01-4699-8cfe-2a2d19bee4f1,3eb31521-2060-4beb-b6fb-18ba88b6adda,078d5e32-627a-4907-8df8-4360bc7c06da,388df8a5-218a-4e80-9138-897f70252a75,ea6e2d03-d75e-474a-90a7-4e79096b5b45,014af366-5112-4363-9b52-6226a2ff48d9,f3cbc158-35a4-4c2c-ac5e-56e1fa5b08fd,82647e5a-8a81-41f8-8ed7-859e023c448f,3c91a871-2d4f-4d8a-a921-f2fb2859e0df,169ee922-31e9-4c90-9117-38234c705b84,d337388e-1a65-40b4-b89d-0d15c78d611f,fea7e548-473c-4cf9-bc1b-a6fd4d9bb0e2,f0e24877-3ed8-4026-a999-69bf3909cc40,5a17386b-33fb-43d4-bf71-258277768fcc,c0d479f8-52bf-4781-8d56-ecfcb21b41d1,075236e1-be26-4084-a4fe-ceba0a69a5a0,7c1962ea-0a21-47b3-bf6c-91afabddc237,4dda0cbc-9e53-4e45-98f8-87f574857e12,30735969-391b-478c-a81c-be93115f87a8,ce56c260-4cf6-4d10-b481-9ed2fd7a90d4,a5f8dc56-616d-4123-b256-047249ff1176,67ba5a13-59ed-4e8f-b279-44a7978c516b,3de94802-07a4-47c0-947e-65d61302752f,76c6e4cb-adab-48fd-aa48-bffd412b3c03,1f68f9e5-6d06-4feb-b2a1-4f208c648951,a1dcbfe4-e614-4c2c-8143-c277d1aba5f8,b4fc5b4c-ef99-4d24-be15-f8690c35955b,d0c5c4c5-ab54-407d-a6f0-d924610c86a6,35e672bd-8f0e-4e9d-9391-5b977c4b52ea,9e3216dc-1aff-41c4-bae7-75058158e6d3,8e6bfeb7-25f2-41c2-be52-75fc98c8025c,3cd6c684-388d-45b4-b050-ac6cc2803028,1c678705-4565-415b-bbf6-e89efc48fbed,056e834d-a1d2-4df3-a93d-7ebd60e6bb16,55871558-d0f9-4391-b539-3f435c894d7c,a2b4beb2-7c4d-4749-bc95-5b04d4adf837,c68232c5-7375-43fe-a7ce-510d7530cbf6,e6db07ff-ae8d-4948-a2f7-5aa6a883d6b9,e92d0690-1df3-474b-9a5a-14e9761dfae3,170d7ace-25e7-4ecf-a2f7-a79024b2c8a2,8ed26cb7-eb7d-4b7b-8d8c-3e93d5855bdd,ac7cd4f0-8980-41ee-9931-cbbd3865907c,f6d77ae4-f662-4f13-a0d5-dc75a72caddd,ddf073f6-808e-491a-9cd8-6f1763b38aaa,f31e8f17-5547-41d9-906e-082c8b3e5f3d,06f65018-add9-4340-b5f0-d33f43f626d3,4f30407c-6a3c-4a4e-8a3d-652217d4b6cb,c5c88e82-be9a-4e49-9546-f269c0f714ec,3ae99187-1625-4925-b490-6c1b080cd406,ed4f0a63-4887-4b08-b89c-bf1ac1703f54,960153c2-f137-44b9-8650-136abe528a9b,c13eeeb7-d49a-4961-b6ba-93f14c9dd393,47e68964-42b7-489c-a698-b5a6bdebd374,d4f93f80-56c6-44d3-af5c-c37e70e11770,64153376-b4d5-495f-826f-89bd134f12f1,9123ec08-699e-4804-ad97-39d32254491b,a64421ba-ce07-4688-bf9e-b97533ebda45,ee66dc2a-aded-4445-a7b2-1ad63715725c,16f9be64-9fe0-4c07-b58c-f69b0d3d0610,05ed345b-bc36-44bc-9ef6-e9d5055eba40,df1ecb02-77a5-47b1-aa59-7c78ad69d1c5,9d4b400b-637c-4886-bf35-51231380ce61,bedfb594-54b5-4976-8b57-3e1f347e413a,bb5bb05a-5c71-4038-b342-4f1aab72d9a6,df73cdc7-5840-4f42-bb66-c84a6f52b9c4,72fb38ea-adb8-468a-9d7b-be46ae9d7fc1",
        "startDate":"2025-01-01",
        "endDate":to_date,
        "viewType":"SUBCATEGORY",
        "aggregationLevel":"DAY"
        }


  
    def get_records(self, context):
        brands = stream_cache.get('brands', [])
        if not brands:
            raise Exception("No brands found in cache. Make sure BrandsStream runs before CampaignStream.")

        for brand in brands:
            brand_id = brand.get('id') 
        
            params = self.get_params(self, brand_id)

            response = self.request_api(
                method=self.API_METHOD,
                path=self.api_path,
                params=params
            )

            # chart_data = response['data'].get('data', [])
            overall_conversion = (
                response.get("data", {})
                .get("metrics", {})
                .get("overallConversion", {})
            )

            chart_data = overall_conversion.get("data", [])
            data_config = overall_conversion.get("dataConfig", {})
            y_axis = data_config.get("yAxis", [])


            LOGGER.info(f"Fetched {len(chart_data)} overall conversions for brand {brand_id} ")

            key_map = {
                entry["key"]: urllib.parse.unquote(entry["key"])
                for entry in y_axis
            }

            for record in chart_data:
                transformed = {"key": record["key"]}
                for encoded_key, decoded_key in key_map.items():
                    transformed[decoded_key] = record.get(encoded_key)
                # overallConversion = chart_data['metrics']['overallConversion']
                # new_record={key:overallConversion}
                # all_keys = overallConversion['dataConfig']['yAxis']
                # all_keys = for i in all_keys
            
            yield self.transform_record(transformed)





    