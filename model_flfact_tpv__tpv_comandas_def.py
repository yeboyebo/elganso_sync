
# @class_declaration elganso_sync #
from sync import tasks


class elganso_sync(flfact_tpv):

    def elganso_sync_getActivity(self, params):
        return tasks.getActivity()

    def elganso_sync_revoke(self, params):
        return tasks.revoke(params["id"])

    def elganso_sync_mgSyncOrders(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.getUnsynchronizedOrders.delay(params['fakeRequest'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def elganso_sync_mgSyncStock(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.updateProductStock.delay(params['fakeRequest'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def elganso_sync_mgSyncPrices(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.updateProductPrices.delay(params['fakeRequest'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def elganso_sync_mgSyncPoints(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.updatePointMovements.delay(params['fakeRequest'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def elganso_sync_mgSyncCust(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.getUnsynchronizedCustomers.delay(params['fakeRequest'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def elganso_sync_egSyncVt(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.getVentasTienda.delay(params['fakeRequest'], params['codtienda'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def elganso_sync_mgSyncDevWeb(self, params):
        if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
            tasks.getUnsynchronizedDevWeb.delay(params['fakeRequest'])
            return True
        else:
            print("no tengo contraseña")

        return False

    def __init__(self, context=None):
        super().__init__(context)

    def getActivity(self, params):
        return self.ctx.elganso_sync_getActivity(params)

    def revoke(self, params):
        return self.ctx.elganso_sync_revoke(params)

    def mgSyncOrders(self, params):
        return self.ctx.elganso_sync_mgSyncOrders(params)

    def mgSyncStock(self, params):
        return self.ctx.elganso_sync_mgSyncStock(params)

    def mgSyncPrices(self, params):
        return self.ctx.elganso_sync_mgSyncPrices(params)

    def mgSyncPoints(self, params):
        return self.ctx.elganso_sync_mgSyncPoints(params)

    def mgSyncCust(self, params):
        return self.ctx.elganso_sync_mgSyncCust(params)

    def egSyncVt(self, params):
        return self.ctx.elganso_sync_egSyncVt(params)

    def mgSyncDevWeb(self, params):
        return self.ctx.elganso_sync_mgSyncDevWeb(params)

