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
    def elganso_sync_updateProductPrices(self):
        _i = self.iface

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
            codTienda = "AWEB"
            now = str(qsatype.Date())
            currD = now[:10]
            currT = now[-(8):]

            fecha = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro", "codtienda = '" + codTienda + "' AND esquema = 'PRICES_WEB'")
            hora = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "horasincro", "codtienda = '" + codTienda + "' AND esquema = 'PRICES_WEB'")

            if not fecha or fecha is None:
                fecha = "2014-08-01"
            else:
                fecha = str(fecha)[:10]

            if not hora or hora is None:
                hora = "00:00:00"
            else:
                hora = str(hora)[-(8):]

            filtroFechas = "(a.fechaalta > '" + fecha + "' OR (a.fechaalta = '" + fecha + "' AND  a.horaalta >= '" + hora + "'))"
            filtroFechas += " OR (a.fechamod > '" + fecha + "' OR (a.fechamod = '" + fecha + "' AND  a.horamod >= '" + hora + "'))"
            where = filtroFechas + " ORDER BY a.referencia"

            q = qsatype.FLSqlQuery()
            q.setSelect("a.referencia,a.pvp, a.codtarifa, st.codwebsite, st.codstoreview")
            q.setFrom("mg_websites w inner join mg_storeviews st on w.codwebsite = st.codwebsite inner join articulostarifas a on a.codtarifa = st.codtarifa")
            q.setWhere(where)

            if not q.exec_():
                qsatype.debug("Error. La consulta falló.")
                qsatype.debug(q.sql())
                syncppal.iface.log("Error. La consulta falló.", "mgsyncprices")
                return False

            while q.next():
                sku = q.value("a.referencia")
                price = parseFloat(q.value("a.pvp"))
                store_id = q.value("st.codstoreview")
                website = q.value("st.codwebsite")

                body.append({"sku": sku, "price": price, "sincroPrecios": True, "auto": True, "store_id": store_id, "website": website})

            if not len(body):
                syncppal.iface.log("Éxito. No hay precios que sincronizar.", "mgsyncprices")
                return True

            url = None
            if qsatype.FLUtil.isInProd():
                url = 'https://www.elganso.com/syncapi/index.php/productupdates'
            else:
                url = 'http://local2.elganso.com/syncapi/index.php/productupdates'

            nBody = []
            for idx in range(len(body)):
                if len(nBody) < 10 or idx == len(body) - 1:
                    nBody.append(body[idx])

                if len(nBody) == 10 or idx == len(body) - 1:
                    qsatype.debug(ustr("Llamando a ", url, " ", json.dumps(nBody)))
                    response = requests.post(url, data=json.dumps(nBody), headers=headers)
                    stCode = response.status_code
                    jsonres = None
                    if response and stCode == 202:
                        jsonres = response.json()
                    else:
                        syncppal.iface.log("Error. No se pudo actualizar los precios.", "mgsyncprices")
                        return False

                    if jsonres and "request_id" in jsonres:
                        syncppal.iface.log("Éxito. Precios sincronizados correctamente (id: " + str(jsonres["request_id"]) + ")", "mgsyncprices")
                        nBody = []
                    else:
                        syncppal.iface.log("Error. No se pudo actualizar los precios.", "mgsyncprices")
                        return False

            if fecha != "2014-08-01":
                qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '" + currD + "', horasincro = '" + currT + "' WHERE codtienda = '" + codTienda + "' AND esquema = 'PRICES_WEB'")
            else:
                qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('" + codTienda + "', 'PRICES_WEB', '" + currD + "', '" + currT + "')")

            return True

            # qsatype.debug(ustr("Llamando a ", url, " ", json.dumps(body)))
            # response = requests.post(url, data=json.dumps(body), headers=headers)
            # stCode = response.status_code
            # jsonres = None
            # if response and stCode == 202:
            #     jsonres = response.json()

            #     if jsonres and "request_id" in jsonres:
            #         if fecha != "2014-08-01":
            #             qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '" + currD + "', horasincro = '" + currT + "' WHERE codtienda = '" + codTienda + "' AND esquema = 'PRICES_WEB'")
            #         else:
            #             qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('" + codTienda + "', 'PRICES_WEB', '" + currD + "', '" + currT + "')")

            #         syncppal.iface.log("Éxito. Precios sincronizados correctamente (id: " + str(jsonres["request_id"]) + ")", "mgsyncprices")
            #         return cdSmall
            #     else:
            #         syncppal.iface.log("Error. No se pudo actualizar los precios.", "mgsyncprices")
            #         return cdSmall
            # else:
            #     syncppal.iface.log("Error. No se pudo actualizar los precios. Código: " + str(stCode), "mgsyncprices")
            #     return cdSmall

        except Exception as e:
            qsatype.debug(e)
            syncppal.iface.log("Error. No se pudo establecer la conexión con el servidor.", "mgsyncprices")
            return False

        return True

    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)

    def updateProductPrices(self):
        return self.ctx.elganso_sync_updateProductPrices()


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
