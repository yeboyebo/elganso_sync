
# @class_declaration elganso_sync_tpv_comandas #
from models.flsyncppal import eg_diagnosis_def as diagnosis


class elganso_sync_tpv_comandas(flfact_tpv_tpv_comandas, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def getactivity(params):
        return form.iface.getActivity(params)

    @helpers.decoradores.csr()
    def revoke(params):
        return form.iface.revoke(params)

    @helpers.decoradores.csr()
    def mgsyncorders(params):
        return form.iface.mgSyncOrders(params)

    @helpers.decoradores.csr()
    def mgsyncstock(params):
        return form.iface.mgSyncStock(params)

    @helpers.decoradores.csr()
    def mgsyncprices(params):
        return form.iface.mgSyncPrices(params)

    @helpers.decoradores.csr()
    def mgsyncpoints(params):
        return form.iface.mgSyncPoints(params)

    @helpers.decoradores.csr()
    def mgsynccust(params):
        return form.iface.mgSyncCust(params)

    @helpers.decoradores.csr()
    def egsyncvt(params):
        return form.iface.egSyncVt(params)

    @helpers.decoradores.csr()
    def diagnosis(params):
        return diagnosis.iface.diagnosis(params)

    @helpers.decoradores.csr()
    def mgsyncdevweb(params):
        return form.iface.mgSyncDevWeb(params)

