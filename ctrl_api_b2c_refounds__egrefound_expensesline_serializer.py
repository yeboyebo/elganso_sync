from YBLEGACY.constantes import *

from controllers.api.b2c.refounds.serializers.egrefound_line_serializer import EgRefoundLineSerializer


class EgRefoundExpensesLineSerializer(EgRefoundLineSerializer):

    def get_data(self):
        if "shipping_price" not in self.init_data:
            return False

        if not self.init_data["shipping_price"]:
            return False

        shipping_price = self.init_data["shipping_price"]
        if not shipping_price or shipping_price == 0 or shipping_price == "0.0000" or shipping_price == "0.00":
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

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        self.set_data_value("cantdevuelta", 0)
        

        self.set_data_value("ivaincluido", True)
        self.set_data_relation("iva", "iva")

        cant_linea = self.get_cantidad()
        pvpunitarioiva = parseFloat(shipping_price)
        pvpsindtoiva = parseFloat(shipping_price)
        pvptotaliva = parseFloat(shipping_price)

        pvpunitario = parseFloat(shipping_price)
        pvpsindto = parseFloat(shipping_price)
        pvptotal = parseFloat(shipping_price)
        if iva and iva != 0:
            pvpunitario = pvpunitario / (1 + (parseFloat(iva) / 100))
            pvpsindto = pvpsindto / (1 + (parseFloat(iva) / 100))
            pvptotal = pvptotal / (1 + (parseFloat(iva) / 100))

        if self.init_data["tipo_linea"] == "GastosNegativos":
            pvpsindtoiva = pvpsindtoiva * (-1)
            pvptotaliva = pvptotaliva * (-1)
            pvpsindto = pvpsindto * (-1)
            pvptotal = pvptotal * (-1)
            cant_linea = cant_linea * (-1)

        self.set_data_value("pvpunitarioiva", pvpunitarioiva)
        self.set_data_value("pvpsindtoiva", pvpsindtoiva)
        self.set_data_value("pvptotaliva", pvptotaliva)
        self.set_data_value("pvpunitario", pvpunitario)
        self.set_data_value("pvpsindto", pvpsindto)
        self.set_data_value("pvptotal", pvptotal)
        self.set_data_value("cantidad", cant_linea)

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
