from YBLEGACY import qsatype

from controllers.base.magento2.customers.controllers.customer_upload import CustomerUpload


class EgB2bCustomerUpload(CustomerUpload):

    def __init__(self, params=None):
        super().__init__("mgb2bcustomers", params)

        customer_params = self.get_param_sincro('b2bCustomersUpload')
        self.customer_url = customer_params['url']
        self.customer_test_url = customer_params['test_url']

        customer_put_params = self.get_param_sincro('b2bCustomersUploadPut')
        self.customer_put_url = customer_put_params['url']
        self.customer_put_test_url = customer_put_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))
