# @class_declaration interna_eg_lineasecommerceexcluidas #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_lineasecommerceexcluidas(modelos.mtd_eg_lineasecommerceexcluidas, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_lineasecommerceexcluidas #
class elganso_sync_eg_lineasecommerceexcluidas(interna_eg_lineasecommerceexcluidas, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_lineasecommerceexcluidas #
class eg_lineasecommerceexcluidas(elganso_sync_eg_lineasecommerceexcluidas, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_lineasecommerceexcluidas_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
