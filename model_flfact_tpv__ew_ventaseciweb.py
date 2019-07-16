# @class_declaration interna_ew_ventaseciweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_ew_ventaseciweb(modelos.mtd_ew_ventaseciweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_ew_ventaseciweb #
class elganso_sync_ew_ventaseciweb(interna_ew_ventaseciweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration ew_ventaseciweb #
class ew_ventaseciweb(elganso_sync_ew_ventaseciweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.ew_ventaseciweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
