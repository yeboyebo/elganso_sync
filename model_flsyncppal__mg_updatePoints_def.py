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
    def elganso_sync_updatePointMovements(self):
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
            movs = []
            tarjs = []
            codTienda = qsatype.FactoriaModulos.get("flfactalma").iface.pub_dameAlmacenWeb()

            q = qsatype.FLSqlQuery()
            q.setSelect("tpv_movpuntos.idmovpuntos, tpv_tarjetaspuntos.codtarjetapuntos, tpv_movpuntos.canpuntos, tpv_movpuntos.fecha, tpv_movpuntos.operacion, tpv_movpuntos.idsincro, tpv_movpuntos.codtienda, tpv_movpuntos.devolucion, tpv_movpuntos.borrado, tpv_movpuntos.fechamod, tpv_movpuntos.horamod, tpv_tarjetaspuntos.direccion, tpv_tarjetaspuntos.sexo, tpv_tarjetaspuntos.fechanacimiento, tpv_tarjetaspuntos.sincronizada, tpv_tarjetaspuntos.codbarrastarjeta, tpv_tarjetaspuntos.dtoespecial, tpv_tarjetaspuntos.horaalta, tpv_tarjetaspuntos.horamod, tpv_tarjetaspuntos.activa, tpv_tarjetaspuntos.codpais, tpv_tarjetaspuntos.email, tpv_tarjetaspuntos.saldopuntos, tpv_tarjetaspuntos.cifnif, tpv_tarjetaspuntos.dtopor, tpv_tarjetaspuntos.provincia, tpv_tarjetaspuntos.topemensual, tpv_tarjetaspuntos.deempleado, tpv_tarjetaspuntos.nombre, tpv_tarjetaspuntos.telefono, tpv_tarjetaspuntos.fechaalta, tpv_tarjetaspuntos.codpostal, tpv_tarjetaspuntos.idprovincia, tpv_tarjetaspuntos.fechamod, tpv_tarjetaspuntos.ciudad")
            q.setFrom("tpv_tarjetaspuntos LEFT OUTER JOIN tpv_movpuntos ON tpv_tarjetaspuntos.codtarjetapuntos = tpv_movpuntos.codtarjetapuntos AND NOT sincronizado")
            q.setWhere("(codtienda <> '" + codTienda + "' OR codtienda IS NULL OR (codtienda = '" + codTienda + "' AND idpedidomagento IS NULL)) AND (NOT sincronizada OR NOT sincronizado) ORDER BY tpv_tarjetaspuntos.fechamod ASC, tpv_tarjetaspuntos.codtarjetapuntos, tpv_movpuntos.fecha ASC LIMIT 30")

            if not q.exec_():
                qsatype.debug("Error. La consulta falló.")
                qsatype.debug(q.sql())
                syncppal.iface.log("Error. La consulta falló.", "mgsyncpoints")
                return cdLarge

            if not q.size():
                syncppal.iface.log("Éxito. No hay puntos que sincronizar.", "mgsyncpoints")
                return cdLarge

            actTarj = None
            antTarj = None
            obj = None
            while q.next():
                actTarj = q.value("tpv_tarjetaspuntos.codtarjetapuntos")
                if antTarj != actTarj:
                    if antTarj is not None:
                        body.append(obj)
                    antTarj = actTarj
                    obj = {
                        "movs": [],
                        "codtarjetapuntos": antTarj,
                        "codbarrastarjeta": q.value("tpv_tarjetaspuntos.codbarrastarjeta"),
                        "saldopuntos": q.value("tpv_tarjetaspuntos.saldopuntos"),
                        "nombre": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.nombre")),
                        "email": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.email")),
                        "cifnif": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.cifnif")),
                        "fechanacimiento": str(q.value("tpv_tarjetaspuntos.fechanacimiento")) if q.value("tpv_tarjetaspuntos.fechanacimiento") else None,
                        "direccion": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.direccion")),
                        "ciudad": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.ciudad")),
                        "codpostal": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.codpostal")),
                        "idprovincia": q.value("tpv_tarjetaspuntos.idprovincia"),
                        "provincia": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.provincia")),
                        "codpais": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.codpais")),
                        "telefono": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.telefono")),
                        "sexo": syncppal.iface.replace(q.value("tpv_tarjetaspuntos.sexo")),
                        "activa": q.value("tpv_tarjetaspuntos.activa"),
                        "deempleado": q.value("tpv_tarjetaspuntos.deempleado"),
                        "topemensual": q.value("tpv_tarjetaspuntos.topemensual"),
                        "dtoespecial": q.value("tpv_tarjetaspuntos.dtoespecial"),
                        "dtopor": q.value("tpv_tarjetaspuntos.dtopor"),
                        "fechaalta": str(q.value("tpv_tarjetaspuntos.fechaalta")) if q.value("tpv_tarjetaspuntos.fechaalta") else None,
                        "fechamod": str(q.value("tpv_tarjetaspuntos.fechamod")) if q.value("tpv_tarjetaspuntos.fechamod") else None,
                        "horaalta": str(q.value("tpv_tarjetaspuntos.horaalta"))[:8] if q.value("tpv_tarjetaspuntos.horaalta") else None,
                        "horamod": str(q.value("tpv_tarjetaspuntos.horamod"))[:8] if q.value("tpv_tarjetaspuntos.horamod") else None
                    }

                    if not q.value("tpv_tarjetaspuntos.sincronizada") and antTarj not in tarjs:
                        tarjs.append(antTarj)

                idsincro = q.value("tpv_movpuntos.idsincro")
                if idsincro and idsincro != "":
                    obj["movs"].append({
                        "idsincro": idsincro,
                        "operacion": q.value("tpv_movpuntos.operacion"),
                        "fecha": str(q.value("tpv_movpuntos.fecha")) if q.value("tpv_movpuntos.fecha") else None,
                        "canpuntos": parseFloat(q.value("tpv_movpuntos.canpuntos")),
                        "codtienda": q.value("tpv_movpuntos.codtienda"),
                        "devolucion": q.value("tpv_movpuntos.devolucion"),
                        "borrado": q.value("tpv_movpuntos.borrado"),
                        "fechamod": str(q.value("tpv_movpuntos.fechamod")) if q.value("tpv_movpuntos.fechamod") else None,
                        "horamod": str(q.value("tpv_movpuntos.horamod"))[:8] if q.value("tpv_movpuntos.horamod") else None
                    })

                    idmov = str(q.value("tpv_movpuntos.idmovpuntos"))
                    if idmov not in movs:
                        movs.append(idmov)

            if obj is not None:
                body.append(obj)

            url = None
            if qsatype.FLUtil.isInProd():
                url = 'https://www.elganso.com/syncapi/index.php/pointsupdates'
            else:
                url = 'http://local2.elganso.com/syncapi/index.php/pointsupdates'

            qsatype.debug(ustr("Llamando a ", url, " ", json.dumps(body)))

            response = requests.post(url, data=json.dumps(body), headers=headers)
            stCode = response.status_code
            jsonres = None
            if response and stCode == 202:
                jsonres = response.json()

                if jsonres and "request_id" in jsonres:
                    if len(movs):
                        qsatype.FLSqlQuery().execSql("UPDATE tpv_movpuntos SET sincronizado = true WHERE NOT sincronizado AND idmovpuntos IN (" + ",".join(movs) + ")")
                    if len(tarjs):
                        qsatype.FLSqlQuery().execSql("UPDATE tpv_tarjetaspuntos SET sincronizada = true WHERE NOT sincronizada AND codtarjetapuntos IN ('" + "','".join(tarjs) + "')")
                    syncppal.iface.log("Éxito. Puntos sincronizados correctamente (id: " + str(jsonres["request_id"]) + ")", "mgsyncpoints")
                else:
                    syncppal.iface.log("Error. No se pudieron sincronizar los puntos.", "mgsyncpoints")
                    return cdSmall
            else:
                syncppal.iface.log("Error. No se pudieron sincronizar los puntos. Código: " + str(stCode), "mgsyncpoints")
                return cdSmall

        except Exception as e:
            qsatype.debug(e)
            syncppal.iface.log("Error. No se pudo establecer la conexión con el servidor.", "mgsyncpoints")
            return cdSmall

        return cdSmall

    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)

    def updatePointMovements(self):
        return self.ctx.elganso_sync_updatePointMovements()


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
