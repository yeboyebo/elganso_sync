# @class_declaration interna_az_articulosamazon #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_az_articulosamazon(modelos.mtd_az_articulosamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_az_articulosamazon #
class elganso_sync_az_articulosamazon(interna_az_articulosamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration az_articulosamazon #
class az_articulosamazon(elganso_sync_az_articulosamazon, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.az_articulosamazon_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
