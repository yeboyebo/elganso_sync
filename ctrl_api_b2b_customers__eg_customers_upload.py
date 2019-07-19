from YBLEGACY import qsatype

from controllers.base.magento2.customers.controllers.customer_upload import CustomerUpload


class EgB2bCustomerUpload(CustomerUpload):

    customer_url = "https://b2b.elganso.com/index.php/rest/default/V1/customers"
    customer_test_url = "http://magento2.local/index.php/rest/default/V1/customers"

    customer_put_url = "https://b2b.elganso.com/index.php/rest/default/V1/customers/"
    customer_put_test_url = "http://magento2.local/index.php/rest/default/V1/customers/"

    def __init__(self, params=None):
        super().__init__("mgb2bcustomers", params)

        self.set_sync_params({
            "auth": "Bearer 7plp6sabntbe9liboanunxy8l9813f3p",
            "test_auth": "Bearer 2uvlxkuihd474nzj3dize4f5ezbl3lb6"
        })
