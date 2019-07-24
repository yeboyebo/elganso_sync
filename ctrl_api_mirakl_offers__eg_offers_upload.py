from controllers.base.mirakl.offers.controllers.offers_upload import OffersUpload


class EgMiraklOffersUpload(OffersUpload):

    offers_url = "https://marketplace.elcorteingles.es/api/offers/imports"
    offers_test_url = "https://marketplace.elcorteingles.es/api/offers/imports"

    def __init__(self, params=None):
        super().__init__("egmirakloffers", params)

        self.set_sync_params({
            "auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e",
            "test_auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e"
        })
