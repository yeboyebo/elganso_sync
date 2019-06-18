from YBLEGACY import qsatype

from controllers.base.magento2.tierprice.controllers.tierprice_upload import TierpriceUpload


class EgB2bTierpriceUpload(TierpriceUpload):

    tierprice_url = "https://b2b.elganso.com/index.php/rest/default/V1/products/tier-prices"
    tierprice_test_url = "http://magento2.local/index.php/rest/default/V1/products/tier-prices"

    def __init__(self, params=None):
        super().__init__("mgb2btierprice", params)

        self.set_sync_params({
            "auth": "Bearer 7plp6sabntbe9liboanunxy8l9813f3p",
            "test_auth": "Bearer 2uvlxkuihd474nzj3dize4f5ezbl3lb6"
        })