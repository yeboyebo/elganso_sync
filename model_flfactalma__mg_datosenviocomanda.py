# @class_declaration interna_mg_datosenviocomanda #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_mg_datosenviocomanda(modelos.mtd_mg_datosenviocomanda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_mg_datosenviocomanda #
class elganso_sync_mg_datosenviocomanda(interna_mg_datosenviocomanda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration mg_datosenviocomanda #
class mg_datosenviocomanda(elganso_sync_mg_datosenviocomanda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.mg_datosenviocomanda_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
