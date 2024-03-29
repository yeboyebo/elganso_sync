# @class_declaration interna_mg_customers #
import importlib

from YBUTILS.viewREST import helpers

from models.flfactalma import models as modelos


class interna_mg_customers(modelos.mtd_mg_customers, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True


# @class_declaration elganso_sync_mg_customers #
class elganso_sync_mg_customers(interna_mg_customers, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    @helpers.decoradores.csr()
    def mg2customer(params):
        return form.iface.mg2customer(params)


# @class_declaration mg_customers #
class mg_customers(elganso_sync_mg_customers, helpers.MixinConAcciones):
    pass

    class Meta:
        proxy = True

    def getIface(self=None):
        return form.iface


definitions = importlib.import_module("models.flfactalma.mg_customers_def")
form = definitions.FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
