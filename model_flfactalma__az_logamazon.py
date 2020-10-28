# @class_declaration interna_az_logamazon #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_az_logamazon(modelos.mtd_az_logamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_az_logamazon #
class elganso_sync_az_logamazon(interna_az_logamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration az_logamazon #
class az_logamazon(elganso_sync_az_logamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.az_logamazon_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
