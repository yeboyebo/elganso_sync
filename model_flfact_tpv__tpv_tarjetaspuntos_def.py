# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
from YBLEGACY.constantes import *


class elganso_sync(interna):

    def elganso_sync_getDesc(self):
        return None

    def elganso_sync_desuscribesm(self, params):
        try:
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
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
            if "passwd" in params and params['passwd'] == "bUqfqBMnoH":
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

    def __init__(self, context=None):
        super().__init__(context)

    def getDesc(self):
        return self.ctx.elganso_sync_getDesc()

    def desuscribesm(self, params):
        return self.ctx.elganso_sync_desuscribesm(params)

    def suscribesm(self, params):
        return self.ctx.elganso_sync_suscribesm(params)


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
