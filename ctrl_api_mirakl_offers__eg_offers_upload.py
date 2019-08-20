from controllers.base.mirakl.offers.controllers.offers_upload import OffersUpload


class EgMiraklOffersUpload(OffersUpload):

    offers_url = "https://marketplace.elcorteingles.es/api/offers/imports"
    offers_test_url = "https://marketplace.elcorteingles.es/api/offers/imports"

    def __init__(self, params=None):
        super().__init__("egmirakloffers", params)

        self.set_sync_params({
            "auth": "a83379cd-1f31-4b05-8175-5c5173620a4a",
            "test_auth": "a83379cd-1f31-4b05-8175-5c5173620a4a"
        })
