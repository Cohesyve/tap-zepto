
from tap_zepto.streams.cities import CitiesStream
from tap_zepto.streams.category_mapping import CategoryMappingStream
from tap_zepto.streams.product_performance import ProductPerformanceStream
from tap_zepto.streams.brands import BrandsStream
from tap_zepto.streams.products import ProductsStream
from tap_zepto.streams.sponsored_sov import SponsoredSOVStream
from tap_zepto.streams.campaign_keyword_performance import CampaignKeywordPerformanceStream

AVAILABLE_STREAMS = [
    CitiesStream,
    CategoryMappingStream,
    BrandsStream,
    ProductsStream,
    SponsoredSOVStream,
    CampaignKeywordPerformanceStream,
    ProductPerformanceStream
]

__all__ = [
    'CitiesStream',
    'CategoryMappingStream',
    'BrandsStream',
    'ProductsStream',
    'SponsoredSOVStream',
    'CampaignKeywordPerformanceStream',
    'ProductPerformanceStream'
]
