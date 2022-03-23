# @class_declaration interna_eg_sincrostockwebcanalweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_sincrostockwebcanalweb(modelos.mtd_eg_sincrostockwebcanalweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_sincrostockwebcanalweb #
class elganso_sync_eg_sincrostockwebcanalweb(interna_eg_sincrostockwebcanalweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_sincrostockwebcanalweb #
class eg_sincrostockwebcanalweb(elganso_sync_eg_sincrostockwebcanalweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_sincrostockwebcanalweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
