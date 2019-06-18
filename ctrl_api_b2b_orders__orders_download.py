from YBLEGACY import qsatype

from controllers.base.magento2.orders.controllers.orders_download import OrdersDownload


class OrdersDownload(OrdersDownload):

    orders_url = "http://b2b.elganso.com/index.php/rest/V1/unsynchronized/orders/"
    orders_test_url = "http://magento2.local/index.php/rest/V1/unsynchronized/orders/"

    def __init__(self, params=None):
        super().__init__("mgb2borders", params)

        self.set_sync_params({
            "auth": "Bearer 7plp6sabntbe9liboanunxy8l9813f3p",
            "test_auth": "Bearer 2uvlxkuihd474nzj3dize4f5ezbl3lb6"
        })
