# @class_declaration interna_eg_tarjetamonedero #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_tarjetamonedero(modelos.mtd_eg_tarjetamonedero, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_tarjetamonedero #
class elganso_sync_eg_tarjetamonedero(interna_eg_tarjetamonedero, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def consultatarjetamonedero(params):
        return form.iface.consultatarjetamonedero(params)

    @helpers.decoradores.csr()
    def actualizatarjetamonedero(params):
        return form.iface.actualizatarjetamonedero(params)

    @helpers.decoradores.csr()
    def creatarjetamonedero(params):
        return form.iface.creatarjetamonedero(params)


# @class_declaration eg_tarjetamonedero #
class eg_tarjetamonedero(elganso_sync_eg_tarjetamonedero, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_tarjetamonedero_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
