from YBLEGACY import qsatype
import json

from controllers.base.magento2.orders.controllers.orders_download import OrdersDownload


class OrdersDownload(OrdersDownload):

    def __init__(self, params=None):
        super().__init__("mgb2borders", params)

        orders_params = self.get_param_sincro('b2bOrdersDownload')
        self.orders_url = orders_params['url']
        self.orders_test_url = orders_params['test_url']

        self.set_sync_params(self.get_param_sincro('b2b'))
        self.origin_field = "increment_id"
        self.idlogs = ""
        self.small_sleep = 10
        self.large_sleep = 60
        self.no_sync_sleep = 120
        self.jPedidos = {}

    def get_data(self):
        self.small_sleep = 10
        q = qsatype.FLSqlQuery()
        q.setSelect("idlog, cuerpolog")
        q.setFrom("eg_logpedidosb2b")
        q.setWhere("not procesado AND (estadoprocesado IS NULL OR estadoprocesado = '') AND increment_id IS NOT NULL ORDER BY fechaalta, horaalta LIMIT 10")

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
            cuerpolog = cuerpolog.replace("\\xa0", " ")
            cuerpolog = cuerpolog.replace("\\xad", "")
            cuerpolog = cuerpolog.replace("\\x81", "")
            cuerpolog = cuerpolog.replace("\\n", " ")
            cuerpolog = cuerpolog.replace("\n", " ")

            # print(str(cuerpolog))
            # cuerpolog = cuerpolog.replace("False", "\"False\"")
            # cuerpolog = cuerpolog.replace("True", "\"True\"")

            datajson = json.loads(str(cuerpolog))    
            aData.append(datajson)

        return aData

    def after_sync(self):
        success_records = []
        error_records = []

        for order in self.error_data:
            error_records.append(order["increment_id"])

        after_sync_error_records = []

        for order in self.success_data:
            try:
                codigo_pedido = qsatype.FLUtil.sqlSelect("pedidoscli", "codigo", "observaciones LIKE '%{}%'".format(order["increment_id"]))
                qsatype.FLSqlQuery().execSql("UPDATE eg_logpedidosb2b SET procesado = true, fechaprocesado = CURRENT_DATE, horaprocesado = CURRENT_TIME, estadoprocesado = 'OK', codpedido = '{}' WHERE increment_id = '{}'".format(codigo_pedido, order["increment_id"]))
                success_records.append(order["increment_id"])
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(order["increment_id"])

        if success_records:
            self.log("Exito", "Los siguientes pedidos B2B se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Los siguientes pedidos B2B no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Los siguientes pedidos  B2B no se han marcado como sincronizados: {}".format(after_sync_error_records))

        return self.small_sleep

    def fetch_query(self, q):
        field_list = [field.strip() for field in q.select().split(",")]

        rows = []
        while q.next():
            row = {field: q.value(field) for (field) in field_list}
            rows.append(row)

        return rows