# @class_declaration interna_tpv_viajesmultitransstock #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_tpv_viajesmultitransstock(modelos.mtd_tpv_viajesmultitransstock, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_tpv_viajesmultitransstock #
class elganso_sync_tpv_viajesmultitransstock(interna_tpv_viajesmultitransstock, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration tpv_viajesmultitransstock #
class tpv_viajesmultitransstock(elganso_sync_tpv_viajesmultitransstock, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.tpv_viajesmultitransstock_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
