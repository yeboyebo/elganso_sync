# @class_declaration interna_eg_logarticulosweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactppal import models as modelos


class interna_eg_logarticulosweb(modelos.mtd_eg_logarticulosweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_logarticulosweb #
class elganso_sync_eg_logarticulosweb(interna_eg_logarticulosweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_logarticulosweb #
class eg_logarticulosweb(elganso_sync_eg_logarticulosweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactppal.eg_logarticulosweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
