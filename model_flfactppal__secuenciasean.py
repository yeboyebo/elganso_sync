# @class_declaration interna_secuenciasean #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactppal import models as modelos


class interna_secuenciasean(modelos.mtd_secuenciasean, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_secuenciasean #
class elganso_sync_secuenciasean(interna_secuenciasean, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration secuenciasean #
class secuenciasean(elganso_sync_secuenciasean, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactppal.secuenciasean_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
