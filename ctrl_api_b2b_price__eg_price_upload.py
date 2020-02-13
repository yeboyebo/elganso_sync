from YBLEGACY import qsatype

from controllers.base.magento2.price.controllers.price_upload import PriceUpload


class EgB2bPriceUpload(PriceUpload):

    def __init__(self, params=None):
        super().__init__("mgb2bprice", params)

        price_params = self.get_param_sincro('b2bPricesUpload')
        self.price_url = price_params['url']
        self.price_test_url = price_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))
