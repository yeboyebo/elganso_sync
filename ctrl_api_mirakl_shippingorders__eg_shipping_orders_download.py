from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.shipping_orders_download import ShippingOrdersDownload


class EgMiraklShippingOrdersDownload(ShippingOrdersDownload):

    shipping_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&order_ids={}"
    shipping_test_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&order_ids={}"

    def __init__(self, params=None):
        super().__init__("egmiraklshippingorders", params)

        self.set_sync_params({
            "auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e",
            "test_auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e"
        })
