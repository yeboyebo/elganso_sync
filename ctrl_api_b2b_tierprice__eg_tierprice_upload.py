from YBLEGACY import qsatype

from controllers.base.magento2.tierprice.controllers.tierprice_upload import TierpriceUpload


class EgB2bTierpriceUpload(TierpriceUpload):

    def __init__(self, params=None):
        super().__init__("mgb2btierprice", params)

        tierprice_params = self.get_param_sincro('b2bTierpricesUpload')
        self.tierprice_url = tierprice_params['url']
        self.tierprice_test_url = tierprice_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))
