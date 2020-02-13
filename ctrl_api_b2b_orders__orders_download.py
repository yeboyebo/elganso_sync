from YBLEGACY import qsatype

from controllers.base.magento2.orders.controllers.orders_download import OrdersDownload


class OrdersDownload(OrdersDownload):

    def __init__(self, params=None):
        super().__init__("mgb2borders", params)

        orders_params = self.get_param_sincro('b2bOrdersDownload')
        self.orders_url = orders_params['url']
        self.orders_test_url = orders_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))
