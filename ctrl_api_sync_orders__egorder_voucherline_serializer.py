from YBLEGACY.constantes import *

from controllers.api.sync.orders.serializers.egorder_line_serializer import EgOrderLineSerializer


class EgOrderVoucherLineSerializer(EgOrderLineSerializer):

    def get_data(self):
        if not self.init_data["vale_description"] or not self.init_data["total"]:
            return False

        super().get_data()

        vale_total = round(parseFloat(self.init_data["vale_total"]) * (-1), 2)
        dto_sin_iva = vale_total
        iva = self.init_data["iva"]

        if iva and iva != 0:
            dto_sin_iva = dto_sin_iva / (1 + (parseFloat(iva) / 100))

        self.set_data_value("pvpunitarioiva", vale_total)
        self.set_data_value("pvpsindtoiva", vale_total)
        self.set_data_value("pvptotaliva", vale_total)
        self.set_data_value("pvpunitario", dto_sin_iva)
        self.set_data_value("pvpsindto", dto_sin_iva)
        self.set_data_value("pvptotal", dto_sin_iva)

        return True

    def get_referencia(self):
        return "0000ATEMP00040"

    def get_descripcion(self):
        return "{} {}".format(self.init_data["vale_description"], self.init_data["vale_codigo_cliente"])

    def get_barcode(self):
        return "8433614171347"

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return 1
