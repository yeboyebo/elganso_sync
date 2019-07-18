from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.shipping_orders_download import ShippingOrdersDownload


class EgMiraklShippingOrdersDownload(ShippingOrdersDownload):

    orders_url = "https://marketplace.elcorteingles.es/api/orders?start_update_date={}"
    orders_test_url = "https://marketplace.elcorteingles.es/api/orders?start_update_date={}"

    # orders_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&start_update_date={}"
    # orders_test_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&start_update_date={}"

    def __init__(self, params=None):
        super().__init__("egmiraklshippingorders", params)

        self.set_sync_params({
            "auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e",
            "test_auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e"
        })
