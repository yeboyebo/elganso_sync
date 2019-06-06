from YBLEGACY.constantes import *

from controllers.api.sync.orders.serializers.egorder_line_serializer import EgOrderLineSerializer


class EgOrderExpensesLineSerializer(EgOrderLineSerializer):

    def get_data(self):
        if not self.init_data["shipping_price"]:
            return False

        super().get_data()

        self.set_data_relation("pvpunitarioiva", "shipping_price")
        self.set_data_relation("pvpsindtoiva", "shipping_price")
        self.set_data_relation("pvptotaliva", "shipping_price")

        iva = self.init_data["iva"]
        gastos_sin_iva = self.init_data["shipping_price"]

        if iva and iva != 0:
            gastos_sin_iva = gastos_sin_iva / (1 + (parseFloat(iva) / 100))

        self.set_data_value("pvpunitario", gastos_sin_iva)
        self.set_data_value("pvpsindto", gastos_sin_iva)
        self.set_data_value("pvptotal", gastos_sin_iva)

        return True

    def get_referencia(self):
        return "0000ATEMP00001"

    def get_descripcion(self):
        return "MANIPULACIÓN Y ENVIO"

    def get_barcode(self):
        return "8433613403654"

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return 1
