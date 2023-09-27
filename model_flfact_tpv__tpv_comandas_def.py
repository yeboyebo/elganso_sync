
# @class_declaration elganso_sync #
from models.flsyncppal import flsyncppal_def as syncppal
import requests

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

                existe_pedido = qsatype.FLUtil.quickSqlSelect("eg_logpedidosweb", "codcomanda", "estadopedidomagento = '{}' AND increment_id = '{}'".format(str(params["order"]["status"]), str(params["order"]["increment_id"])))
                if existe_pedido:
                    return True

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
                curLogPedidoWeb.setValueBuffer("estadopedidomagento", str(params["order"]["status"]))


                if "codcanalweb" in params['order']:
                    curLogPedidoWeb.setValueBuffer("codcanalweb", str(params["order"]["codcanalweb"]))

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

    def elganso_sync_eglogdevolucionesweb(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:

                if "refound" not in params:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro refound", "status": 0}

                if "rma_id" not in params['refound']:
                    return {"Error": "Formato Incorrecto. No viene el parametro rma_id dentro de order", "status": 0}

                curLogDevolucionWeb = qsatype.FLSqlCursor("eg_logdevolucionesweb")
                curLogDevolucionWeb.setModeAccess(curLogDevolucionWeb.Insert)
                curLogDevolucionWeb.refreshBuffer()
                curLogDevolucionWeb.setValueBuffer("procesado", False)
                curLogDevolucionWeb.setValueBuffer("fechaalta", str(qsatype.Date())[:10])
                curLogDevolucionWeb.setValueBuffer("horaalta", str(qsatype.Date())[-8:])
                curLogDevolucionWeb.setValueBuffer("rma_id", str(params["refound"]["rma_id"]))
                curLogDevolucionWeb.setValueBuffer("codcomanda", "WDV" + str(params["refound"]["rma_id"]))
                curLogDevolucionWeb.setValueBuffer("website", "magento2")
                curLogDevolucionWeb.setValueBuffer("cuerpolog", str(params["refound"]))
                if not curLogDevolucionWeb.commitBuffer():
                    return False
                return True
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_consultasaft(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:

                if "codcomanda" not in params:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro codcomanda", "status": 0}
                print("////*******CODCOMANDA: ", params["codcomanda"])
                url = "https://ediwinws.sedeb2b.com/EdiwinWS/rest/EdiwinIntegrationRest/getCustomData"
                payload={'user': 'WS_EDIWIN_INTEGRATION_510138543',
                'password': '85ufripdsd',
                'domain': '510138543',
                'process': 'IN_RESPONSE_SAFT_INVOICE_GETCUSTOMDATA_510138543',
                'parameters': '[{"name": "IDEXTERNO", "operator": "LIKE", "value": "' + params["codcomanda"] + '"}]',
                'unzipResponse': 'true'}
                files=[]
                headers = {}

                #response = self.send_request("post", url, headers=headers, data=payload, files=files)
                response = requests.request("post", url, headers=headers, data=payload, files=files)

                print(response.text)

                return {"datos": response.text}
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_eglogpedidosb2b(self, params):
        print("ENTRA")
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                print(1)
                if "order" not in params:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro order", "status": 0}
                print(2)
                if "increment_id" not in params['order']:
                    return {"Error": "Formato Incorrecto. No viene el parametro increment_id dentro de order", "status": 0}

                existe_pedido = qsatype.FLUtil.quickSqlSelect("eg_logpedidosb2b", "increment_id", "increment_id = '{}'".format(str(params["order"]["increment_id"])))
                if existe_pedido:
                    return True

                curLogPedidoB2b = qsatype.FLSqlCursor("eg_logpedidosb2b")
                curLogPedidoB2b.setModeAccess(curLogPedidoB2b.Insert)
                curLogPedidoB2b.refreshBuffer()
                curLogPedidoB2b.setValueBuffer("procesado", False)
                curLogPedidoB2b.setValueBuffer("fechaalta", str(qsatype.Date())[:10])
                curLogPedidoB2b.setValueBuffer("horaalta", str(qsatype.Date())[-8:])
                curLogPedidoB2b.setValueBuffer("increment_id", str(params["order"]["increment_id"]))
                curLogPedidoB2b.setValueBuffer("codpedido", "")
                curLogPedidoB2b.setValueBuffer("cuerpolog", str(params["order"]))
                curLogPedidoB2b.setValueBuffer("estadopedidomagento", "")

                if not curLogPedidoB2b.commitBuffer():
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

    def eglogdevolucionesweb(self, params):
        return self.ctx.elganso_sync_eglogdevolucionesweb(params)

    def consultasaft(self, params):
        return self.ctx.elganso_sync_consultasaft(params)

    def eglogpedidosb2b(self, params):
        return self.ctx.elganso_sync_eglogpedidosb2b(params)

