# @class_declaration interna_eg_bonos #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_bonos(modelos.mtd_eg_bonos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_bonos #
class elganso_sync_eg_bonos(interna_eg_bonos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def creabono(params):
        return form.iface.creabono(params)

    @helpers.decoradores.csr()
    def consultabono(params):
        return form.iface.consultabono(params)

    @helpers.decoradores.csr()
    def tienebonoregistro(params):
        return form.iface.tienebonoregistro(params)

    @helpers.decoradores.csr()
    def actualizabono(params):
        return form.iface.actualizabono(params)

    @helpers.decoradores.csr()
    def consultabonoventa(params):
        return form.iface.consultabonoventa(params)

    def generaCodBono():
        return form.iface.generaCodBono()


# @class_declaration eg_bonos #
class eg_bonos(elganso_sync_eg_bonos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_bonos_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
