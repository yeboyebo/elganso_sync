# @class_declaration interna_eg_motivosdevolucion #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_motivosdevolucion(modelos.mtd_eg_motivosdevolucion, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_motivosdevolucion #
class elganso_sync_eg_motivosdevolucion(interna_eg_motivosdevolucion, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_motivosdevolucion #
class eg_motivosdevolucion(elganso_sync_eg_motivosdevolucion, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_motivosdevolucion_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
