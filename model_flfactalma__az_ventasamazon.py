# @class_declaration interna_az_ventasamazon #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_az_ventasamazon(modelos.mtd_az_ventasamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_az_ventasamazon #
class elganso_sync_az_ventasamazon(interna_az_ventasamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration az_ventasamazon #
class az_ventasamazon(elganso_sync_az_ventasamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.az_ventasamazon_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
