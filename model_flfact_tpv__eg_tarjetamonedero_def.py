# @class_declaration interna #
from YBLEGACY import qsatype
import json

class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
from YBLEGACY.constantes import *
from random import randrange, choice
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(interna):

    params = {}

    def elganso_sync_getDesc(self):
        return None

    def __init__(self, context=None):
        super().__init__(context)

    def elganso_sync_consultatarjetamonedero(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                
                if "codUso" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
    
                q = qsatype.FLSqlQuery()
                q.setSelect(u"codactivacion, saldoinicial, saldopendiente, coddivisa, venta, email, emailregalo, activo")
                q.setFrom(u"eg_tarjetamonedero")
                q.setWhere(ustr(u"coduso = '", params['codUso'], u"'"))

                if not q.exec_():
                    return {"Error": "Fallo consulta.", "status": -1}

                if q.size() > 1:
                    return {"Error": "Hay mas de una tarjeta monedero con el mismo código de uso", "status": -2}

                if not q.next():
                    return {"Error": "No se encuentra la tarjeta monedero", "status": -3}
               
                if q.value("activo") is False:
                    return {"Error": "La Tarjeta monedero no está activa", "status": 1}

  
                return {"saldoTarjeta": q.value("saldoinicial"), "saldoPendiente": q.value("saldopendiente"), "divisa": q.value("coddivisa"), "venta": q.value("venta"), "email": q.value("email"), "emailregalo": q.value("emailregalo"), "activo": q.value("activo")}
               
                
            else:
                return {"Error": "Petición Incorrecta", "status": -1}
        except Exception as e:
            return {"Error": "Petición Incorrectaa", "status": -2}
        return False

    def elganso_sync_actualizatarjetamonedero(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')

            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "codUso" not in params:
                    return {"Error": "Falta el código de uso", "status": -8}
                
                if "codigoVenta" not in params:
                    return {"Error": "Falta el código de la venta", "status": -9}
            
                if "importeVenta" not in params:
                    return {"Error": "Falta el importe de la venta", "status": -1}
                        
                if "codDivisa" not in params:
                    return {"Error": "Falta el código de la divisa", "status": -1}
                

                curTarjeta = qsatype.FLSqlCursor(u"eg_tarjetamonedero")
                curTarjeta.select("coduso = '" + str(params["codUso"]) + "'")

                # Comprobaciones
                if not curTarjeta.first():
                    return {"Error": "No se encuentra la tarjeta monedero con código de uso: " + str(params["codUso"]), "status": -3}

                curTarjeta.setModeAccess(curTarjeta.Edit)
                curTarjeta.refreshBuffer()

                if not curTarjeta.valueBuffer("activo"):
                    return {"Error": "La tarjeta monedero con código de uso " + str(params["codUso"]) + " no está activa", "status": -2}

                if (parseFloat(curTarjeta.valueBuffer("saldopendiente")) - (parseFloat(params['importeVenta'])) * -1) < 0:
                    importe = parseFloat(curTarjeta.valueBuffer("saldopendiente")) * -1
        
                if params["codDivisa"] != curTarjeta.valueBuffer("coddivisa"):
                    return {"Error": "Divisas no coinciden", "status": -5}


                curMoviTarjeta = qsatype.FLSqlCursor("eg_movitarjetamonedero")
                curMoviTarjeta.setModeAccess(curMoviTarjeta.Insert)
                curMoviTarjeta.refreshBuffer()
                curMoviTarjeta.setValueBuffer("coduso", str(params["codUso"]))
                curMoviTarjeta.setValueBuffer("fecha", str(qsatype.Date())[:10])
                curMoviTarjeta.setValueBuffer("codcomanda", str(params['codigoVenta']))
                curMoviTarjeta.setValueBuffer("importe", parseFloat(params["importeVenta"]) * -1)
                curMoviTarjeta.setValueBuffer("idtarjeta", curTarjeta.valueBuffer("idtarjeta"))
                if not curMoviTarjeta.commitBuffer():
                    return {"Error": "Error en inserción de movimiento de la tarjeta monedero", "status": -4}

                saldoconsumido = qsatype.FLUtil.sqlSelect(u"eg_movitarjetamonedero", u"SUM(importe)", ustr(u"coduso = '", str(params["codUso"]), u"'")) * -1

                curTarjeta.setValueBuffer("saldoconsumido", saldoconsumido)
                saldopendiente = curTarjeta.valueBuffer("saldoinicial") - saldoconsumido
                curTarjeta.setValueBuffer("saldopendiente", saldopendiente)

                if not curTarjeta.commitBuffer():
                    return {"Error": "Error actualizando la tarjeta monedero", "status": -6}
                return {"saldoPendiente": saldopendiente, "status": 1}

            else:
                return {"Error": "Petición Incorrecta", "status": -7}
        except Exception as e:
            return {"Error": "Petición Incorrecta. EXCEPCION: " + e, "status": 0}
        return False

    def elganso_sync_creatarjetamonedero(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')

            if "passwd" in params and params['passwd'] == self.params['auth']:

                if "codigoVenta" not in params:
                    return {"Error": "Formato Incorrecto. Falta el nodo codigoVenta", "status": -1}

                if "email" not in params:
                    return {"Error": "Formato Incorrecto. Falta el nodo email", "status": -1}

                if "importeTarjeta" not in params:
                    return {"Error": "Formato Incorrecto. Falta el nodo importeTarjeta", "status": -1}

                if "codDivisa" not in params:
                    return {"Error": "Formato Incorrecto. Falta el nodo codDivisa", "status": -1}

                if params['codDivisa'] != "EUR" and params['codDivisa'] != "GBP":
                    return {"Error": "Formato divisa incorrecto", "status": -1}

                cod_uso = qsatype.FactoriaModulos.get('flfact_tpv').iface.calculaCodUsoTarjetaRegalo()
                while cod_uso == qsatype.FLUtil.sqlSelect(u"eg_tarjetamonedero", u"coduso", ustr(u"coduso = '", cod_uso, u"'")):
                    cod_uso = qsatype.FactoriaModulos.get('flfact_tpv').iface.calculaCodUsoTarjetaRegalo()

                cod_activacion = qsatype.FactoriaModulos.get('flfact_tpv').iface.calculaCodTarjetaRegalo()
                while cod_activacion == qsatype.FLUtil.sqlSelect(u"eg_tarjetamonedero", u"codactivacion", ustr(u"codactivacion = '", cod_activacion, u"'")):
                    cod_activacion = qsatype.FactoriaModulos.get('flfact_tpv').iface.calculaCodTarjetaRegalo()
                
                curTarjeta = qsatype.FLSqlCursor("eg_tarjetamonedero")
                curTarjeta.setModeAccess(curTarjeta.Insert)
                curTarjeta.refreshBuffer()

                curTarjeta.setValueBuffer("activo", True)
                curTarjeta.setValueBuffer("codactivacion", cod_activacion)
                curTarjeta.setValueBuffer("coddivisa", str(params['codDivisa']))
                curTarjeta.setValueBuffer("codtienda", "AWEB")
                curTarjeta.setValueBuffer("coduso", cod_uso)
                curTarjeta.setValueBuffer("correoenviado", False)
                curTarjeta.setValueBuffer("correoregaloenviado", False)
                curTarjeta.setValueBuffer("email", str(params['email']))
                if "emailRegalo" in params:
                    if str(params["emailRegalo"]) != "None" and str(params["emailRegalo"]) != "":
                        curTarjeta.setValueBuffer("emailregalo", str(params["emailRegalo"]))

                curTarjeta.setValueBuffer("fecha", str(qsatype.Date())[:10])
                curTarjeta.setValueBuffer("fechaactivacion", str(qsatype.Date())[:10])
                curTarjeta.setValueBuffer("saldoconsumido", 0)
                curTarjeta.setValueBuffer("saldoinicial", parseFloat(params["importeTarjeta"]))
                curTarjeta.setValueBuffer("saldopendiente", parseFloat(params["importeTarjeta"]))
                curTarjeta.setValueBuffer("venta", str(params['codigoVenta']))

                if not curTarjeta.commitBuffer():
                    return {"Error": "Error en inserción de movimiento de la tarjeta monedero", "status": -4}

                return {"codigoUso": cod_uso, "importeTarjeta": params["importeTarjeta"], "status": 1}
            else:
                return {"Error": "Petición Incorrecta", "status": 0}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado generacion de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def getDesc(self):
        return self.ctx.elganso_sync_getDesc()

    def consultatarjetamonedero(self, params):
        return self.ctx.elganso_sync_consultatarjetamonedero(params)

    def actualizatarjetamonedero(self, params):
        return self.ctx.elganso_sync_actualizatarjetamonedero(params)

    def creatarjetamonedero(self, params):
        return self.ctx.elganso_sync_creatarjetamonedero(params)



# @class_declaration head #
class head(elganso_sync):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)
