# @class_declaration interna_eg_anulacionstockreservado #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_anulacionstockreservado(modelos.mtd_eg_anulacionstockreservado, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_anulacionstockreservado #
class elganso_sync_eg_anulacionstockreservado(interna_eg_anulacionstockreservado, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_anulacionstockreservado #
class eg_anulacionstockreservado(elganso_sync_eg_anulacionstockreservado, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_anulacionstockreservado_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
