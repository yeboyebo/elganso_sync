from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.magento2.refounds.serializers.mg2_refound_line_serializer import Mg2RefoundLineSerializer


class Mg2RefoundTarjetaMonederoSerializer(Mg2RefoundLineSerializer):

    def get_data(self):

        importe = parseFloat(self.init_data["importe_gastado"])
        if not importe or importe == 0 or importe == "0.0000" or importe == "0.00":
            return False

        iva = parseFloat(self.init_data["iva"])
        if not iva or iva == "":
            iva = 0

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", "0000ATEMP11111", max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", "8445005503262", max_characters=20)
        self.set_string_value("talla", "TU", max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        self.set_data_value("cantdevuelta", 0)

        self.set_data_value("ivaincluido", True)
        self.set_data_relation("iva", "iva")

        cant_linea = self.get_cantidad()
        pvpunitarioiva = parseFloat(importe) * self.init_data["tasaconv"]
        pvpsindtoiva = parseFloat(importe) * self.init_data["tasaconv"]
        pvptotaliva = parseFloat(importe) * self.init_data["tasaconv"]

        pvpunitario = parseFloat(importe) * self.init_data["tasaconv"]
        pvpsindto = parseFloat(importe) * self.init_data["tasaconv"]
        pvptotal = parseFloat(importe) * self.init_data["tasaconv"]
        if iva and iva != 0:
            pvpunitario = pvpunitario / (1 + (parseFloat(iva) / 100))
            pvpsindto = pvpsindto / (1 + (parseFloat(iva) / 100))
            pvptotal = pvptotal / (1 + (parseFloat(iva) / 100))

        if self.init_data["tipo_linea"] == "tarjetaMonederoNegativos":
            pvpsindtoiva = pvpsindtoiva * (-1)
            pvptotaliva = pvptotaliva * (-1)
            pvpsindto = pvpsindto * (-1)
            pvptotal = pvptotal * (-1)
            cant_linea = cant_linea * (-1)
        else:
            pvpunitario = pvpunitario * (-1)
            pvpunitarioiva = pvpunitarioiva * (-1)
            pvpsindtoiva = pvpsindtoiva * (-1)
            pvptotaliva = pvptotaliva * (-1)
            pvpsindto = pvpsindto * (-1)
            pvptotal = pvptotal * (-1)

        self.set_data_value("pvpunitarioiva", pvpunitarioiva)
        self.set_data_value("pvpsindtoiva", pvpsindtoiva)
        self.set_data_value("pvptotaliva", pvptotaliva)
        self.set_data_value("pvpunitario", pvpunitario)
        self.set_data_value("pvpsindto", pvpsindto)
        self.set_data_value("pvptotal", pvptotal)
        self.set_data_value("cantidad", cant_linea)

        return True

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
