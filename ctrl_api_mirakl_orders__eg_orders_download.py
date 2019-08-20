from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.orders_download import OrdersDownload


class EgMiraklOrdersDownload(OrdersDownload):

    orders_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=WAITING_ACCEPTANCE&start_date={}"
    orders_test_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=WAITING_ACCEPTANCE&start_date={}"

    def __init__(self, params=None):
        super().__init__("egmiraklorders", params)

        self.set_sync_params({
            "auth": "a83379cd-1f31-4b05-8175-5c5173620a4a",
            "test_auth": "a83379cd-1f31-4b05-8175-5c5173620a4a"
        })
