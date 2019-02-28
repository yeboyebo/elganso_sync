# @class_declaration interna #
import requests
import json
from django.db import transaction
from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from models.flsyncppal import flsyncppal_def as syncppal


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
class elganso_sync(interna):

    @transaction.atomic
    def elganso_sync_updateProductStock(self):
        _i = self.iface

        cdSmall = 10
        cdLarge = 180

        headers = None
        if qsatype.FLUtil.isInProd():
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic c2luY3JvOmJVcWZxQk1ub0g="
            }
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic dGVzdDp0ZXN0"
            }

        try:
            body = []
            ssw = None
            codTienda = qsatype.FactoriaModulos.get("flfactalma").iface.pub_dameAlmacenWeb()
            now = str(qsatype.Date())
            currD = now[:10]
            currT = now[-(8):]

            fecha = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro", "codtienda = '" + codTienda + "' AND esquema = 'STOCK_WEB'")
            hora = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "horasincro", "codtienda = '" + codTienda + "' AND esquema = 'STOCK_WEB'")

            fecha = str(fecha)[:10]
            hora = str(hora)[-(8):]

            if not fecha:
                fecha = "2014-08-01"
            if not hora:
                hora = "00:00:00"

            filtroFechas = "((ssw.fecha > '" + fecha + "' OR (ssw.fecha = '" + fecha + "' AND  ssw.hora >= '" + hora + "')) OR NOT sincronizado OR sincronizado = false)"

            q = qsatype.FLSqlQuery()
            q.setSelect("aa.referencia, aa.talla, aa.barcode, s.disponible, ssw.idssw")
            q.setFrom("articulos a INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON (aa.barcode = s.barcode AND s.codalmacen = 'AWEB') LEFT OUTER JOIN eg_sincrostockweb ssw ON s.idstock = ssw.idstock")
            q.setWhere(filtroFechas + " ORDER BY aa.referencia LIMIT 50")

            if not q.exec_():
                qsatype.debug("Error. La consulta falló.")
                qsatype.debug(q.sql())
                syncppal.iface.log("Error. La consulta falló.", "mgsyncstock")
                return cdLarge

            if not q.size():
                syncppal.iface.log("Éxito. No hay stocks que sincronizar.", "mgsyncstock")
                return cdLarge

            while q.next():
                sku = _i.dameSkuStock(q.value("aa.referencia"), q.value("aa.talla"))
                qty = parseInt(_i.dameStock(q.value("s.disponible")))

                body.append({"sku": sku, "qty": qty, "sincroStock": True})
                if not ssw:
                    ssw = ""
                else:
                    ssw += ","
                ssw += str(q.value("ssw.idssw"))

            url = None
            if qsatype.FLUtil.isInProd():
                url = 'https://www.elganso.com/syncapi/index.php/productupdates'
            else:
                url = 'http://local2.elganso.com/syncapi/index.php/productupdates'

            qsatype.debug(ustr("Llamando a ", url, " ", json.dumps(body)))
            response = requests.post(url, data=json.dumps(body), headers=headers)
            stCode = response.status_code
            jsonres = None
            if response and stCode == 202:
                jsonres = response.json()

                if jsonres and "request_id" in jsonres:
                    qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = true WHERE idssw IN (" + ssw + ")")
                    qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '" + currD + "', horasincro = '" + currT + "' WHERE codtienda = '" + codTienda + "' AND esquema = 'STOCK_WEB'")
                    syncppal.iface.log("Éxito. Stock sincronizado correctamente (id: " + str(jsonres["request_id"]) + ")", "mgsyncstock")
                    return cdSmall
                else:
                    syncppal.iface.log("Error. No se pudo actualizar el stock.", "mgsyncstock")
                    return cdSmall
            else:
                syncppal.iface.log("Error. No se pudo actualizar el stock. Código: " + str(stCode), "mgsyncstock")
                return cdSmall

        except Exception as e:
            qsatype.debug(e)
            syncppal.iface.log("Error. No se pudo establecer la conexión con el servidor.", "mgsyncstock")
            return cdSmall

        return cdSmall

    def elganso_sync_dameSkuStock(self, referencia, talla):
        if talla == "TU":
            talla = ""
        else:
            talla = "-" + talla

        return referencia + talla

    def elganso_sync_dameStock(self, disponible):
        if not disponible or isNaN(disponible) or disponible < 0:
            return 0
        return disponible

    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)

    def updateProductStock(self):
        return self.ctx.elganso_sync_updateProductStock()

    def dameSkuStock(self, referencia, talla):
        return self.ctx.elganso_sync_dameSkuStock(referencia, talla)

    def dameStock(self, disponible):
        return self.ctx.elganso_sync_dameStock(disponible)


# @class_declaration head #
class head(elganso_sync):

    def __init__(self, context=None):
        super(head, self).__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super(ifaceCtx, self).__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)


form = FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
iface = form.iface
