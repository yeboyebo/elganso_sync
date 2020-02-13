from controllers.base.mirakl.offers.controllers.offers_upload import OffersUpload


class EgMiraklOffersUpload(OffersUpload):

    def __init__(self, params=None):
        super().__init__("egmirakloffers", params)

        offers_params = self.get_param_sincro('miraklOffersUpload')
        self.offers_url = offers_params['url']
        self.offers_test_url = offers_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))
