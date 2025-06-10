
from tap_zepto.streams.cities import CitiesStream
from tap_zepto.streams.category_mapping import CategoryMappingStream
from tap_zepto.streams.product_performance import ProductPerformanceStream
from tap_zepto.streams.brands import BrandsStream
from tap_zepto.streams.products import ProductsStream
from tap_zepto.streams.sponsored_sov import SponsoredSOVStream
from tap_zepto.streams.campaign_keyword_performance import CampaignKeywordPerformanceStream
from tap_zepto.streams.campaigns import CampaignStream
from tap_zepto.streams.transactions import TransactionStream
from tap_zepto.streams.wallet_details import WalletStream
from tap_zepto.streams.reports import ReportStream
from tap_zepto.streams.top_searched_keywords import TopSearchedStream
from tap_zepto.streams.overall_conversion_chart import OverallConversionStream
from tap_zepto.streams.action_to_purchase import ActionToPurchase



AVAILABLE_STREAMS = [
    CitiesStream,
    CategoryMappingStream,
    BrandsStream,
    CampaignKeywordPerformanceStream,
    ProductPerformanceStream,
    CampaignStream,
    TransactionStream,
    WalletStream,
    ReportStream,
    
    # OverallConversionStream,
    # ActionToPurchase
    # TopSearchedStream
]

__all__ = [
    'CitiesStream',
    'CategoryMappingStream',
    'BrandsStream',
    'SponsoredSOVStream',
    'CampaignKeywordPerformanceStream',
    'ProductPerformanceStream',
    'CampaignStream',
    'TransactionStream',
    'WalletStream',
    "ReportStream"
    # 'OverallConversionStream',
    # 'ActionToPurchase'
    # 'TopSearchedStream'
]
