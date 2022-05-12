from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.magento2.orders.serializers.mg2_lineaecommerceexcluida_serializer import Mg2LineaEcommerceExcluidaSerializer


class EgOrderLineSerializer(DefaultSerializer):

    def get_data(self):
        iva = self.get_init_value("commission_rate_vat")
        if not iva or iva == "":
            iva = 0

        self.set_string_value("codtienda", self.get_codtienda())

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        pvpunitario = parseFloat(self.get_init_value("price_unit") / ((100 + iva) / 100))
        pvpsindto = parseFloat(self.get_init_value("price") / ((100 + iva) / 100))
        pvptotal = parseFloat(self.get_init_value("total_price") / ((100 + iva) / 100))

        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("ivaincluido", True)
        self.set_data_value("pvpunitario", pvpunitario)
        self.set_data_value("pvpsindto", pvpsindto)
        self.set_data_value("pvptotal", pvptotal)

        self.set_data_relation("iva", "commission_rate_vat")
        self.set_data_relation("pvpunitarioiva", "price_unit")
        self.set_data_relation("pvpsindtoiva", "price")
        self.set_data_relation("pvptotaliva", "total_price")

        if "almacen" in self.init_data:
            print("///////////entra: ", str(self.init_data["almacen"]))
            if str(self.init_data["almacen"]) != "AWEB":
                linea_ecommerce_excluida = Mg2LineaEcommerceExcluidaSerializer().serialize(self.init_data)
                self.data["children"]["lineaecommerceexcluida"] = linea_ecommerce_excluida

        return True

    def get_codtienda(self):
        return "AEVV"

    def get_referencia(self):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "referencia", "barcode = '{}'".format(self.get_barcode()))

    def get_descripcion(self):
        return self.get_init_value("product_title")

    def get_barcode(self):
        return self.get_init_value("product_sku")

    def get_talla(self):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "talla", "barcode = '{}'".format(self.get_barcode())) or "TU"

    def get_color(self):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "color", "barcode = '{}'".format(self.get_barcode())) or "U"

    def get_codimpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def get_cantidad(self):
        return self.get_init_value("quantity") or 0
