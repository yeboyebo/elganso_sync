import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.magento2.orders.serializers.mg2_orderline_serializer import Mg2OrderLineSerializer


class Mg2PointsLineSerializer(Mg2OrderLineSerializer):

    def get_data(self):
        descripcion = False
        importe = 0
        if "email" in self.init_data:
            descripcion = self.get_descripcion()

        if not descripcion:
            return False

        if "puntos_gastados" in self.init_data:
            importe = self.init_data["puntos_gastados"]
            if not importe or float(importe) == 0 or importe == "0.0000" or importe == "0.00":
                return False

        importe = importe * (-1)
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", descripcion, max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_data_relation("iva", "iva")
        self.set_data_value("ivaincluido", True)
        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("pvpunitarioiva", importe)
        self.set_data_value("pvpsindtoiva", importe)
        self.set_data_value("pvptotaliva", importe)

        importe_sin_iva = importe

        if iva and iva != 0:
            importe_sin_iva = importe / (1 + (parseFloat(iva) / 100))

        self.set_data_value("pvpunitario", importe_sin_iva)
        self.set_data_value("pvpsindto", importe_sin_iva)
        self.set_data_value("pvptotal", importe_sin_iva)

        return True

    def get_referencia(self):
        return "0000ATEMP00001"

    def get_codtarjetapuntos(self):

        email = self.init_data["email"]
        codtarjetapuntos = qsatype.FLUtil.quickSqlSelect("tpv_tarjetaspuntos", "codtarjetapuntos", "email = '{}'".format(email).lower())

        if not codtarjetapuntos:
            return False

        return codtarjetapuntos

    def get_descripcion(self):
        codtarjetapuntos = self.get_codtarjetapuntos()

        if not codtarjetapuntos:
            return False

        return "DESCUENTO PUNTOS {}".format(codtarjetapuntos)

    def get_barcode(self):
        return "8433613403654"

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return 1
