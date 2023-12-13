# @class_declaration interna_vp_articulosprivalia #
import importlib

from YBUTILS.viewREST import helpers

from models.flfact_tpv import models as modelos


class interna_vp_articulosprivalia(modelos.mtd_vp_articulosprivalia, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_vp_articulosprivalia #
class elganso_sync_vp_articulosprivalia(interna_vp_articulosprivalia, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration vp_articulosprivalia #
class vp_articulosprivalia(elganso_sync_vp_articulosprivalia, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfact_tpv.vp_articulosprivalia_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
