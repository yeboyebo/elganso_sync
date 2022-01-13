# @class_declaration interna_so_inventariossincro #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_so_inventariossincro(modelos.mtd_so_inventariossincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_so_inventariossincro #
class elganso_sync_so_inventariossincro(interna_so_inventariossincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration so_inventariossincro #
class so_inventariossincro(elganso_sync_so_inventariossincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.so_inventariossincro_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
