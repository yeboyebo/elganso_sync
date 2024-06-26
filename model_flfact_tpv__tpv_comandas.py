
# @class_declaration elganso_sync_tpv_comandas #
from models.flsyncppal import eg_diagnosis_def as diagnosis


class elganso_sync_tpv_comandas(flfact_tpv_tpv_comandas, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def diagnosis(params):
        return diagnosis.iface.diagnosis(params)

    @helpers.decoradores.csr()
    def eglogpedidosweb(params):
        return form.iface.eglogpedidosweb(params)

    @helpers.decoradores.csr()
    def eglogdevolucionesweb(params):
        return form.iface.eglogdevolucionesweb(params)

    @helpers.decoradores.csr()
    def consultasaft(params):
        return form.iface.consultasaft(params)

    @helpers.decoradores.csr()
    def eglogpedidosb2b(params):
        return form.iface.eglogpedidosb2b(params)

    @helpers.decoradores.csr()
    def actualizarestadopaack(params):
        return form.iface.actualizarestadopaack(params)

