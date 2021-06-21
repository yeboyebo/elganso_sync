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

    # Cambio pruebas Xavi 1
    # params = syncppal.iface.get_param_sincro('apipass')
    params = {}

    def elganso_sync_tienebonoregistro(self, params):
        try:
            # Cambio pruebas Xavi 2
            # bdparams = self.params
            # if "auth" not in bdparams:
            #     bdparams = syncppal.iface.get_param_sincro('apipass')
            # if "passwd" in params and params['passwd'] == bdparams['auth']:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
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
            # Cambio pruebas Xavi 2
            # bdparams = self.params
            # if "auth" not in bdparams:
            #     bdparams = syncppal.iface.get_param_sincro('apipass')
            # if "passwd" in params and params['passwd'] == bdparams['auth']:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "codigoVenta" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                q = qsatype.FLSqlQuery()
                q.setTablesList(u"eg_bonos")
                q.setSelect(u"codbono, saldoinicial, saldopendiente, coddivisa, venta, activo")
                q.setFrom(u"eg_bonos")
                q.setWhere(ustr(u"venta = '", params['codigoVenta'], u"'"))
                if not q.exec_():
                    return {"Error": "Bono incorrecto", "status": -1}
                if q.size() > 1:
                    return {"Error": "Bono asociado a mas de una venta", "status": -2}
                if not q.next():
                    return {"Error": "Bono incorrecto", "status": -3}
                activo = q.value("activo")
                if q.value("activo") is False:
                    return {"Error": "El bono no esta activo", "status": 1}
                codbono = q.value("codbono")
                saldopendiente = q.value("saldopendiente")
                saldoinicial = q.value("saldoinicial")
                coddivisa = q.value("coddivisa")
                venta = q.value("venta")
                return {"saldoBono": saldoinicial, "saldoPendiente": saldopendiente, "codigoBono": codbono, "divisa": coddivisa, "venta": venta, "activo": activo}
            else:
                return {"Error": "Petición Incorrecta", "status": 0}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_consultabono(self, params):
        try:
            # Cambio pruebas Xavi 2
            # bdparams = self.params
            # if "auth" not in bdparams:
            #     bdparams = syncppal.iface.get_param_sincro('apipass')
            # if "passwd" in params and params['passwd'] == bdparams['auth']:
            for prop in params:
                print(prop)
                print(params[prop])
                print("-----------------")
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "codigoBono" not in params:
                    return {"Error": "Formato Incorrecto", "status": 0}
                codbono = params['codigoBono']
                
                print(codbono)
                
                if str(codbono)[:2]=="BX":
                    # saldopendiente = qsatype.FLUtil.sqlSelect(u"eg_bonos", u"saldopendiente", ustr(u"codbono = '", codbono, u"'"))
                    q = qsatype.FLSqlQuery()
                    q.setTablesList(u"eg_bonos")
                    q.setSelect(u"codbono, saldoinicial, saldopendiente, coddivisa, venta, email, fechaexpiracion, importeminimo, activo")
                    q.setFrom(u"eg_bonos")
                    q.setWhere(ustr(u"codbono = '", codbono, u"'"))
                    if not q.exec_():
                        return {"Error": "Bono incorrecto", "status": -1}
                    if q.size() > 1:
                        return {"Error": "Bono asociado a mas de una venta", "status": -2}
                    if not q.next():
                        return {"Error": "Bono incorrecto", "status": -3}
                    activo = q.value("activo")
                    if q.value("activo") is False:
                        return {"Error": "El bono no esta activo", "status": 1}
                    saldopendiente = q.value("saldopendiente")
                    saldoinicial = q.value("saldoinicial")
                    coddivisa = q.value("coddivisa")
                    venta = q.value("venta")
                    email = q.value("email") or ""
                    fechaexpiracion = q.value("fechaexpiracion") or ""
                    importeminimo = q.value("importeminimo") or 0
                    if saldopendiente == 0:
                        return {"saldoBono": saldoinicial, "saldoPendiente": saldopendiente, "divisa": coddivisa, "venta": venta, "email": email, "fechaexpiracion": fechaexpiracion, "importeminimo": importeminimo, "activo": activo, "escupon": False}
                    if not saldopendiente:
                        return {"Error": "Bono incorrecto", "status": 1}
                    return {"saldoBono": saldoinicial, "saldoPendiente": saldopendiente, "divisa": coddivisa, "venta": venta, "email": email, "fechaexpiracion": fechaexpiracion, "importeminimo": importeminimo, "activo": activo, "escupon": False}
                if str(codbono)[:2]=="KN":
                    q = qsatype.FLSqlQuery()
                    q.setTablesList(u"eg_cupones")
                    q.setSelect(u"codcupon, esdescuento, artregalo, dtopor, email, fechaexpiracion, activo")
                    q.setFrom(u"eg_cupones")
                    q.setWhere(ustr(u"codcupon = '", codbono, u"'"))
                    if not q.exec_():
                        return {"Error": "Cupón incorrecto", "status": -1}
                    if not q.next():
                        return {"Error": "Cupón incorrecto", "status": -3}
                    activo = q.value("activo")
                    #if q.value("activo") is False:
                        #return {"Error": "El cupón no esta activo", "status": 1}
                    email = q.value("email") or ""
                    fechaexpiracion = q.value("fechaexpiracion") or ""
                    dtoPor = q.value("dtopor") or ""
                    artRegalo = str(q.value("artregalo")) or ""
                    esDescuento = q.value("esdescuento") or False
                    
                    if esDescuento == False:
                        disponible = qsatype.FLUtil.sqlSelect(u"stocks", u"disponible", ustr(u"codalmacen = 'AWEB' AND referencia = '", artRegalo, u"'"))
                    
                        if int(disponible) <= 0:
                            artRegalo = "4070ATEMP210001"
                    
                    return {"artregalo": str(artRegalo) + "FI", "email": email, "fechaexpiracion": fechaexpiracion, "dtopor": dtoPor, "activo": activo, "esdescuento": esDescuento, "escupon": True}
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
            # Cambio pruebas Xavi 2
            # bdparams = self.params
            # if "auth" not in bdparams:
            #     bdparams = syncppal.iface.get_param_sincro('apipass')
            # if "passwd" in params and params['passwd'] == bdparams['auth']:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
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

                activo = True
                if "activo" in params:
                    activo = params["activo"]

                correoenviado = True
                if "correoEnviado" in params:
                    correoenviado = params["correoEnviado"]

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
                if not qsatype.FLUtil.sqlInsert(u"eg_bonos", [u"codbono", u"fecha", u"fechaalta", u"horaalta", u"venta", u"saldoinicial", u"saldoconsumido", u"saldopendiente", u"activo", u"fechaexpiracion", u"coddivisa", u"email", u"observaciones", u"importeminimo", u"correoenviado", u"activo"], [codbono, str(qsatype.Date())[:10], str(qsatype.Date())[:10], horaalta, params['codigoVenta'], importe, 0, importe, True, fechaexpiracion, params['divisa'], params['email'].lower(), observaciones, importeminimo, correoenviado, activo]):
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
            # Cambio pruebas Xavi 2
            # bdparams = self.params
            # if "auth" not in bdparams:
            #     bdparams = syncppal.iface.get_param_sincro('apipass')
            # if "passwd" in params and params['passwd'] == bdparams['auth']:
            if "auth" not in self.params:
                print("auth")
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                print("pass")
                if "codigoBono" not in params:
                    return {"Error": "Falta el código del bono", "status": -8}
                if "codigoVenta" not in params:
                    return {"Error": "Falta el código de la venta", "status": -9}
                
                codbono = params['codigoBono']
                if str(codbono)[:2]=="BX":
                    if "importeVenta" not in params or "divisa" not in params:
                        return {"Error": "Formato Incorrecto", "status": -1}
                        
                    importe = params['importeVenta']
                    divisa = params['divisa']
                    curBono = qsatype.FLSqlCursor(u"eg_bonos")
                    curBono.setModeAccess(curBono.Edit)
                    curBono.refreshBuffer()
                    curBono.select(ustr(u"codbono = '", codbono, u"'"))

                    # Comprobaciones
                    if not curBono.first():
                        qsatype.debug(ustr(u"El bono no esta activo o no se encuentrao: ", codbono))
                        return {"Error": "El bono no se encuentra", "status": -3}
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

                if str(codbono)[:2]=="KN":
                    codCupon = params['codigoBono']
                    qsatype.FLUtil.sqlUpdate(u"eg_cupones", [u"activo", u"observaciones"], [False, u"Cupón usado en venta " + params['codigoVenta']], ustr(u"codcupon = '", codCupon, u"'"))
                    return {"saldoPendiente": 0, "status": 1}
            else:
                return {"Error": "Petición Incorrecta", "status": -7}
        except Exception as e:
            qsatype.debug(params)
            qsatype.debug(ustr(u"Error inesperado generacion de bono: ", e))
            return {"Error": "Petición Incorrecta. EXCEPCION: " + e, "status": 0}
        return False

    def elganso_sync_generaCodCupon(self):
        longitud = 6
        valores = "0123456789abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        codbono = ""
        codbono = codbono.join([choice(valores) for i in range(longitud)])
        codbono = "KN" + codbono
        return codbono

    def elganso_sync_generarcuponespromocion(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')

            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "descuento" not in params or "email" not in params:
                    return {"Error": "Formato Incorrecto", "status": -4}

                q = qsatype.FLSqlQuery()
                q.setTablesList(u"eg_cupones")
                q.setSelect(u"codcupon, esdescuento, artregalo, dtopor, email, fechaexpiracion, activo")
                q.setFrom(u"eg_cupones")
                q.setWhere(ustr(u"email = '", params['email'].lower(), u"'"))
                if not q.exec_():
                    return {"Error": "Cupón incorrecto", "status": -1}
                if q.next():
                    codCupon = q.value("codcupon")
                    activo = q.value("activo")
                    email = q.value("email")
                    fechaexpiracion = q.value("fechaexpiracion")
                    dtoPor = q.value("dtopor")
                    artRegalo = q.value("artregalo")
                    esDescuento = q.value("esdescuento") or False

                    if esDescuento:
                        return {"cupon": codCupon, "status": 1, "tipo": "DESCUENTO", "descuento": dtoPor}

                    return {"cupon": codCupon, "status": 1, "tipo": "ARTICULO_REGALO", "articulo": artRegalo + "FI"}

                valor = qsatype.FLUtil.sqlSelect(u"param_parametros", u"valor", ustr(u"nombre = 'CUPONES'"))

                if not valor:
                    return {"Error": "Hay que configurar los parámetros de los cupones", "status": -1}

                datosParamsCupon = json.loads(valor)

                activo = datosParamsCupon["activo"]

                if activo == "False":
                    return {"Error": "Promoción desactivada", "status": -3}

                diasExpiracion = datosParamsCupon["diasexpiracion"]
                dtoPor = datosParamsCupon["dtopor"]
                articulosDto = datosParamsCupon["articulosdto"]
                aArtregalo = datosParamsCupon["aartregalo"]

                codCupon = self.generaCodCupon()
                fecha = str(qsatype.Date())[:10]
                horaalta = str(qsatype.Date())[-8:]
                fechaexpiracion = str(qsatype.FLUtil.addDays(qsatype.Date(), int(diasExpiracion)))

                while codCupon == qsatype.FLUtil.sqlSelect(u"eg_cupones", u"codcupon", ustr(u"codcupon = '", codCupon, u"'")):
                    codCupon = self.generaCodCupon()

                esDescuento = False
                artRegalo = ""

                if str(params['descuento']) == "True":
                    esDescuento = True
                else:
                    print("hola")
                    ratioDescuentoRegalo = float(qsatype.FLUtil.sqlSelect(u"param_parametros", u"valor", ustr(u"nombre = 'ratioDescuentoRegalo'")))
                    cantRegalos = int(qsatype.FLUtil.sqlSelect(u"eg_cupones", u"count(*)", ustr(u"esdescuento = FALSE")))*ratioDescuentoRegalo
                    cantDto = int(qsatype.FLUtil.sqlSelect(u"eg_cupones", u"count(*)", ustr(u"esdescuento = TRUE")))

                    if cantRegalos > cantDto:
                        esDescuento = True
                    else:
                        aArtregalo = aArtregalo.split(";")
                        i = 0
                        cantTotalRegalos = 0
                        while i < len(aArtregalo):
                            aAR = aArtregalo[i].split(",")
                            cantTotalRegalos += int(aAR[1])
                            i += 1

                        estoyBuscando = True
                        hayRegalos = False
                        iRandom = randrange(0, len(aArtregalo))
                        while estoyBuscando:
                            aAR = aArtregalo[iRandom].split(",")
                            if str(aAR[0]) != "dto":
                                valorCont = int(qsatype.FLUtil.sqlSelect(u"secuencias", u"valor", ustr(u"nombre = '", aAR[0], u"'")))
                                cantTotalRegalos = cantTotalRegalos - valorCont
                                if(valorCont < int(aAR[1])):
                                    estoyBuscando = False
                                    hayRegalos = True
                                    qsatype.FLUtil.sqlUpdate(u"secuencias", u"valor", valorCont + 1, ustr(u"nombre = '", aAR[0], u"'"))
                                    artRegalo = str(aAR[0])
                                else:
                                    if iRandom < len(aArtregalo) - 1:
                                        iRandom += 1
                                    else:
                                        iRandom = 0
                                if cantTotalRegalos <= 0:
                                    estoyBuscando = False
                            else:
                                estoyBuscando = False

                        if not hayRegalos:
                            esDescuento = True

                if not qsatype.FLUtil.sqlInsert(u"eg_cupones", [u"codcupon", u"fecha", u"fechaalta", u"fechaexpiracion", u"horaalta", u"activo", u"email", u"observaciones", u"correoenviado", u"esdescuento", u"dtopor", u"articulosdto", u"artregalo"], [codCupon, fecha, fecha, fechaexpiracion, horaalta, True, params['email'].lower(), "", False, esDescuento, dtoPor, articulosDto, artRegalo]):
                    return {"Error": "Error al guardar el cupón", "status": -2}

                if esDescuento:
                    return {"cupon": codCupon, "status": 1, "tipo": "DESCUENTO", "descuento": dtoPor}
                return {"cupon": codCupon, "status": 1, "tipo": "ARTICULO_REGALO", "articulo": str(artRegalo) + "FI"}

            else:
                return {"Error": "Contraseña incorrecta", "status": 0}
        except Exception as e:
            qsatype.debug(ustr(u"Error inesperado generación del cupón: ", e))
            return {"Error": "Error inesperado generación del cupón", "status": -5}
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

    def generaCodCupon(self):
        return self.ctx.elganso_sync_generaCodCupon()

    def generarcuponespromocion(self, params):
        return self.ctx.elganso_sync_generarcuponespromocion(params)


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
