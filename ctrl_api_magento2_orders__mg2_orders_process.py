from YBLEGACY import qsatype
import json
from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.magento2.orders.serializers.mg2_orders_serializer import Mg2OrdersSerializer

from models.flfact_tpv.objects.mg2_order_raw import Mg2Order


class Mg2OrdersProcess(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mg2ordersprocess", driver, params)
        self.origin_field = "increment_id"
        self.idlogs = ""
        self.small_sleep = 10
        self.large_sleep = 60
        self.no_sync_sleep = 120

    def get_data(self):
        self.small_sleep = 10
        q = qsatype.FLSqlQuery()
        q.setSelect("idlog, cuerpolog")
        q.setFrom("eg_logpedidosweb left outer join tpv_comandas on eg_logpedidosweb.codcomanda = tpv_comandas.codigo")
        q.setWhere("website = 'magento2' AND not procesado AND (estadoprocesado IS NULL OR estadoprocesado = '') AND increment_id IS NOT NULL AND codigo IS NULL ORDER BY fechaalta, horaalta LIMIT 10")

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
            cuerpolog = cuerpolog.replace('"', "\'")
            cuerpolog = cuerpolog.replace("{'", "{\"")
            cuerpolog = cuerpolog.replace("'}", "\"}")
            cuerpolog = cuerpolog.replace("':", "\":")
            cuerpolog = cuerpolog.replace(": '", ": \"")
            cuerpolog = cuerpolog.replace(", '", ", \"")
            cuerpolog = cuerpolog.replace("',", "\",")
            cuerpolog = cuerpolog.replace("['", "[\"")
            cuerpolog = cuerpolog.replace("']", "\"]")
            cuerpolog = cuerpolog.replace("'", ",")
            
            # print(str(cuerpolog))
            datajson = json.loads(str(cuerpolog))
            aData.append(datajson)

        return aData

    def process_data(self, data):
        order_data = Mg2OrdersSerializer().serialize(data)

        if not order_data:
            return

        order = Mg2Order(order_data)
        order.save()

    def after_sync(self):
        success_records = []
        error_records = [order["increment_id"] for order in self.error_data]
        after_sync_error_records = []

        for order in self.success_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logpedidosweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'OK' WHERE idlog IN ({}) AND increment_id = '{}'".format(self.idlogs, order["increment_id"]))
                success_records.append(order["increment_id"])
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(order["increment_id"])

        for order in self.error_data:
            try:
                qsatype.FLSqlQuery().execSql("UPDATE eg_logpedidosweb SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'ERROR' WHERE idlog IN ({}) AND increment_id = '{}'".format(self.idlogs, order["increment_id"]))
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(order["increment_id"])

        if success_records:
            self.log("Exito", "Los siguientes pedidos se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Los siguientes pedidos no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Los siguientes pedidos no se han marcado como sincronizados: {}".format(after_sync_error_records))

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
