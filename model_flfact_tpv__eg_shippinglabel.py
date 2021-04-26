# @class_declaration interna_eg_shippinglabel #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_shippinglabel(modelos.mtd_eg_shippinglabel, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_shippinglabel #
class elganso_sync_eg_shippinglabel(interna_eg_shippinglabel, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_shippinglabel #
class eg_shippinglabel(elganso_sync_eg_shippinglabel, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_shippinglabel_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
