from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.orders_download import OrdersDownload


class EgMiraklOrdersDownload(OrdersDownload):

    def __init__(self, params=None):
        super().__init__("egmiraklorders", params)

        orders_params = self.get_param_sincro('miraklOrdersDownload')
        self.orders_url = orders_params['url']
        self.orders_test_url = orders_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))
