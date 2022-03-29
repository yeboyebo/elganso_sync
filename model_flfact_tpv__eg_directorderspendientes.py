# @class_declaration interna_eg_directorderspendientes #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_directorderspendientes(modelos.mtd_eg_directorderspendientes, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_directorderspendientes #
class elganso_sync_eg_directorderspendientes(interna_eg_directorderspendientes, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_directorderspendientes #
class eg_directorderspendientes(elganso_sync_eg_directorderspendientes, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_directorderspendientes_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
