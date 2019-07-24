from AQNEXT.celery import app
from YBLEGACY import qsatype
from YBUTILS import globalValues
from YBUTILS import DbRouter

from models.flsyncppal import flsyncppal_def as syncppal
from models.flsyncppal import mg_importDevWeb_def as iMgDevWeb

from controllers.base.default.managers.task_manager import TaskManager

from controllers.base.magento.drivers.magento import MagentoDriver
from controllers.base.store.drivers.psql_store import PsqlStoreDriver

from controllers.api.b2c.stocks.controllers.egstock_upload import EgStockUpload
from controllers.api.b2c.points.controllers.egpoints_upload import EgPointsUpload
from controllers.api.b2c.prices.controllers.egprices_upload import EgPricesUpload
from controllers.api.b2c.orders.controllers.egorders_download import EgOrdersDownload
from controllers.api.b2c.customers.controllers.egcustomers_download import EgCustomersDownload

from controllers.api.b2b.products.controllers.eg_products_upload import EgProductsUpload as b2bProducts
from controllers.api.b2b.orders.controllers.orders_download import OrdersDownload as b2bOrders
from controllers.api.b2b.tierprice.controllers.eg_tierprice_upload import EgB2bTierpriceUpload
from controllers.api.b2b.price.controllers.eg_price_upload import EgB2bPriceUpload
from controllers.api.b2b.inventory.controllers.eg_inventory_upload import EgB2bInventoryUpload
from controllers.api.b2b.customerrequest.controllers.eg_customerrequest_recieve import EgB2bCustomerrequestRecieve
from controllers.api.b2b.customers.controllers.eg_customers_upload import EgB2bCustomerUpload

from controllers.api.store.orders.controllers.egorders_download import EgStoreOrdersDownload

from controllers.api.mirakl.orders.controllers.eg_orders_download import EgMiraklOrdersDownload
from controllers.api.mirakl.shippingorders.controllers.eg_shipping_orders_download import EgMiraklShippingOrdersDownload
from controllers.api.mirakl.returns.controllers.eg_returns_download import EgMiraklReturnsDownload
from controllers.api.mirakl.offers.controllers.eg_offers_upload import EgMiraklOffersUpload


sync_object_dict = {
    "stock_upload": {
        "sync_object": EgStockUpload,
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
    }
}

task_manager = TaskManager(sync_object_dict)

globalValues.registrarmodulos()
cdDef = 10


@app.task
def getUnsynchronizedDevWeb(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iMgDevWeb.iface.getUnsynchronizedDevWeb() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsyncdevweb")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsyncdevweb'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        getUnsynchronizedDevWeb.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsyncdevweb")
