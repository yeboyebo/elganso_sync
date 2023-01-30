import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.magento2.orders.serializers.mg2_orderline_serializer import Mg2OrderLineSerializer


class Mg2TarjetaRegaloLineSerializer(Mg2OrderLineSerializer):

    def get_data(self):


        importe = float(self.init_data["importe_gastado"])

        if not importe or float(importe) == 0 or importe == "0.0000" or importe == "0.00":
            return False

        tasaconv = float(self.init_data["tasaconv"])

        importe = importe * (-1)

        importe = round(parseFloat(importe * tasaconv), 2)
      
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", "0000ATEMP11111", max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", "8445005503262", max_characters=20)
        self.set_string_value("talla", "TU", max_characters=50)
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

    def get_codtarjetaregalo(self):

        cod_activacion = qsatype.FLUtil.quickSqlSelect("eg_tarjetamonedero", "codactivacion", "coduso = '{}'".format(self.init_data["cod_uso"]))

        if not cod_activacion:
            return False

        return cod_activacion

    def get_descripcion(self):
        cod_activacion = self.get_codtarjetaregalo()

        if not cod_activacion:
            return False

        return "TARJETA MONEDERO {}".format(cod_activacion)

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return 1
