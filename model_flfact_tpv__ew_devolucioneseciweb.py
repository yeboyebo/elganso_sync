# @class_declaration interna_ew_devolucioneseciweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_ew_devolucioneseciweb(modelos.mtd_ew_devolucioneseciweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_ew_devolucioneseciweb #
class elganso_sync_ew_devolucioneseciweb(interna_ew_devolucioneseciweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration ew_devolucioneseciweb #
class ew_devolucioneseciweb(elganso_sync_ew_devolucioneseciweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.ew_devolucioneseciweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
