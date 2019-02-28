# @class_declaration interna_eg_movibono #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_eg_movibono(modelos.mtd_eg_movibono, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_movibono #
class elganso_sync_eg_movibono(interna_eg_movibono, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_movibono #
class eg_movibono(elganso_sync_eg_movibono, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.eg_movibono_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
