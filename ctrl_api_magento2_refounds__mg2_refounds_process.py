from YBLEGACY import qsatype
import json
from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.magento2.refounds.serializers.mg2_refound_serializer import Mg2RefoundsSerializer

from models.flfact_tpv.objects.mg2_refound_raw import MgRefound

class Mg2RefoundsProcess(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mg2refoundsprocess", driver, params)
        self.origin_field = "rma_id"
        self.idlogs = ""

    def get_data(self):
        self.small_sleep = 10
        q = qsatype.FLSqlQuery()
        q.setSelect("idlog, cuerpolog")
        q.setFrom("eg_logdevolucionesweb")
        q.setWhere("website = 'magento2' AND not procesado AND (estadoprocesado IS NULL OR estadoprocesado = '') AND rma_id IS NOT NULL ORDER BY fechaalta, horaalta LIMIT 10")

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
            cuerpolog = cuerpolog.replace("None", "\"None\"")
            cuerpolog = cuerpolog.replace("{'", "{\"")
            cuerpolog = cuerpolog.replace("'}", "\"}")
            cuerpolog = cuerpolog.replace("':", "\":")
            cuerpolog = cuerpolog.replace(": '", ": \"")
            cuerpolog = cuerpolog.replace(", '", ", \"")
            cuerpolog = cuerpolog.replace("',", "\",")
            cuerpolog = cuerpolog.replace("['", "[\"")
            cuerpolog = cuerpolog.replace("']", "\"]")
            cuerpolog = cuerpolog.replace("'", " ")
            cuerpolog = cuerpolog.replace("False", "\"False\"")
            cuerpolog = cuerpolog.replace("True", "\"True\"")

            datajson = json.loads(str(cuerpolog))
            aData.append(datajson)

        return aData

    def process_data(self, data):
        refound_data = Mg2RefoundsSerializer().serialize(data)
        if not refound_data:
            return

        refound = MgRefound(refound_data)
        refound.save()

    def after_sync(self):
        success_records = []
        error_records = [refound["rma_id"] for refound in self.error_data]
        after_sync_error_records = []

        for refound in self.success_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logdevolucionesweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'OK' WHERE idlog IN ({}) AND rma_id = '{}'".format(self.idlogs, refound["rma_id"]))
                success_records.append(refound["rma_id"])
            except Exception as e:
                self.after_sync_error(refound, e)
                after_sync_error_records.append(refound["rma_id"])

        for refound in self.error_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logdevolucionesweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'ERROR' WHERE idlog IN ({}) AND rma_id = '{}'".format(self.idlogs, refound["rma_id"]))
            except Exception as e:
                self.after_sync_error(refound, e)
                after_sync_error_records.append(refound["rma_id"])

        if success_records:
            self.log("Exito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Las siguientes devoluciones no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Las siguientes devoluciones no se han marcado como sincronizados: {}".format(after_sync_error_records))

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
