# @class_declaration interna_solicitudescliente #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactppal import models as modelos


class interna_solicitudescliente(modelos.mtd_solicitudescliente, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_solicitudescliente #
class elganso_sync_solicitudescliente(interna_solicitudescliente, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def crearsolicitudcliente(params):
        return form.iface.crearsolicitudcliente(params)


# @class_declaration solicitudescliente #
class solicitudescliente(elganso_sync_solicitudescliente, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactppal.solicitudescliente_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
