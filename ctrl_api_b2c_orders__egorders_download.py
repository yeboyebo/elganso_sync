from YBLEGACY import qsatype

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.b2c.orders.serializers.egorder_serializer import EgOrderSerializer

from models.flfact_tpv.objects.egorder_raw import EgOrder

class EgOrdersDownload(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mgsyncorders", driver, params)

        self.set_sync_params(self.get_param_sincro('b2c'))
        self.set_sync_params(self.get_param_sincro('b2cOrdersDownload'))

        self.origin_field = "increment_id"

    def process_data(self, data):
        order_data = EgOrderSerializer().serialize(data)
        if not order_data:
            return

        order = EgOrder(order_data)
        order.save()

    def after_sync(self):
        self.set_sync_params(self.get_param_sincro('b2cOrdersDownloadSync'))

        success_records = []
        error_records = [order["increment_id"] for order in self.error_data]
        after_sync_error_records = []

        for order in self.success_data:
            try:
                self.send_request("put", replace=[order["entity_id"],order["status"]])
                success_records.append(order["increment_id"])
            except Exception as e:
                self.after_sync_error(order, e)
                after_sync_error_records.append(order["increment_id"])

        for order in self.error_data:
            try:
                self.send_request("put", replace=[order["entity_id"],order["status"]])
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
