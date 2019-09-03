from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgOrderLineSerializer(DefaultSerializer):

    def get_data(self):
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        if not self.comprobar_talla():
            return False

        self.set_string_value("codtienda", "AWEB")

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        pvpunitario = parseFloat(self.init_data["pvpunitarioiva"] / ((100 + iva) / 100))
        pvpsindto = parseFloat(self.init_data["pvpsindtoiva"] / ((100 + iva) / 100))
        pvptotal = parseFloat(self.init_data["pvptotaliva"] / ((100 + iva) / 100))

        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("ivaincluido", True)
        self.set_data_value("pvpunitario", pvpunitario)
        self.set_data_value("pvpsindto", pvpsindto)
        self.set_data_value("pvptotal", pvptotal)

        self.set_data_relation("iva", "iva")
        self.set_data_relation("pvpunitarioiva", "pvpunitarioiva")
        self.set_data_relation("pvpsindtoiva", "pvpsindtoiva")
        self.set_data_relation("pvptotaliva", "pvptotaliva")

        return True

    def get_splitted_sku(self):
        return self.init_data["sku"].split("-")

    def get_referencia(self):
        return self.get_splitted_sku()[0]

    def get_descripcion(self):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '{}'".format(self.get_referencia()))

    def get_barcode(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0].upper()
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            referencia = splitted_sku[0].upper()
            talla = splitted_sku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '{}' AND talla = '{}'".format(referencia, talla))
        else:
            return "ERRORNOTALLA"

    def get_talla(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "talla", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            return splitted_sku[1]
        else:
            return "TU"

    def get_color(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            referencia = splitted_sku[0]
            talla = splitted_sku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '{}' AND talla = '{}'".format(referencia, talla))
        else:
            return "U"

    def get_codimpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def get_cantidad(self):
        return self.init_data["cantidad"]


    def comprobar_talla(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            cant_tallas = qsatype.FLUtil.quickSqlSelect("atributosarticulos", "COUNT(*)", "referencia = '{}'".format(referencia))

            if float(cant_tallas) > 1:
                raise NameError("Error. Se ha indicado una referencia con varias tallas asociadas, revisar JSON")

        return True
