from YBLEGACY import qsatype
from YBUTILS import globalValues

# Base
from controllers.base.default.managers.task_manager import TaskManager
from controllers.base.magento.drivers.magento import MagentoDriver
from controllers.base.store.drivers.psql_store import PsqlStoreDriver

# B2C
from controllers.api.b2c.stocks.controllers.egstock_upload import EgStockUpload
from controllers.api.b2c.movistock.controllers.egmovistock_upload import EgMovistockUpload
from controllers.api.b2c.points.controllers.egpoints_upload import EgPointsUpload
from controllers.api.b2c.prices.controllers.egprices_upload import EgPricesUpload
from controllers.api.b2c.orders.controllers.egorders_download import EgOrdersDownload
from controllers.api.b2c.customers.controllers.egcustomers_download import EgCustomersDownload
from controllers.api.b2c.refounds.controllers.egrefounds_download import EgRefoundsDownload
from controllers.api.b2c.stock_inicial.controllers.egstock_inicial_recieve import EgStockInicialRecieve

# B2B
from controllers.api.b2b.products.controllers.eg_products_upload import EgProductsUpload as b2bProducts
from controllers.api.b2b.orders.controllers.orders_download import OrdersDownload as b2bOrders
from controllers.api.b2b.tierprice.controllers.eg_tierprice_upload import EgB2bTierpriceUpload
from controllers.api.b2b.price.controllers.eg_price_upload import EgB2bPriceUpload
from controllers.api.b2b.inventory.controllers.eg_inventory_upload import EgB2bInventoryUpload
from controllers.api.b2b.customerrequest.controllers.eg_customerrequest_recieve import EgB2bCustomerrequestRecieve
from controllers.api.b2b.customers.controllers.eg_customers_upload import EgB2bCustomerUpload

# Tiendas
from controllers.api.store.orders.controllers.egorders_download import EgStoreOrdersDownload

# Mirakl
from controllers.api.mirakl.orders.controllers.eg_orders_download import EgMiraklOrdersDownload
from controllers.api.mirakl.shippingorders.controllers.eg_shipping_orders_download import EgMiraklShippingOrdersDownload
from controllers.api.mirakl.returns.controllers.eg_returns_download import EgMiraklReturnsDownload
from controllers.api.mirakl.offers.controllers.eg_offers_upload import EgMiraklOffersUpload
from controllers.api.mirakl.returnsvaldemoro.controllers.eg_returnsvaldemoro_download import EgMiraklReturnsValdemoroDownload
from controllers.api.mirakl.returnsvaldemoroid.controllers.eg_returnsvaldemoroid_download import EgMiraklReturnsValdemoroIdDownload
from controllers.api.mirakl.offersdate.controllers.eg_offersdate_upload import EgMiraklOffersDateUpload
from controllers.api.mirakl.returnsnew.controllers.eg_returnsnew_download import EgMiraklReturnsNewDownload

# Amazon
from controllers.api.amazon.products.controllers.az_products_upload import AzProductsUpload
from controllers.api.amazon.stocks.controllers.az_stocks_upload import AzStocksUpload
from controllers.api.amazon.prices.controllers.az_prices_upload import AzPricesUpload
from controllers.api.amazon.images.controllers.az_images_upload import AzImagesUpload
from controllers.api.amazon.relationships.controllers.az_relationships_upload import AzRelationshipsUpload
from controllers.api.amazon.feedresult.controllers.az_feedresult_get import AzFeedResultGet
from controllers.api.amazon.feedresult.controllers.az_feedresult_process import AzFeedResultProcess

from controllers.api.amazon.orderacknowledgement.controllers.az_orderacknowledgement_upload import AzOrderAcknowledgementUpload
from controllers.api.amazon.orderfulfillment.controllers.az_orderfulfillment_upload import AzOrderFulfillmentUpload

from controllers.api.amazon.orders.controllers.az_orders_get import AzOrdersResultGet
from controllers.api.amazon.listorderitems.controllers.az_listorderitems_get import AzListOrderItemsResultGet

from controllers.api.amazon.imagebackground.controllers.az_imagebackground_upload import AzImageBackgroundUpload
from controllers.api.amazon.returns.controllers.az_returns_get import AzReturnsResultGet

# MG2
from controllers.api.magento2.products.controllers.mg2_products_upload import Mg2ProductsUpload
from controllers.api.magento2.orders.controllers.mg2_orders_process import Mg2OrdersProcess
from controllers.api.magento2.price.controllers.mg2_price_upload import Mg2PriceUpload
from controllers.api.magento2.inventory.controllers.mg2_inventory_upload import Mg2InventoryUpload
from controllers.api.magento2.points.controllers.mg2_points_process import Mg2PointsProcess
from controllers.api.magento2.tierprice.controllers.mg2_tierprice_upload import Mg2TierpriceUpload
from controllers.api.magento2.refounds.controllers.mg2_refounds_process import Mg2RefoundsProcess
from controllers.api.magento2.special_price.controllers.mg2_special_price_upload import Mg2SpecialPriceUpload
from controllers.api.magento2.stock_incremental.controllers.mg2_stock_incremental_upload import Mg2StockIncrementalUpload
from controllers.api.magento2.inventory_old.controllers.mg2_inventory_old_upload import Mg2InventoryOldUpload
from controllers.api.magento2.inventory_night.controllers.mg2_inventory_night_upload import Mg2InventoryNightUpload
from controllers.api.magento2.delete_special_price.controllers.mg2_delete_special_price_upload import Mg2DeleteSpecialPriceUpload
from controllers.api.magento2.products_upload.controllers.mg2_products_process import Mg2ProductsProcess

sync_object_dict = {
    "stock_upload": {
        "sync_object": EgStockUpload,
        "driver": MagentoDriver
    },
    "movistock_upload": {
        "sync_object": EgMovistockUpload,
        "driver": MagentoDriver
    },
    "points_upload": {
        "sync_object": EgPointsUpload,
        "driver": MagentoDriver
    },
    "prices_upload": {
        "sync_object": EgPricesUpload,
        "driver": MagentoDriver
    },
    "orders_download": {
        "sync_object": EgOrdersDownload,
        "driver": MagentoDriver
    },
    "customers_download": {
        "sync_object": EgCustomersDownload,
        "driver": MagentoDriver
    },
    "store_orders_download": {
        "sync_object": EgStoreOrdersDownload,
        "driver": PsqlStoreDriver
    },
    "refounds_download": {
        "sync_object": EgRefoundsDownload,
        "driver": MagentoDriver
    },
    "stock_inicial_recieve": {
        "sync_object": EgStockInicialRecieve
    },
    "products_b2b_upload": {
        "sync_object": b2bProducts
    },
    "orders_b2b_download": {
        "sync_object": b2bOrders
    },
    "b2b_tierprice_upload": {
        "sync_object": EgB2bTierpriceUpload
    },
    "b2b_price_upload": {
        "sync_object": EgB2bPriceUpload
    },
    "b2b_inventory_upload": {
        "sync_object": EgB2bInventoryUpload
    },
    "b2b_customerrequest_recieve": {
        "sync_object": EgB2bCustomerrequestRecieve
    },
    "b2b_customers_upload": {
        "sync_object": EgB2bCustomerUpload
    },
    "mirakl_orders_download": {
        "sync_object": EgMiraklOrdersDownload
    },
    "mirakl_shippingorders_download": {
        "sync_object": EgMiraklShippingOrdersDownload
    },
    "mirakl_returns_download": {
        "sync_object": EgMiraklReturnsDownload
    },
    "mirakl_offers_upload": {
        "sync_object": EgMiraklOffersUpload
    },
    "mirakl_returnsvaldemoro_download": {
        "sync_object": EgMiraklReturnsValdemoroDownload
    },
    "mirakl_returnsvaldemoroid_download": {
        "sync_object": EgMiraklReturnsValdemoroIdDownload
    },
    "mirakl_offersdate_upload": {
        "sync_object": EgMiraklOffersDateUpload
    },
    "amazon_products_upload": {
        "sync_object": AzProductsUpload
    },
    "amazon_stocks_upload": {
        "sync_object": AzStocksUpload
    },
    "amazon_prices_upload": {
        "sync_object": AzPricesUpload
    },
    "amazon_images_upload": {
        "sync_object": AzImagesUpload
    },
    "amazon_relationships_upload": {
        "sync_object": AzRelationshipsUpload
    },
    "amazon_feedresult_get": {
        "sync_object": AzFeedResultGet
    },
    "mirakl_returnsnew_download": {
        "sync_object": EgMiraklReturnsNewDownload
    },
    "amazon_feedresult_process": {
        "sync_object": AzFeedResultProcess
    },
    "amazon_orderacknowledgement_upload": {
        "sync_object": AzOrderAcknowledgementUpload
    },
    "amazon_orderfulfillment_upload": {
        "sync_object": AzOrderFulfillmentUpload
    },
    "amazon_orders_get": {
        "sync_object": AzOrdersResultGet
    },
    "amazon_listorderitems_get": {
        "sync_object": AzListOrderItemsResultGet
    },
    "amazon_imagebackground_upload": {
        "sync_object": AzImageBackgroundUpload
    },
    "amazon_returns_get": {
        "sync_object": AzReturnsResultGet
    },
    "mg2_products_upload": {
        "sync_object": Mg2ProductsUpload
    },
    "mg2_orders_process": {
        "sync_object": Mg2OrdersProcess,
        "driver": MagentoDriver
    },
    "mg2_price_upload": {
        "sync_object": Mg2PriceUpload
    },
    "mg2_inventory_upload": {
        "sync_object": Mg2InventoryUpload
    },
    "mg2_points_process": {
        "sync_object": Mg2PointsProcess,
        "driver": MagentoDriver
    },
    "mg2_tierprice_upload": {
        "sync_object": Mg2TierpriceUpload
    },
    "mg2_refounds_process": {
        "sync_object": Mg2RefoundsProcess,
        "driver": MagentoDriver
    },
    "mg2_special_price_upload": {
        "sync_object": Mg2SpecialPriceUpload
    },
    "mg2_stock_incremental_upload": {
        "sync_object": Mg2StockIncrementalUpload
    },
    "mg2_inventory_old_upload": {
        "sync_object": Mg2InventoryOldUpload
    },
    "mg2_inventory_night_upload": {
        "sync_object": Mg2InventoryNightUpload
    },
    "mg2_delete_special_price_upload": {
        "sync_object": Mg2DeleteSpecialPriceUpload
    },
    "mg2_products_process": {
        "sync_object": Mg2ProductsProcess,
        "driver": MagentoDriver
    }
}

task_manager = TaskManager(sync_object_dict)

globalValues.registrarmodulos()
cdDef = 10
