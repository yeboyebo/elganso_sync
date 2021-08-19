# @class_declaration interna_eg_sincrostockwebinmediato #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_sincrostockwebinmediato(modelos.mtd_eg_sincrostockwebinmediato, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_sincrostockwebinmediato #
class elganso_sync_eg_sincrostockwebinmediato(interna_eg_sincrostockwebinmediato, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_sincrostockwebinmediato #
class eg_sincrostockwebinmediato(elganso_sync_eg_sincrostockwebinmediato, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_sincrostockwebinmediato_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
