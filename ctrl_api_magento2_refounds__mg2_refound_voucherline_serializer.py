from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.api.magento2.refounds.serializers.mg2_refound_line_serializer import Mg2RefoundLineSerializer


class Mg2RefoundVoucherLineSerializer(Mg2RefoundLineSerializer):

    def get_data(self):

        if str(self.init_data["vale_description"]) == "None" or str(self.init_data["vale_total"]) == "None":
            return False

        iva = parseFloat(self.init_data["iva"])
        if not iva or iva == "":
            iva = 0

        self.set_string_value("codtienda", "AWEB")

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", "DESCUENTO VALE: " + self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        self.set_data_value("cantdevuelta", 0)

        self.set_data_value("ivaincluido", True)
        self.set_string_value("iva", iva)

        pvpUnitario = parseFloat(self.init_data["vale_total"]) / ((100 + iva) / 100) * self.init_data["tasaconv"]
        pvpSinDto = pvpUnitario
        pvpTotal = pvpSinDto
        pvpUnitarioIva = parseFloat(self.init_data["vale_total"]) * self.init_data["tasaconv"]
        pvpSinDtoIva = pvpUnitarioIva
        pvpTotalIva = pvpUnitarioIva
        cant_linea = self.get_cantidad()

        if self.init_data["tipo_linea"] == "ValesNegativos":
           pvpUnitario = pvpUnitario * (-1)
           pvpUnitarioIva = pvpUnitarioIva * (-1)
           cant_linea = cant_linea * (-1)
        else:
            pvpUnitario = pvpUnitario * (-1)
            pvpUnitarioIva = pvpUnitarioIva * (-1)
            pvpSinDto = pvpSinDto * (-1)
            pvpTotal = pvpTotal * (-1)
            pvpSinDtoIva = pvpSinDtoIva * (-1)
            pvpTotalIva = pvpTotalIva * (-1)

        self.set_data_value("cantidad", cant_linea)
        self.set_data_value("pvpunitario", pvpUnitario)
        self.set_data_value("pvpsindto", pvpSinDto)
        self.set_data_value("pvptotal", pvpTotal)
        self.set_data_value("pvpunitarioiva", pvpUnitarioIva)
        self.set_data_value("pvpsindtoiva", pvpSinDtoIva)
        self.set_data_value("pvptotaliva", pvpTotalIva)

        self.crear_registro_movvale()

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

    def crear_registro_movvale(self):
        importe = parseFloat(self.init_data["vale_total"])

        if self.init_data["tipo_linea"] == "ValesNegativos":
            importe = importe * (-1)

        curMovVale = qsatype.FLSqlCursor("tpv_movivale")
        curMovVale.setModeAccess(curMovVale.Insert)
        curMovVale.refreshBuffer()
        curMovVale.setValueBuffer("total", importe)
        curMovVale.setValueBuffer("idsincropago", str(self.init_data["codcomanda"]))
        curMovVale.setValueBuffer("refvale", str(self.init_data["vale_description"]))

        if not curMovVale.commitBuffer():
            return False

        if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_vales SET saldoconsumido = CASE WHEN (SELECT SUM(total) FROM tpv_movivale WHERE refvale = tpv_vales.referencia) IS NULL THEN 0 ELSE (SELECT SUM(total) FROM tpv_movivale WHERE refvale = tpv_vales.referencia) END WHERE referencia = '", str(self.init_data["vale_description"]), "'")):
            return False

        if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_vales SET saldopendiente = CASE WHEN (total - saldoconsumido) IS NULL THEN 0 ELSE (total - saldoconsumido) END, fechamod = CURRENT_DATE, horamod = CURRENT_TIME WHERE referencia = '", str(self.init_data["vale_description"]), "'")):
            return False

        return True
