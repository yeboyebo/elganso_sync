# @class_declaration interna_eg_devolucionestienda #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_devolucionestienda(modelos.mtd_eg_devolucionestienda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_devolucionestienda #
class elganso_sync_eg_devolucionestienda(interna_eg_devolucionestienda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_devolucionestienda #
class eg_devolucionestienda(elganso_sync_eg_devolucionestienda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_devolucionestienda_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
