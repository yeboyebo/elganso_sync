# @class_declaration interna_eg_lineasdevolucioneswebtienda #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_lineasdevolucioneswebtienda(modelos.mtd_eg_lineasdevolucioneswebtienda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_lineasdevolucioneswebtienda #
class elganso_sync_eg_lineasdevolucioneswebtienda(interna_eg_lineasdevolucioneswebtienda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_lineasdevolucioneswebtienda #
class eg_lineasdevolucioneswebtienda(elganso_sync_eg_lineasdevolucioneswebtienda, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_lineasdevolucioneswebtienda_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
