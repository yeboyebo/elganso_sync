import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.b2c.orders.serializers.egorder_line_serializer import EgOrderLineSerializer


class EgOrderDiscountLineSerializer(EgOrderLineSerializer):

    bono = None

    def get_data(self):
        dto = self.init_data["discount_amount"]
        if not dto or dto == 0 or dto == "0.0000" or dto == "0.00":
            return False

        self.get_bono_data()

        if self.bono:
            dto = self.bono["discount"]

        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_data_relation("iva", "iva")
        self.set_data_value("ivaincluido", True)
        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_relation("pvpunitarioiva", "discount_amount")
        self.set_data_relation("pvpsindtoiva", "discount_amount")
        self.set_data_relation("pvptotaliva", "discount_amount")

        dto_sin_iva = dto

        if iva and iva != 0:
            dto_sin_iva = dto / (1 + (parseFloat(iva) / 100))

        self.set_data_value("pvpunitario", dto_sin_iva)
        self.set_data_value("pvpsindto", dto_sin_iva)
        self.set_data_value("pvptotal", dto_sin_iva)

        return True

    def get_bono_data(self):
        self.bono = False

        descripcion_bono = False
        json_bono = False
        codbono = False

        try:
            strbono = qsatype.FLUtil.sqlSelect("tpv_gestionparametros", "valor", "param = 'GASTAR_BONOS'")
            json_bono = json.loads(strbono)
        except Exception:
            pass

        if json_bono and "fechahasta" in json_bono and json_bono["fechahasta"] and json_bono["fechahasta"] != "":
            if qsatype.FLUtil.daysTo(qsatype.Date(), json_bono["fechahasta"]) >= 0:
                descripcion_bono = True

        if descripcion_bono:
            codbono = qsatype.FLUtil.sqlSelect("eg_movibono", "codbono", "venta = '{}'".format(self.init_data["codcomanda"]))
            if not codbono or codbono == "" or codbono is None:
                descripcion_bono = False

        if descripcion_bono:
            dto = qsatype.FLUtil.sqlSelect("eg_movibono", "importe", "codbono = '{}' AND venta = '{}'".format(codbono, self.init_data["codcomanda"]))

            if self.init_data["codcomanda"][:4] == "WEB7":
                dto = dto / 0.8

            self.bono = {
                "referencia": json_bono["referenciabono"],
                "barcode": json_bono["barcodebono"],
                "descripcion": "BONO {}".format(codbono),
                "discount": dto
            }

    def get_referencia(self):
        if self.bono:
            return self.bono["referencia"]

        return "0000ATEMP00001"

    def get_descripcion(self):
        if self.bono:
            return self.bono["descripcion"]

        return "DESCUENTO"

    def get_barcode(self):
        if self.bono:
            return self.bono["barcode"]

        return "8433613403654"

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return 1
