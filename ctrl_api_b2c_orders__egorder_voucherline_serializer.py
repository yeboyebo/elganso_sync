from YBLEGACY.constantes import *

from controllers.api.b2c.orders.serializers.egorder_line_serializer import EgOrderLineSerializer


class EgOrderVoucherLineSerializer(EgOrderLineSerializer):

    def get_data(self):
        if not self.init_data["vale_description"] or not self.init_data["total"]:
            return False

        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        self.set_string_value("codtienda", "AWEB")

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("ivaincluido", True)
        self.set_data_relation("iva", "iva")

        vale_total = round(parseFloat(self.init_data["vale_total"]) * (-1), 2)
        dto_sin_iva = vale_total

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
