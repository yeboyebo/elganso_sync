# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
from YBLEGACY.constantes import *
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(interna):

    params = syncppal.iface.get_param_sincro('apipass')

    def elganso_sync_getDesc(self):
        return None

    def elganso_sync_desuscribesm(self, params):
        try:
            bdparams = self.params
            if "auth" not in bdparams:
                bdparams = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == bdparams['auth']:
                if "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}
                qsatype.debug(ustr(u"desuscribesm: ", params['email']))
                curTpvTarjetas = qsatype.FLSqlCursor(u"tpv_tarjetaspuntos")

                q = qsatype.FLSqlQuery()
                q.setSelect(u"codtarjetapuntos")
                q.setFrom(u"tpv_tarjetaspuntos")
                q.setWhere(ustr(u"email = '", params['email'], "'"))
                if not q.exec_():
                    return False

                while q.next():
                    curTpvTarjetas.select(ustr(u"codtarjetapuntos = '", q.value(u"codtarjetapuntos"), "'"))
                    if not curTpvTarjetas.first():
                        return False
                    curTpvTarjetas.setModeAccess(curTpvTarjetas.Edit)
                    curTpvTarjetas.refreshBuffer()
                    curTpvTarjetas.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                    curTpvTarjetas.setValueBuffer("horamod", str(qsatype.Date())[-8:])
                    curTpvTarjetas.setValueBuffer("sincronizada", False)
                    curTpvTarjetas.setValueBuffer("suscritocrm", False)
                    if not curTpvTarjetas.commitBuffer():
                        return False

                return True
            else:
                return {"Error": "Formato Incorrecto", "status": -1}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado desuscribesm: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_suscribesm(self, params):
        try:
            bdparams = self.params
            if "auth" not in bdparams:
                bdparams = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == bdparams['auth']:
                if "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}
                qsatype.debug(ustr(u"suscribesm: ", params['email']))
                curTpvTarjetas = qsatype.FLSqlCursor(u"tpv_tarjetaspuntos")

                q = qsatype.FLSqlQuery()
                q.setSelect(u"codtarjetapuntos")
                q.setFrom(u"tpv_tarjetaspuntos")
                q.setWhere(ustr(u"email = '", params['email'], "'"))
                if not q.exec_():
                    return False

                while q.next():
                    curTpvTarjetas.select(ustr(u"codtarjetapuntos = '", q.value(u"codtarjetapuntos"), "'"))
                    if not curTpvTarjetas.first():
                        return False
                    curTpvTarjetas.setModeAccess(curTpvTarjetas.Edit)
                    curTpvTarjetas.refreshBuffer()
                    curTpvTarjetas.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                    curTpvTarjetas.setValueBuffer("horamod", str(qsatype.Date())[-8:])
                    curTpvTarjetas.setValueBuffer("sincronizada", False)
                    curTpvTarjetas.setValueBuffer("suscritocrm", True)
                    if not curTpvTarjetas.commitBuffer():
                        return False
                return True
            else:
                return {"Error": "Formato Incorrecto", "status": -1}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado suscribesm: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_unificartarjetas(self, params):
        try:
            bdparams = self.params
            if "auth" not in bdparams:
                bdparams = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == bdparams['auth']:
                if "emailOrigen" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}
                if "emailDestino" not in params:
                    return {"Error": "Formato Incorrecto", "status": -1}

                saldoPuntosOrigen = qsatype.FLUtil.sqlSelect("tpv_tarjetaspuntos", "saldopuntos", "email = '" + str(params['emailOrigen']) + "'")

                if not self.quitarPuntosTarjetaOrigen(params):
                    return False

                if not self.acumularPuntosTarjetaDestino(params, saldoPuntosOrigen):
                    return False

                if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_tarjetaspuntos SET saldopuntos = CASE WHEN (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) IS NULL THEN 0 ELSE (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) END WHERE email = '", str(params['emailOrigen']), "'")):
                    return False

                if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_tarjetaspuntos SET saldopuntos = CASE WHEN (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) IS NULL THEN 0 ELSE (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) END WHERE email = '", str(params['emailDestino']), "'")):
                    return False

                return True
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado unificartarjetas: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}

        return True

    def elganso_sync_quitarPuntosTarjetaOrigen(self, params):
        curTpvTarjetas = qsatype.FLSqlCursor("tpv_tarjetaspuntos")
        q = qsatype.FLSqlQuery()
        q.setSelect("codtarjetapuntos, saldopuntos")
        q.setFrom("tpv_tarjetaspuntos")
        q.setWhere("email = '" + str(params['emailOrigen']) + "'")

        if not q.exec_():
            return False

        while q.next():

            curTpvTarjetas.select("codtarjetapuntos = '" + q.value("codtarjetapuntos") + "'")
            if not curTpvTarjetas.first():
                return False

            curTpvTarjetas.setModeAccess(curTpvTarjetas.Edit)
            curTpvTarjetas.refreshBuffer()
            saldoPuntos = float(q.value("saldopuntos")) * (-1)

            curMP = qsatype.FLSqlCursor("tpv_movpuntos")
            curMP.setModeAccess(curMP.Insert)
            curMP.refreshBuffer()
            curMP.setValueBuffer("codtarjetapuntos", str(q.value("codtarjetapuntos")))
            curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
            curMP.setValueBuffer("horamod", str(qsatype.Date())[-(8):])
            curMP.setValueBuffer("canpuntos", saldoPuntos)
            curMP.setValueBuffer("operacion", "UNIFICACION PUNTOS " + str(params['emailDestino']))
            curMP.setValueBuffer("sincronizado", False)
            curMP.setValueBuffer("codtienda", "AWEB")

            if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                return False

            if not curMP.commitBuffer():
                return False

            if not curTpvTarjetas.commitBuffer():
                return False

        return True

    def elganso_sync_acumularPuntosTarjetaDestino(self, params, saldoPuntosOrigen):
        curTpvTarjetas = qsatype.FLSqlCursor("tpv_tarjetaspuntos")
        q = qsatype.FLSqlQuery()
        q.setSelect("codtarjetapuntos, saldopuntos")
        q.setFrom("tpv_tarjetaspuntos")
        q.setWhere("email = '" + str(params['emailDestino']) + "'")

        if not q.exec_():
            return False

        while q.next():

            curTpvTarjetas.select("codtarjetapuntos = '" + q.value("codtarjetapuntos") + "'")
            if not curTpvTarjetas.first():
                return False

            curTpvTarjetas.setModeAccess(curTpvTarjetas.Edit)
            curTpvTarjetas.refreshBuffer()

            curMP = qsatype.FLSqlCursor("tpv_movpuntos")
            curMP.setModeAccess(curMP.Insert)
            curMP.refreshBuffer()
            curMP.setValueBuffer("codtarjetapuntos", str(q.value("codtarjetapuntos")))
            curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
            curMP.setValueBuffer("horamod", str(qsatype.Date())[-(8):])
            curMP.setValueBuffer("canpuntos", saldoPuntosOrigen)
            curMP.setValueBuffer("operacion", "UNIFICACION PUNTOS " + str(params['emailOrigen']))
            curMP.setValueBuffer("sincronizado", False)
            curMP.setValueBuffer("codtienda", "AWEB")

            if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                return False

            if not curMP.commitBuffer():
                return False

            if not curTpvTarjetas.commitBuffer():
                return False

        return True

    def elganso_sync_generarmovimentopuntosoperacionesmagento(self, params):
        try:
            bdparams = self.params
            if "auth" not in bdparams:
                bdparams = syncppal.iface.get_param_sincro('apipass')

            if "passwd" in params and params['passwd'] == bdparams['auth']:

                if "email" not in params:
                    return {"Error": "Formato Incorrecto. Falta el email en los parametros", "status": -1}
                if "operacion" not in params:
                    return {"Error": "Formato Incorrecto. Falta la operacion en los parametros", "status": -1}
                if "canpuntos" not in params:
                    return {"Error": "Formato Incorrecto. Falta la cantidad de puntos en los parametros", "status": -1}

                params['saldo'] = 0
                if not self.acumularPuntosOperacionesMagento(params):
                    return False
                    
                saldo = parseFloat(params['saldo'])
                email = str(params['email'])

                if "codtarjetapuntos" in params:
                    if not qsatype.FLSqlQuery().execSql(ustr(u"UPDATE tpv_tarjetaspuntos SET saldopuntos = " , saldo , " WHERE codtarjetapuntos = '" , str(params['codtarjetapuntos']) , "'")):
                        return False
                else:
                    if not qsatype.FLSqlQuery().execSql(ustr(u"UPDATE tpv_tarjetaspuntos SET saldopuntos = " , saldo , " WHERE email = '" , email , "'")):
                        return False

                return True
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado generarmovimentopuntosoperacionesmagento: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}

        return True

    def elganso_sync_acumularPuntosOperacionesMagento(self, params):
        curTpvTarjetas = qsatype.FLSqlCursor("tpv_tarjetaspuntos")
        q = qsatype.FLSqlQuery()
        q.setSelect("codtarjetapuntos, saldopuntos")
        q.setFrom("tpv_tarjetaspuntos")
        if "codtarjetapuntos" in params:
            q.setWhere("codtarjetapuntos = '" + str(params['codtarjetapuntos']) + "'")
        else:
            q.setWhere("lower(email) = '" + str(params['email']).lower() + "' limit 1")

        if not q.exec_():
            return False

        if q.size() <= 0:
            return False

        while q.next():
            curTpvTarjetas.select("codtarjetapuntos = '" + q.value("codtarjetapuntos") + "'")
            if not curTpvTarjetas.first():
                return False
            
            params["saldo"] = q.value("saldopuntos")
            idMovPuntos = qsatype.FLUtil.sqlSelect("tpv_movpuntos", "idmovpuntos", "canpuntos = " + params['canpuntos'] + " AND operacion = '" + str(params['operacion']) + "'")
            
            if idMovPuntos:
                return True

            curTpvTarjetas.setModeAccess(curTpvTarjetas.Edit)
            curTpvTarjetas.refreshBuffer()

            curMP = qsatype.FLSqlCursor("tpv_movpuntos")
            curMP.setModeAccess(curMP.Insert)
            curMP.refreshBuffer()
            curMP.setValueBuffer("codtarjetapuntos", str(q.value("codtarjetapuntos")))
            curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
            curMP.setValueBuffer("horamod", str(qsatype.Date())[-(8):])
            curMP.setValueBuffer("canpuntos", params['canpuntos'])
            curMP.setValueBuffer("operacion", str(params['operacion']))
            curMP.setValueBuffer("sincronizado", True)
            if "codTienda" in params:
                curMP.setValueBuffer("codtienda", params["codTienda"])
            else:
                curMP.setValueBuffer("codtienda", "AWEB")

            if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                return False

            if not curMP.commitBuffer():
                return False

            if not curTpvTarjetas.commitBuffer():
                return False

            params["saldo"] = qsatype.FactoriaModulos.get("formRecordtpv_tarjetaspuntos").iface.pub_commonCalculateField("saldopuntos", curTpvTarjetas)

        return True

    def elganso_sync_eglogtarjetasweb(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:

                if "customer" not in params:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro customer", "status": 0}

                if "email" not in params["customer"]:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro email", "status": 0}

                curLogTarjetasWeb = qsatype.FLSqlCursor("eg_logtarjetasweb")
                curLogTarjetasWeb.setModeAccess(curLogTarjetasWeb.Insert)
                curLogTarjetasWeb.refreshBuffer()
                curLogTarjetasWeb.setValueBuffer("procesado", False)
                curLogTarjetasWeb.setValueBuffer("fechaalta", str(qsatype.Date())[:10])
                curLogTarjetasWeb.setValueBuffer("horaalta", str(qsatype.Date())[-8:])
                curLogTarjetasWeb.setValueBuffer("email", str(params["customer"]["email"]))
                curLogTarjetasWeb.setValueBuffer("website", "magento2")
                curLogTarjetasWeb.setValueBuffer("cuerpolog", str(params["customer"]))
                if not curLogTarjetasWeb.commitBuffer():
                    return False
                return True
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_consultapuntos(self, params):
        try:
            # return {"Error": "Ahora no es posible realizar la consulta de puntos", "status": 0}
            # print("entro en consultapuntos: " + str(qsatype.Date()))
            if "passwd" in params and params["passwd"] == self.params['auth']:

                if "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                email = str(params['email']).lower()
                # print("saldo de consultapuntos: " + str(email))
                existe_tarjeta = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"codtarjetapuntos", ustr(u"lower(email) = '", email, u"'"))

                if not existe_tarjeta:
                    if qsatype.FLUtil.sqlSelect(u"eg_logtarjetasweb", u"email", ustr(u"lower(email) = '", email, u"'")):
                        if not qsatype.FLUtil.sqlSelect(u"eg_logtarjetasweb", "procesado", ustr(u"lower(email) = '", email, u"'")):
                            return {"Error": "Petición realizada, pendiente de creación", "status": 2}
                    return {"Error": "No se ha encontrado la tarjeta.", "status": 1}

                es_empleado = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"deempleado", ustr(u"lower(email) = '", email, u"' AND codtarjetapuntos = '", existe_tarjeta, u"'"))
                es_dtoespecial = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"dtoespecial", ustr(u"lower(email) = '", email, u"' AND codtarjetapuntos = '", existe_tarjeta, u"'"))
                dtopor = ""
                if es_dtoespecial:
                    dtopor = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"dtopor", ustr(u"lower(email) = '", email, u"' AND codtarjetapuntos = '", existe_tarjeta, u"'"))

                saldopuntos = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"ROUND(CAST(saldopuntos AS NUMERIC),2)", ustr(u"lower(email) = '", email, u"' AND codtarjetapuntos = '", existe_tarjeta, u"'"))
                
                # print("saldo de consultapuntos: " + str(qsatype.Date()))
                return {"saldoPuntos": saldopuntos, "email": email, "codtarjetapuntos": existe_tarjeta, "esempleado": es_empleado, "esdtoespecial": es_dtoespecial, "dtopor": dtopor}
            else:
                return {"Error": "Petición Incorrecta", "status": -1}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado consulta de puntos: ", e))
            return {"Error": params, "status": -2}
        return False

    def elganso_sync_consultamovimientospuntos(self, params):
        try:
            if "passwd" in params and params["passwd"] == self.params['auth']:

                if "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                email = str(params['email']).lower()

                existe_tarjeta = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"codtarjetapuntos", ustr(u"lower(email) = '", email, u"'"))

                if not existe_tarjeta:
                    return {"Error": "No se ha encontrado la tarjeta.", "status": 1}

                q = qsatype.FLSqlQuery()
                q.setSelect("m.idmovpuntos, m.operacion, m.fecha, m.canpuntos")
                q.setFrom("tpv_tarjetaspuntos t inner join tpv_movpuntos m on t.codtarjetapuntos = m.codtarjetapuntos")
                q.setWhere("lower(t.email) = '" + email + "' AND t.codtarjetapuntos = '" + existe_tarjeta + "' order by fecha,idmovpuntos")

                if not q.exec_():
                    return False

                movi_puntos = []
                while q.next():
                    movi_puntos.append({
                        "idmovpuntos": q.value("m.idmovpuntos"),
                        "operacion": q.value("m.operacion"),
                        "fecha": q.value("m.fecha"),
                        "importe": round(float(q.value("m.canpuntos")), 2)
                    })
                return movi_puntos
            else:
                return {"Error": "Petición Incorrecta", "status": -1}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado consulta de puntos: ", e))
            return {"Error": params, "status": -2}
        return False

    def __init__(self, context=None):
        super().__init__(context)

    def getDesc(self):
        return self.ctx.elganso_sync_getDesc()

    def desuscribesm(self, params):
        return self.ctx.elganso_sync_desuscribesm(params)

    def suscribesm(self, params):
        return self.ctx.elganso_sync_suscribesm(params)

    def unificartarjetas(self, params):
        return self.ctx.elganso_sync_unificartarjetas(params)

    def quitarPuntosTarjetaOrigen(self, params):
        return self.ctx.elganso_sync_quitarPuntosTarjetaOrigen(params)

    def acumularPuntosTarjetaDestino(self, params, saldoPuntosOrigen):
        return self.ctx.elganso_sync_acumularPuntosTarjetaDestino(params, saldoPuntosOrigen)

    def generarmovimentopuntosoperacionesmagento(self, params):
        return self.ctx.elganso_sync_generarmovimentopuntosoperacionesmagento(params)

    def acumularPuntosOperacionesMagento(self, params):
        return self.ctx.elganso_sync_acumularPuntosOperacionesMagento(params)

    def eglogtarjetasweb(self, params):
        return self.ctx.elganso_sync_eglogtarjetasweb(params)

    def consultapuntos(self, params):
        return self.ctx.elganso_sync_consultapuntos(params)

    def consultamovimientospuntos(self, params):
        return self.ctx.elganso_sync_consultamovimientospuntos(params)


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
