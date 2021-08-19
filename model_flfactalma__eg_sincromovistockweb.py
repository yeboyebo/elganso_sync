# @class_declaration interna_eg_sincromovistockweb #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_eg_sincromovistockweb(modelos.mtd_eg_sincromovistockweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_eg_sincromovistockweb #
class elganso_sync_eg_sincromovistockweb(interna_eg_sincromovistockweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration eg_sincromovistockweb #
class eg_sincromovistockweb(elganso_sync_eg_sincromovistockweb, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.eg_sincromovistockweb_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
