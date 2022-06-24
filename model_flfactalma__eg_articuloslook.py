# @class_declaration interna_eg_articuloslook #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_articuloslook(modelos.mtd_eg_articuloslook, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_articuloslook #
class elganso_sync_eg_articuloslook(interna_eg_articuloslook, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_articuloslook #
class eg_articuloslook(elganso_sync_eg_articuloslook, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_articuloslook_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
