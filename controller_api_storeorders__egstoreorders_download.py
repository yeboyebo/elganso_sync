from YBLEGACY import qsatype

from controllers.api.sync.base.controllers.aqsync_download import AQSyncDownload
from controllers.api.sync.storeorders.serializers.egstoreorder_serializer import EgStoreOrderSerializer

from models.flfactalma.objects.egstoreorder_raw import EgStoreOrder


class EgStoreOrdersDownload(AQSyncDownload):

    def __init__(self, process_name, driver, params=None):
        super().__init__("egsyncvt{}".format(params["codtienda"].lower()), driver, params)

        self.origin_field = "codigo"
        self.codtienda = params["codtienda"]

        self.set_sync_params({
            "name": params["codtienda"].lower()
        })

    def get_data(self):
        data = []

        where = "codtienda = '{}' AND NOT sincronizada AND fecha >= '2018-07-01' AND tipodoc <> 'PRESUPUESTO' AND estado <> 'Abierta' AND codigo NOT LIKE '#%' ORDER BY fecha, hora LIMIT 3".format(self.codtienda)

        headers = self.execute("SELECT * FROM tpv_comandas WHERE {}".format(where))
        for header in headers:
            lines = self.execute("SELECT * FROM tpv_lineas WHERE idtpv_comanda = {}".format(header["idtpv_comanda"]))
            payments = self.execute("SELECT * FROM tpv_pagoscomanda WHERE idtpv_comanda = {}".format(header["idtpv_comanda"]))
            reasons = self.execute("SELECT * FROM eg_motivosdevolucion WHERE codcomandadevol = '{}'".format(header["codigo"]))

            data.append({"header": header, "lines": lines, "payments": payments, "reasons": reasons})

        return data

    def process_data(self, data):
        store_order_data = EgStoreOrderSerializer().serialize(data)

        store_order = EgStoreOrder(store_order_data)
        store_order.save()

    def after_sync(self):
        success_records = []
        error_records = [order["header"]["codigo"] for order in self.error_data]
        after_sync_error_records = []

        for order in self.success_data:
            try:
                code = order["header"]["codigo"]
                self.execute("UPDATE tpv_comandas SET sincronizada = true WHERE codigo = '{}'".format(code))
                self.driver.commit()
                success_records.append(code)
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(code)

        for order in self.error_data:
            try:
                code = order["header"]["codigo"]
                self.execute("UPDATE tpv_comandas SET sincronizada = true WHERE codigo = '{}'".format(code))
                self.driver.commit()
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(code)

        if success_records:
            success_records = ", ".join(success_records)
            self.log("Éxito", "Las siguientes ventas se sincronizaron correctamente: [{}]".format(success_records))

        if error_records:
            error_records = ", ".join(error_records)
            self.log("Error", "Las siguientes ventas no se han sincronizado correctamente: [{}]".format(error_records))

        if after_sync_error_records:
            after_sync_error_records = ", ".join(after_sync_error_records)
            self.log("Error", "Las siguientes ventas no se han marcado como sincronizadas: [{}]".format(after_sync_error_records))

        id_sincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "codtienda = '{}' AND esquema = 'SINCRO_OBJETO'".format(self.codtienda))

        if id_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = '{}' AND esquema = 'SINCRO_OBJETO'".format(self.start_date, self.start_time, self.codtienda))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', 'SINCRO_OBJETO', '{}', '{}')".format(self.start_date, self.start_time, self.codtienda))

        return self.small_sleep
