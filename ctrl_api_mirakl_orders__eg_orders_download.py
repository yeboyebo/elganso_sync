from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.orders_download import OrdersDownload


class EgMiraklOrdersDownload(OrdersDownload):

    # orders_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=WAITING_ACCEPTANCE"
    # orders_test_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=WAITING_ACCEPTANCE"

    orders_url = "https://marketplace.elcorteingles.es/api/orders"
    orders_test_url = "https://marketplace.elcorteingles.es/api/orders"

    def __init__(self, process, params=None):
        super().__init__("egmirakleorders", params)

        self.set_sync_params({
            "auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e",
            "test_auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e"
        })
