from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.shipping_orders_download import ShippingOrdersDownload


class EgMiraklShippingOrdersDownload(ShippingOrdersDownload):

    def __init__(self, params=None):
        super().__init__("egmiraklshippingorders", params)

        shipping_params = self.get_param_sincro('miraklShippingOrdersDownload')
        self.shipping_url = shipping_params['url']
        self.shipping_test_url = shipping_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))
