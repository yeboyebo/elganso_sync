from YBLEGACY import qsatype
import json
from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.magento2.points.serializers.mg2_points_serializer import Mg2PointsSerializer

from models.flfact_tpv.objects.mg2_points_raw import Mg2Points

class Mg2PointsProcess(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mg2pointsprocess", driver, params)
        self.origin_field = "email"
        self.idlogs = ""
        self.small_sleep = 10
        self.large_sleep = 60
        self.no_sync_sleep = 180

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("idlog,cuerpolog")
        q.setFrom("eg_logtarjetasweb left outer join tpv_tarjetaspuntos on eg_logtarjetasweb.email = tpv_tarjetaspuntos.email")
        q.setWhere("eg_logtarjetasweb.website = 'magento2' AND not eg_logtarjetasweb.procesado AND (eg_logtarjetasweb.estadoprocesado IS NULL OR eg_logtarjetasweb.estadoprocesado = '') and tpv_tarjetaspuntos.codtarjetapuntos is null ORDER BY eg_logtarjetasweb.fechaalta, eg_logtarjetasweb.horaalta LIMIT 1")

        q.exec_()

        if not q.size():
            self.small_sleep = 60
            return []

        body = self.fetch_query(q)
        aData = []

        for row in body:

            if self.idlogs == "":
                self.idlogs = str(row['idlog'])
            else:
                self.idlogs += "," + str(row['idlog'])

            cuerpolog = row['cuerpolog']
            # print(str(cuerpolog))
            cuerpolog = cuerpolog.replace("None", "\"None\"")
            cuerpolog = cuerpolog.replace("{'", "{\"")
            cuerpolog = cuerpolog.replace("'}", "\"}")
            cuerpolog = cuerpolog.replace("':", "\":")
            cuerpolog = cuerpolog.replace(": '", ": \"")
            cuerpolog = cuerpolog.replace(", '", ", \"")
            cuerpolog = cuerpolog.replace("',", "\",")
            cuerpolog = cuerpolog.replace("['", "[\"")
            cuerpolog = cuerpolog.replace("']", "\"]")
            cuerpolog = cuerpolog.replace("'", ",")
            cuerpolog = cuerpolog.replace("False", "\"False\"")
            cuerpolog = cuerpolog.replace("True", "\"True\"")
            datajson = json.loads(str(cuerpolog))
            
            # print(str(cuerpolog))

            aData.append(datajson)

        return aData

    def process_data(self, data):

        points_data = Mg2PointsSerializer().serialize(data)

        if not points_data:
            return

        points = Mg2Points(points_data)

        points.save()

    def after_sync(self):
        success_records = []
        error_records = [tarjeta["email"] for tarjeta in self.error_data]
        after_sync_error_records = []

        for tarjeta in self.success_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logtarjetasweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'OK' WHERE idlog IN ({}) AND email = '{}'".format(self.idlogs, tarjeta["email"]))
                success_records.append(tarjeta["email"])
            except Exception as e:
                self.after_sync_error(tarjeta, e)
                after_sync_error_records.append(tarjeta["email"])

        for tarjeta in self.error_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logtarjetasweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'ERROR' WHERE idlog IN ({}) AND email = '{}'".format(self.idlogs, tarjeta["email"]))
            except Exception as e:
                self.after_sync_error(tarjeta, e)
                after_sync_error_records.append(tarjeta["email"])

        if success_records:
            self.log("Exito", "Las siguientes tarjetas se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Las siguientes tarjetas no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Las siguientes tarjetas no se han marcado como sincronizados: {}".format(after_sync_error_records))

        d = qsatype.Date()
        if not qsatype.FactoriaModulos.get("formtpv_tiendas").iface.marcaFechaSincroTienda("AWEB", "VENTAS_TPV", d):
            return False

        return self.small_sleep

    def fetch_query(self, q):

        field_list = [field.strip() for field in q.select().split(",")]
        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)

        return rows
