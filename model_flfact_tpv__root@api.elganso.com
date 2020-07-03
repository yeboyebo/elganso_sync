# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
from YBLEGACY.constantes import *
from random import choice
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(interna):

    params = syncppal.iface.get_param_sincro('apipass')

    def elganso_sync_tienebonoregistro(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                q = qsatype.FLSqlQuery()
                q.setTablesList(u"eg_bonos")
                q.setSelect(u"codbono, venta, email")
                q.setFrom(u"eg_bonos")
                q.setWhere("venta like '%FIDELIZACION%' AND email = '" + params["email"].lower() + "'")
                if not q.exec_():
                    return {"Error": "Bono incorrecto", "status": -1}
                if q.size() == 0:
                    return False
                else:
                    return True
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_consultabonoventa(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "codigoVenta" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                q = qsatype.FLSqlQuery()
                q.setTablesList(u"eg_bonos")
                q.setSelect(u"codbono, saldoinicial, saldopendiente, coddivisa, venta")
                q.setFrom(u"eg_bonos")
                q.setWhere(ustr(u"venta = '", params['codigoVenta'], u"'"))
                if not q.exec_():
                    return {"Error": "Bono incorrecto", "status": -1}
                if q.size() > 1:
                    return {"Error": "Bono asociado a mas de una venta", "status": -2}
                if not q.next():
                    return {"Error": "Bono incorrecto", "status": -3}
                codbono = q.value("codbono")
                saldopendiente = q.value("saldopendiente")
                saldoinicial = q.value("saldoinicial")
                coddivisa = q.value("coddivisa")
                venta = q.value("venta")
                return {"saldoBono": saldoinicial, "saldoPendiente": saldopendiente, "codigoBono": codbono, "divisa": coddivisa, "venta": venta}
            else:
                return {"Error": "Petición Incorrecta", "status": 0}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_consultabono(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "codigoBono" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                codbono = params['codigoBono']
                # saldopendiente = qsatype.FLUtil.sqlSelect(u"eg_bonos", u"saldopendiente", ustr(u"codbono = '", codbono, u"'"))
                q = qsatype.FLSqlQuery()
                q.setTablesList(u"eg_bonos")
                q.setSelect(u"codbono, saldoinicial, saldopendiente, coddivisa, venta, email, fechaexpiracion, importeminimo")
                q.setFrom(u"eg_bonos")
                q.setWhere(ustr(u"codbono = '", codbono, u"'"))
                if not q.exec_():
                    return {"Error": "Bono incorrecto", "status": -1}
                if q.size() > 1:
                    return {"Error": "Bono asociado a mas de una venta", "status": -2}
                if not q.next():
                    return {"Error": "Bono incorrecto", "status": -3}
                saldopendiente = q.value("saldopendiente")
                saldoinicial = q.value("saldoinicial")
                coddivisa = q.value("coddivisa")
                venta = q.value("venta")
                email = q.value("email") or ""
                fechaexpiracion = q.value("fechaexpiracion") or ""
                importeminimo = q.value("importeminimo") or 0
                if saldopendiente == 0:
                    return {"saldoBono": saldoinicial, "saldoPendiente": saldopendiente, "divisa": coddivisa, "venta": venta, "email": email, "fechaexpiracion": fechaexpiracion, "importeminimo": importeminimo}
                if not saldopendiente:
                    return {"Error": "Bono incorrecto", "status": 1}
                return {"saldoBono": saldoinicial, "saldoPendiente": saldopendiente, "divisa": coddivisa, "venta": venta, "email": email, "fechaexpiracion": fechaexpiracion, "importeminimo": importeminimo}
            else:
                return {"Error": "Petición Incorrecta", "status": -1}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado consulta de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": -2}
        return False

    def elganso_sync_generaCodBono(self):
        longitud = 6
        valores = "0123456789abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        codbono = ""
        codbono = codbono.join([choice(valores) for i in range(longitud)])
        codbono = "BX" + codbono
        return codbono

    def elganso_sync_creabono(self, params):
        try:
            print(params)
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "importeVenta" not in params or "codigoVenta" not in params or "divisa" not in params or "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}

                if params['divisa'] != "EUR" and params['divisa'] != "GBP":
                    return {"Error": "Formato divisa incorrecto", "status": -1}

                observaciones = ""
                if "observaciones" in params:
                    observaciones = params["observaciones"]

                fechaexpiracion = None
                if "fechaExpiracion" in params:
                    fechaexpiracion = params["fechaExpiracion"]
                    fecha = qsatype.Date(fechaexpiracion)
                    if not fecha:
                        return {"Error": "Formato fecha Incorrecto", "status": 0}

                importeminimo = 0
                if "importeMinimo" in params:
                    importeminimo = params["importeMinimo"]

                # tarjeta = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"codtarjetapuntos", ustr(u"email = '", params['email'], u"'"))
                deempleado = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"deempleado", ustr(u"email = '", params['email'].lower(), u"'"))
                dtoespecial = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"dtoespecial", ustr(u"email = '", params['email'].lower(), u"'"))
                if deempleado or dtoespecial:
                    return {"Error": "Es un cliente especial", "status": -3}
                # venta = params['codigoVenta']
                importe = float(params['importeVenta'])
                importe = (importe * 20) / 100
                codbono = self.generaCodBono()
                horaalta = str(qsatype.Date())[-8:]
                while codbono == qsatype.FLUtil.sqlSelect(u"eg_bonos", u"codbono", ustr(u"codbono = '", codbono, u"'")):
                    codbono = self.generaCodBono()
                if not qsatype.FLUtil.sqlInsert(u"eg_bonos", [u"codbono", u"fecha", u"fechaalta", u"horaalta", u"venta", u"saldoinicial", u"saldoconsumido", u"saldopendiente", u"activo", u"fechaexpiracion", u"coddivisa", u"email", u"observaciones", u"importeminimo", u"correoenviado"], [codbono, str(qsatype.Date())[:10], str(qsatype.Date())[:10], horaalta, params['codigoVenta'], importe, 0, importe, True, fechaexpiracion, params['divisa'], params['email'].lower(), observaciones, importeminimo, True]):
                    return {"Error": "Error en insercion de bono", "status": -2}
                return {"codigoBono": codbono, "importeBono": importe, "status": 1}
            else:
                return {"Error": "Petición Incorrecta", "status": 0}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado generacion de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_actualizabono(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
                if "importeVenta" not in params or "codigoBono" not in params or "codigoVenta" not in params or "divisa" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}
                codbono = params['codigoBono']
                importe = params['importeVenta']
                divisa = params['divisa']
                curBono = qsatype.FLSqlCursor(u"eg_bonos")
                curBono.setModeAccess(curBono.Edit)
                curBono.refreshBuffer()
                curBono.select(ustr(u"codbono = '", codbono, u"'"))

                # Comprobaciones
                if not curBono.first():
                    qsatype.debug(ustr(u"El bono no esta activo o no se encuentrao: ", codbono))
                    return {"Error": "El bono no se encuentra", "status": -1}
                if not curBono.valueBuffer("activo"):
                    qsatype.debug(ustr(u"El bono no esta activo o no se encuentrao: ", codbono))
                    return {"Error": "El bono no esta activo", "status": -2}
                if (float(curBono.valueBuffer("saldopendiente")) - (float(importe)) * -1) < 0:
                    importe = float(curBono.valueBuffer("saldopendiente")) * -1
                if divisa != curBono.valueBuffer("coddivisa"):
                    return {"Error": "Divisas no coinciden", "status": -5}

                # Insertamos movibono
                if not qsatype.FLUtil.sqlInsert(u"eg_movibono", [u"codbono", u"fecha", u"venta", u"importe"], [codbono, str(qsatype.Date())[:10], params['codigoVenta'], importe]):
                    return {"Error": "Error en insercion de movimiento de bono", "status": -4}

                saldoconsumido = qsatype.FLUtil.sqlSelect(u"eg_movibono", u"SUM(importe)", ustr(u"codbono = '", codbono, u"'"))
                saldoconsumido = saldoconsumido * -1
                curBono.setValueBuffer("saldoconsumido", saldoconsumido)
                saldopendiente = curBono.valueBuffer("saldoinicial") - saldoconsumido
                curBono.setValueBuffer("saldopendiente", saldopendiente)
                if not curBono.commitBuffer():
                    return {"Error": "Error actualizando bono", "status": -6}
                return {"saldoPendiente": saldopendiente, "status": 1}
            else:
                return {"Error": "Petición Incorrecta", "status": 0}
        except Exception as e:
            qsatype.debug(params)
            qsatype.debug(ustr(u"Error inesperado generacion de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_getDesc(self):
        return "codbono"

    def __init__(self, context=None):
        super().__init__(context)

    def tienebonoregistro(self, params):
        return self.ctx.elganso_sync_tienebonoregistro(params)

    def consultabono(self, params):
        return self.ctx.elganso_sync_consultabono(params)

    def consultabonoventa(self, params):
        return self.ctx.elganso_sync_consultabonoventa(params)

    def creabono(self, params):
        return self.ctx.elganso_sync_creabono(params)

    def actualizabono(self, params):
        return self.ctx.elganso_sync_actualizabono(params)

    def generaCodBono(self):
        return self.ctx.elganso_sync_generaCodBono()

    def getDesc(self):
        return self.ctx.elganso_sync_getDesc()


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
