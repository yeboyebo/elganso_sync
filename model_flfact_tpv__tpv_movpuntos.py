# @class_declaration interna_tpv_movpuntos #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_tpv_movpuntos(modelos.mtd_tpv_movpuntos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_tpv_movpuntos #
class elganso_sync_tpv_movpuntos(interna_tpv_movpuntos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration tpv_movpuntos #
class tpv_movpuntos(elganso_sync_tpv_movpuntos, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.tpv_movpuntos_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
