# @class_declaration interna_eg_logpedidosweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_logpedidosweb(modelos.mtd_eg_logpedidosweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_logpedidosweb #
class elganso_sync_eg_logpedidosweb(interna_eg_logpedidosweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_logpedidosweb #
class eg_logpedidosweb(elganso_sync_eg_logpedidosweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_logpedidosweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
