# @class_declaration interna_eg_cupones #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_cupones(modelos.mtd_eg_cupones, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_cupones #
class elganso_sync_eg_cupones(interna_eg_cupones, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_cupones #
class eg_cupones(elganso_sync_eg_cupones, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_cupones_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
