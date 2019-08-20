from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.shipping_orders_download import ShippingOrdersDownload


class EgMiraklShippingOrdersDownload(ShippingOrdersDownload):

    shipping_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&order_ids={}"
    shipping_test_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&order_ids={}"

    # orders_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&start_update_date={}"
    # orders_test_url = "https://marketplace.elcorteingles.es/api/orders?order_state_codes=SHIPPING&start_update_date={}"

    def __init__(self, params=None):
        super().__init__("egmiraklshippingorders", params)

        self.set_sync_params({
            "auth": "a83379cd-1f31-4b05-8175-5c5173620a4a",
            "test_auth": "a83379cd-1f31-4b05-8175-5c5173620a4a"
        })
