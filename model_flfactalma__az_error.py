# @class_declaration interna_az_error #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_az_error(modelos.mtd_az_error, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_az_error #
class elganso_sync_az_error(interna_az_error, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration az_error #
class az_error(elganso_sync_az_error, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.az_error_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
