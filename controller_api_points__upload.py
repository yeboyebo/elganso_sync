from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.sync.base.aqsync_upload import AQSyncUpload

from models.flsyncppal import flsyncppal_def as syncppal


class EgPointsUpload(AQSyncUpload):

    _cards = None
    _movements = None
    _q = None

    def __init__(self, params=None):
        super().__init__("mgsyncpoints", params)

        self.set_sync_params({
            "auth": "Basic c2luY3JvOmJVcWZxQk1ub0g=",
            "test_auth": "Basic dGVzdDp0ZXN0",
            "url": "https://www.elganso.com/syncapi/index.php/pointsupdates",
            "test_url": "http://local2.elganso.com/syncapi/index.php/pointsupdates"
        })

        self._cards = []
        self._movements = []

    def get_data(self):
        self._q = qsatype.FLSqlQuery()
        self._q.setSelect("tpv_movpuntos.idmovpuntos, tpv_tarjetaspuntos.codtarjetapuntos, tpv_movpuntos.canpuntos, tpv_movpuntos.fecha, tpv_movpuntos.operacion, tpv_movpuntos.idsincro, tpv_movpuntos.codtienda, tpv_movpuntos.devolucion, tpv_movpuntos.borrado, tpv_movpuntos.fechamod, tpv_movpuntos.horamod, tpv_tarjetaspuntos.direccion, tpv_tarjetaspuntos.sexo, tpv_tarjetaspuntos.fechanacimiento, tpv_tarjetaspuntos.sincronizada, tpv_tarjetaspuntos.codbarrastarjeta, tpv_tarjetaspuntos.dtoespecial, tpv_tarjetaspuntos.horaalta, tpv_tarjetaspuntos.horamod, tpv_tarjetaspuntos.activa, tpv_tarjetaspuntos.codpais, tpv_tarjetaspuntos.email, tpv_tarjetaspuntos.saldopuntos, tpv_tarjetaspuntos.cifnif, tpv_tarjetaspuntos.dtopor, tpv_tarjetaspuntos.provincia, tpv_tarjetaspuntos.topemensual, tpv_tarjetaspuntos.deempleado, tpv_tarjetaspuntos.nombre, tpv_tarjetaspuntos.telefono, tpv_tarjetaspuntos.fechaalta, tpv_tarjetaspuntos.codpostal, tpv_tarjetaspuntos.idprovincia, tpv_tarjetaspuntos.fechamod, tpv_tarjetaspuntos.ciudad")
        self._q.setFrom("tpv_tarjetaspuntos LEFT OUTER JOIN tpv_movpuntos ON tpv_tarjetaspuntos.codtarjetapuntos = tpv_movpuntos.codtarjetapuntos AND NOT sincronizado")
        self._q.setWhere("(codtienda <> 'AWEB' OR codtienda IS NULL OR (codtienda = 'AWEB' AND idpedidomagento IS NULL)) AND (NOT sincronizada OR NOT sincronizado) ORDER BY tpv_tarjetaspuntos.fechamod ASC, tpv_tarjetaspuntos.codtarjetapuntos, tpv_movpuntos.fecha ASC LIMIT 30")

        self._q.exec_()

        body = []
        if not self._q.size():
            return body

        current_card = None
        former_card = None
        sync_object = None
        while self._q.next():
            current_card = self.get_value("tpv_tarjetaspuntos.codtarjetapuntos")

            if former_card != current_card:
                if former_card is not None:
                    body.append(sync_object)

                former_card = current_card
                sync_object = {
                    "movs": [],
                    "codtarjetapuntos": former_card,
                    "codbarrastarjeta": self.get_value("tpv_tarjetaspuntos.codbarrastarjeta"),
                    "saldopuntos": self.get_value("tpv_tarjetaspuntos.saldopuntos"),
                    "nombre": self.get_string_value("tpv_tarjetaspuntos.nombre"),
                    "email": self.get_string_value("tpv_tarjetaspuntos.email"),
                    "cifnif": self.get_string_value("tpv_tarjetaspuntos.cifnif"),
                    "fechanacimiento": self.get_string_value("tpv_tarjetaspuntos.fechanacimiento"),
                    "direccion": self.get_string_value("tpv_tarjetaspuntos.direccion"),
                    "ciudad": self.get_string_value("tpv_tarjetaspuntos.ciudad"),
                    "codpostal": self.get_string_value("tpv_tarjetaspuntos.codpostal"),
                    "idprovincia": self.get_value("tpv_tarjetaspuntos.idprovincia"),
                    "provincia": self.get_string_value("tpv_tarjetaspuntos.provincia"),
                    "codpais": self.get_string_value("tpv_tarjetaspuntos.codpais"),
                    "telefono": self.get_string_value("tpv_tarjetaspuntos.telefono"),
                    "sexo": self.get_string_value("tpv_tarjetaspuntos.sexo"),
                    "activa": self.get_value("tpv_tarjetaspuntos.activa"),
                    "deempleado": self.get_value("tpv_tarjetaspuntos.deempleado"),
                    "topemensual": self.get_value("tpv_tarjetaspuntos.topemensual"),
                    "dtoespecial": self.get_value("tpv_tarjetaspuntos.dtoespecial"),
                    "dtopor": self.get_value("tpv_tarjetaspuntos.dtopor"),
                    "fechaalta": self.get_string_value("tpv_tarjetaspuntos.fechaalta"),
                    "fechamod": self.get_string_value("tpv_tarjetaspuntos.fechamod"),
                    "horaalta": self.get_string_value("tpv_tarjetaspuntos.horaalta")[:8],
                    "horamod": self.get_string_value("tpv_tarjetaspuntos.horamod")[:8]
                }

                if not self.get_value("tpv_tarjetaspuntos.sincronizada") and former_card not in self._cards:
                    self._cards.append(former_card)

            idsincro = self.get_value("tpv_movpuntos.idsincro")
            if idsincro and idsincro != "":
                sync_object["movs"].append({
                    "idsincro": idsincro,
                    "operacion": self.get_value("tpv_movpuntos.operacion"),
                    "fecha": self.get_string_value("tpv_movpuntos.fecha"),
                    "canpuntos": parseFloat(self.get_value("tpv_movpuntos.canpuntos")),
                    "codtienda": self.get_value("tpv_movpuntos.codtienda"),
                    "devolucion": self.get_value("tpv_movpuntos.devolucion"),
                    "borrado": self.get_value("tpv_movpuntos.borrado"),
                    "fechamod": self.get_string_value("tpv_movpuntos.fechamod"),
                    "horamod": self.get_string_value("tpv_movpuntos.horamod")[:8]
                })

                idmov = self.get_string_value("tpv_movpuntos.idmovpuntos")
                if idmov not in self._movements:
                    self._movements.append(idmov)

        if sync_object is not None:
            body.append(sync_object)

        return body

    def get_value(self, key):
        return self._q.value(key)

    def get_string_value(self, key):
        value = self.get_value(key)
        if not value:
            return None

        return syncppal.iface.replace(str(value))

    def after_sync(self, response_data=None):
        if response_data and "request_id" in response_data:
            if len(self._movements):
                qsatype.FLSqlQuery().execSql("UPDATE tpv_movpuntos SET sincronizado = true WHERE NOT sincronizado AND idmovpuntos IN ({})".format(",".join(self._movements)))
            if len(self._cards):
                qsatype.FLSqlQuery().execSql("UPDATE tpv_tarjetaspuntos SET sincronizada = true WHERE NOT sincronizada AND codtarjetapuntos IN ('{}')".format("','".join(self._cards)))
            self.log("Éxito", "Puntos sincronizados correctamente (id: {})".format(response_data["request_id"]))

        return self.small_sleep
