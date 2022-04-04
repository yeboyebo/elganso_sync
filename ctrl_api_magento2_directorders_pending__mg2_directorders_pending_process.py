from YBLEGACY import qsatype
import json
from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload
from controllers.api.magento2.directorders_pending.serializers.mg2_directorders_pending_serializer import Mg2DirectOrdersPendingSerializer

class Mg2DirectOrdersPendingProcess(InventoryUpload):

    def __init__(self, driver, params=None):
        super().__init__("mg2directorderspendingprocess", params)
        self.origin_field = "codcomanda"
        self.small_sleep = 10
        self.large_sleep = 60
        self.no_sync_sleep = 120

    def get_data(self):
        self.small_sleep = 10
        q = qsatype.FLSqlQuery()
        q.setSelect("codcomanda, codpedido")
        q.setFrom("eg_directorderspendientes")
        q.setWhere("estado = 'PTE' ORDER BY fechaalta, codcomanda LIMIT 10")

        q.exec_()

        if not q.size():
            self.small_sleep = 60
            return []

        body = self.fetch_query(q)
        aData = []
        for row in body:
            print("CODPEDIDO: ", row["codpedido"])
            qPedidos = qsatype.FLSqlQuery()
            qPedidos.setSelect("lp.referencia || '-' || lp.talla, lp.cantidad, lp.barcode")
            qPedidos.setFrom("pedidoscli p INNER JOIN lineaspedidoscli lp ON p.idpedido = lp.idpedido")
            qPedidos.setWhere("p.codigo = '" + row["codpedido"] + "'")

            qPedidos.exec_()
            bodyPedidos = self.fetch_query(qPedidos)
            for linea in bodyPedidos:
                print("barcode:", linea["lp.barcode"])
                idtpv_linea = qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "idtpv_linea", "barcode = '{}' AND idtpv_comanda IN (SELECT idtpv_comanda FROM tpv_comandas WHERE codigo = '{}')".format(linea["lp.barcode"], row["codcomanda"]))
                print("IDLINEA: ", idtpv_linea)
                if idtpv_linea:
                    aData.append({"idtpv_linea": linea["lc.idtpv_linea"], "sku": linea["lp.referencia || '-' || lp.talla"],"barcode": linea["lp.barcode"], "cantidad": int(linea["lp.cantidad"])})

            if aData != []:
                datos = {"codcomanda": row["codcomanda"], "codpedido": row["codpedido"], "items" : aData}
                result = self.get_directorders_pending_serializer().serialize(datos)

        return True

    def send_data(self, data):
        return True

    def get_directorders_pending_serializer(self):
        return Mg2DirectOrdersPendingSerializer()

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
