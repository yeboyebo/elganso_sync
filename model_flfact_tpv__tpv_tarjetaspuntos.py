# @class_declaration interna_tpv_tarjetaspuntos #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_tpv_tarjetaspuntos(modelos.mtd_tpv_tarjetaspuntos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_tpv_tarjetaspuntos #
class elganso_sync_tpv_tarjetaspuntos(interna_tpv_tarjetaspuntos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def desuscribesm(params):
        return form.iface.desuscribesm(params)

    @helpers.decoradores.csr()
    def suscribesm(params):
        return form.iface.suscribesm(params)

    @helpers.decoradores.csr()
    def unificartarjetas(params):
        return form.iface.unificartarjetas(params)

    @helpers.decoradores.csr()
    def generarmovimentopuntosoperacionesmagento(params):
        return form.iface.generarmovimentopuntosoperacionesmagento(params)


# @class_declaration tpv_tarjetaspuntos #
class tpv_tarjetaspuntos(elganso_sync_tpv_tarjetaspuntos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.tpv_tarjetaspuntos_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
