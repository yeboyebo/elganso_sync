from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.api.b2c.orders.serializers.egorder_line_serializer import EgOrderLineSerializer


class EgOrderSoles4soulLineSerializer(EgOrderLineSerializer):

    def get_data(self):
        if "imagen_recoger" not in self.init_data:
            return False

        if str(self.init_data["imagen_recoger"]) == "None" or self.init_data["imagen_recoger"] == None or self.init_data["imagen_recoger"] == False:
            return False

        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        refArticulo = self.get_referencia()
        if not refArticulo:
            return False

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", refArticulo, max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(refArticulo), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(refArticulo), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)
        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)
        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())
        self.set_data_value("ivaincluido", True)
        self.set_data_relation("iva", "iva")
        self.set_data_value("pvpunitarioiva", 0)
        self.set_data_value("pvpsindtoiva", 0)
        self.set_data_value("pvptotaliva", 0)
        self.set_data_value("pvpunitario", 0)
        self.set_data_value("pvpsindto", 0)
        self.set_data_value("pvptotal", 0)

        return True

    def get_referencia(self):
        referencia = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ART_SOLES4SOULS'")
        if not referencia or str(referencia) == "None" or referencia == None:
            raise NameError("No se ha establecido la referencia de ART_SOLES4SOULS.")
            return False 
        return referencia

    def get_descripcion(self, refArticulo):
        return qsatype.FLUtil.sqlSelect("articulos", "descripcion", "referencia = '" + str(refArticulo) + "'")

    def get_barcode(self, refArticulo):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "barcode", "referencia = '" + str(refArticulo) + "'")

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return -1
