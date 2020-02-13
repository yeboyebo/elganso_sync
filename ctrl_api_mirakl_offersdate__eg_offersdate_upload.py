from controllers.base.mirakl.offersdate.controllers.offersdate_upload import OffersDateUpload


class EgMiraklOffersDateUpload(OffersDateUpload):

    def __init__(self, params=None):
        super().__init__("egmirakloffersdate", params)

        offers_params = self.get_param_sincro('miraklOffersdateUpload')
        self.offers_url = offers_params['url']
        self.offers_test_url = offers_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))
