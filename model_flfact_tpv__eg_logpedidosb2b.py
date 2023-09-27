# @class_declaration interna_eg_logpedidosb2b #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_logpedidosb2b(modelos.mtd_eg_logpedidosb2b, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_logpedidosb2b #
class elganso_sync_eg_logpedidosb2b(interna_eg_logpedidosb2b, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_logpedidosb2b #
class eg_logpedidosb2b(elganso_sync_eg_logpedidosb2b, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_logpedidosb2b_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
