
# @class_declaration elganso_sync #
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(flfact_tpv):

    params = syncppal.iface.get_param_sincro('apipass')

    def elganso_sync_eglogpedidosweb(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:

                if "order" not in params:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro order", "status": 0}

                if "increment_id" not in params['order']:
                    return {"Error": "Formato Incorrecto. No viene el parametro increment_id dentro de order", "status": 0}

                curLogPedidoWeb = qsatype.FLSqlCursor("eg_logpedidosweb")
                curLogPedidoWeb.setModeAccess(curLogPedidoWeb.Insert)
                curLogPedidoWeb.refreshBuffer()
                curLogPedidoWeb.setValueBuffer("procesado", False)
                curLogPedidoWeb.setValueBuffer("fechaalta", str(qsatype.Date())[:10])
                curLogPedidoWeb.setValueBuffer("horaalta", str(qsatype.Date())[-8:])
                curLogPedidoWeb.setValueBuffer("increment_id", str(params["order"]["increment_id"]))
                curLogPedidoWeb.setValueBuffer("codcomanda", "WEB" + str(params["order"]["increment_id"]))
                curLogPedidoWeb.setValueBuffer("website", "magento2")
                curLogPedidoWeb.setValueBuffer("cuerpolog", str(params["order"]))
                if not curLogPedidoWeb.commitBuffer():
                    return False
                return True
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def __init__(self, context=None):
        super().__init__(context)

    def eglogpedidosweb(self, params):
        return self.ctx.elganso_sync_eglogpedidosweb(params)

