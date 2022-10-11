from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.api.magento2.refounds.serializers.mg2_refound_line_serializer import Mg2RefoundLineSerializer


class Mg2RefoundPointLineSerializer(Mg2RefoundLineSerializer):

    def get_data(self):
        if not self.init_data["points_used"] or str(self.init_data["points_used"]) == "None":
            return False

        iva = parseFloat(self.init_data["iva"])
        if not iva or iva == "":
            iva = 0

        self.set_string_value("codtienda", "AWEB")

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", "DESCUENTO PAGO PUNTOS " + str(self.get_codtarjetapuntos()), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("ivaincluido", True)
        self.set_data_relation("iva", "iva")

        pvpUnitario = (parseFloat(self.init_data["points_used"])) / ((100 + iva) / 100) * self.init_data["tasaconv"]
        pvpSinDto = pvpUnitario
        pvpTotal = pvpSinDto
        pvpUnitarioIva = (parseFloat(self.init_data["points_used"])) * self.init_data["tasaconv"]
        pvpSinDtoIva = pvpUnitarioIva
        pvpTotalIva = pvpUnitarioIva

        if self.init_data["tipo_linea"] == "PuntosNegativos":
            pvpSinDto = pvpSinDto * (-1)
            pvpTotal = pvpTotal * (-1)
            pvpSinDtoIva = pvpUnitarioIva * (-1)
            pvpTotalIva = pvpUnitarioIva * (-1)
            pvpUnitario = pvpUnitario * (-1)
            pvpUnitarioIva = pvpUnitarioIva * (-1)

        self.set_data_value("pvpunitario", pvpUnitario)
        self.set_data_value("pvpsindto", pvpSinDto)
        self.set_data_value("pvptotal", pvpTotal)
        self.set_data_value("pvpunitarioiva", pvpUnitarioIva)
        self.set_data_value("pvpsindtoiva", pvpSinDtoIva)
        self.set_data_value("pvptotaliva", pvpTotalIva)

        self.crear_registro_puntos()
        return True

    def get_referencia(self):
        return "0000ATEMP00001"

    def get_barcode(self):
        return "8433613403654"

    def get_talla(self):
        return None

    def get_color(self):
        return None

    def get_cantidad(self):
        return 1

    def crear_registro_puntos(self):
        canPuntos = parseFloat(self.init_data["discount_refunded"])
        if self.init_data["tipo_linea"] == "PuntosNegativos":
            canPuntos = canPuntos * (-1)

        curMP = qsatype.FLSqlCursor("tpv_movpuntos")
        curMP.setModeAccess(curMP.Insert)
        # curMP.setActivatedCommitActions(False)
        curMP.refreshBuffer()
        curMP.setValueBuffer("codtarjetapuntos", str(self.get_codtarjetapuntos()))
        curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
        curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
        curMP.setValueBuffer("horamod", self.get_hora(str(qsatype.Date())))
        curMP.setValueBuffer("canpuntos", canPuntos)
        curMP.setValueBuffer("operacion", self.init_data["codcomanda"])
        curMP.setValueBuffer("sincronizado", False)
        curMP.setValueBuffer("codtienda", "AWEB")

        if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
            return False

        if not curMP.commitBuffer():
            return False

        """if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_tarjetaspuntos SET saldopuntos = CASE WHEN (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) IS NULL THEN 0 ELSE (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) END WHERE codtarjetapuntos = '{}'".format(str(self.get_codtarjetapuntos())))):
            return False"""

        return True

    def get_hora(self, fecha):
        h = fecha[-(8):]
        h = "23:59:59" if h == "00:00:00" else h
        return h

    def get_codtarjetapuntos(self):
        codtarjetapuntos = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codtarjetapuntos", "codigo = '{}'".format("WEB" + str(self.init_data["increment_id"])))

        if not codtarjetapuntos:
            codtarjetapuntos = ""

        return codtarjetapuntos
