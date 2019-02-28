# @class_declaration interna_so_comandassincro #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_so_comandassincro(modelos.mtd_so_comandassincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_so_comandassincro #
class elganso_sync_so_comandassincro(interna_so_comandassincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration so_comandassincro #
class so_comandassincro(elganso_sync_so_comandassincro, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.so_comandassincro_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
