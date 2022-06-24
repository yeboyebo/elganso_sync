# @class_declaration interna_eg_look #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_look(modelos.mtd_eg_look, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_look #
class elganso_sync_eg_look(interna_eg_look, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_look #
class eg_look(elganso_sync_eg_look, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_look_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
