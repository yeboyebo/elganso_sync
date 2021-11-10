from YBLEGACY import qsatype
import json
from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.magento2.products_upload.serializers.mg2_products_serializer import Mg2ProductsSerializer

from models.flfact_tpv.objects.mg2_products_raw import Mg2Products


class Mg2ProductsProcess(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mg2productsprocess", driver, params)
        self.origin_field = "sku"
        self.idlogs = ""
        self.small_sleep = 10
        self.large_sleep = 60
        self.no_sync_sleep = 120

    def get_data(self):
        self.small_sleep = 10
        q = qsatype.FLSqlQuery()
        q.setSelect("idlog, cuerpolog")
        q.setFrom("eg_logarticulosweb")
        q.setWhere("website = 'magento2' AND not procesado AND (estadoprocesado IS NULL OR estadoprocesado = '') AND sku IS NOT NULL ORDER BY fechaalta, horaalta LIMIT 10")

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

            cuerpolog = cuerpolog.replace('"', "-")
            cuerpolog = cuerpolog.replace("None", "\"None\"")
            cuerpolog = cuerpolog.replace('"', "\'")
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
        product_data = Mg2ProductsSerializer().serialize(data)

        if not product_data:
            return

    def after_sync(self):
        success_records = []
        error_records = [product["sku"] for product in self.error_data]
        after_sync_error_records = []

        for product in self.success_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logarticulosweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'OK' WHERE idlog IN ({}) AND sku = '{}'".format(self.idlogs, product["sku"]))
                success_records.append(product["sku"])
            except Exception as e:
                self.after_sync_error(product, e)
                after_sync_error_records.append(product["sku"])

        for product in self.error_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logarticulosweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'ERROR' WHERE idlog IN ({}) AND sku = '{}'".format(self.idlogs, product["sku"]))
            except Exception as e:
                self.after_sync_error(product, e)
                after_sync_error_records.append(product["sku"])

        if success_records:
            self.log("Exito", "Los siguientes articulos se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Los siguientes articulos no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Los siguientes articulos no se han marcado como sincronizados: {}".format(after_sync_error_records))

        return self.small_sleep

    def fetch_query(self, q):
        field_list = [field.strip() for field in q.select().split(",")]

        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)

        return rows
