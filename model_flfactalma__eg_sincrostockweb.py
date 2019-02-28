# @class_declaration interna_eg_sincrostockweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_sincrostockweb(modelos.mtd_eg_sincrostockweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_sincrostockweb #
class elganso_sync_eg_sincrostockweb(interna_eg_sincrostockweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_sincrostockweb #
class eg_sincrostockweb(elganso_sync_eg_sincrostockweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_sincrostockweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
