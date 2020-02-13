from YBLEGACY import qsatype

from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload


class EgB2bInventoryUpload(InventoryUpload):

    def __init__(self, params=None):
        super().__init__("mgb2binventory", params)

        inventory_params = self.get_param_sincro('b2bInventoryUpload')
        self.inventory_url = inventory_params['url']
        self.inventory_test_url = inventory_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))
