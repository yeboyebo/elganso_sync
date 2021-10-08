from YBLEGACY import qsatype
from YBLEGACY.constantes import *
import json

from controllers.api.magento2.refounds.serializers.mg2_refound_line_serializer import Mg2RefoundLineSerializer


class Mg2RefoundDiscountLineSerializer(Mg2RefoundLineSerializer):

    bono = None

    def get_data(self):

        if str(self.init_data["cupon_bono"]) == "None":
            return False

        dto = parseFloat(self.init_data["discount_refunded"])
        if not dto or dto == 0 or dto == "0.0000" or dto == "0.00":
            return False

        self.get_bono_data()
        iva = parseFloat(self.init_data["iva"])
        if not iva or iva == "":
            iva = 0

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_value("iva", self.init_data["iva"])
        self.set_data_value("ivaincluido", True)
        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        pvpUnitario = parseFloat(self.init_data["discount_refunded"]) / ((100 + iva) / 100)
        pvpSinDto = pvpUnitario
        pvpTotal = pvpSinDto
        pvpUnitarioIva = parseFloat(self.init_data["discount_refunded"])
        pvpSinDtoIva = pvpUnitarioIva
        pvpTotalIva = pvpUnitarioIva

        if str(self.init_data["tipo_linea"]) == "BonoNegativo":
            pvpSinDto = pvpSinDto * (-1)
            pvpTotal = pvpTotal * (-1)
            pvpSinDtoIva = pvpUnitarioIva * (-1)
            pvpTotalIva = pvpUnitarioIva * (-1)

        self.set_string_value("pvpunitario", pvpUnitario)
        self.set_string_value("pvpsindto", pvpSinDto)
        self.set_string_value("pvptotal", pvpTotal)
        self.set_string_value("pvpunitarioiva", pvpUnitarioIva)
        self.set_string_value("pvpsindtoiva", pvpSinDtoIva)
        self.set_string_value("pvptotaliva", pvpTotalIva)

        self.insertarMovBono()

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
            codbono = qsatype.FLUtil.sqlSelect("eg_movibono", "codbono", "venta = '{}'".format(str(self.init_data["codcomanda"])))
            if not codbono or codbono == "" or codbono is None:
                descripcion_bono = False

        if descripcion_bono:
            dto = qsatype.FLUtil.sqlSelect("eg_movibono", "importe", "codbono = '{}' AND venta = '{}'".format(codbono, str(self.init_data["codcomanda"])))
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

    def get_codimpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def insertarMovBono(self):
        try:
            existeBono = str(qsatype.FLUtil.sqlSelect("eg_bonos", "codbono", "codbono = '" + str(self.init_data["cupon_bono"]) + "'"))
            print("existeBono: ", existeBono)
            if existeBono == "None":
                return True

            importeMovBono = parseFloat(self.init_data["discount_refunded"]) * (-1)

            if str(self.init_data["tipo_linea"]) == "BonoPositivo":
                importeMovBono = parseFloat(self.init_data["discount_refunded"])

            curMoviBono = qsatype.FLSqlCursor("eg_movibono")
            curMoviBono.setModeAccess(curMoviBono.Insert)
            curMoviBono.refreshBuffer()
            curMoviBono.setValueBuffer("codbono", str(self.init_data["cupon_bono"]))
            curMoviBono.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curMoviBono.setValueBuffer("venta", self.init_data["codcomanda"])
            curMoviBono.setValueBuffer("importe", importeMovBono)
            if not curMoviBono.commitBuffer():
                return True

            if not qsatype.FLUtil.execSql(ustr(u"UPDATE eg_bonos SET saldoconsumido = (-1) * (SELECT SUM(importe) FROM eg_movibono WHERE codbono = '", str(self.init_data["cupon_bono"]), "'), saldopendiente = saldoinicial + (SELECT SUM(importe) FROM eg_movibono WHERE codbono = '", str(self.init_data["cupon_bono"]), "') WHERE codbono = '", str(self.init_data["cupon_bono"]), "'")):
                return True

            return True

        except Exception as e:
            qsatype.debug(e)
            return False
