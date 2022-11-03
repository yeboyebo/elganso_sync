# @class_declaration interna_eg_movitarjetamonedero #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_movitarjetamonedero(modelos.mtd_eg_movitarjetamonedero, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_movitarjetamonedero #
class elganso_sync_eg_movitarjetamonedero(interna_eg_movitarjetamonedero, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_movitarjetamonedero #
class eg_movitarjetamonedero(elganso_sync_eg_movitarjetamonedero, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_movitarjetamonedero_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
