from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2RefoundPaymentSerializer(DefaultSerializer):

    def get_data(self):

        idarqueo = self.init_data["idarqueo"]
        if not idarqueo:
            return False

        importe = float(self.init_data["total_pay"])  * self.init_data["tasaconv"]

        self.set_data_value("anulado", False)
        self.set_data_value("editable", True)
        self.set_data_value("nogenerarasiento", True)
        self.set_string_value("estado", "Pagado")
        self.set_string_value("codtienda", self.init_data["codtienda"])
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("codtpv_puntoventa", self.init_data["puntoventa"])
        self.set_string_value("fecha", str(qsatype.Date())[:10])
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)
        self.set_string_value("codcomanda", str(self.init_data["codcomanda"]))
        codPago = self.get_codpago()

        if str(self.init_data["tipo_pago"]) == "Negativo":
            importe = importe * (-1)

        self.set_string_value("importe", importe)
        self.set_string_value("codpago", codPago)




        return True

    def get_codpago(self):
        codPago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '" + str(self.init_data["payment_method"]) + "'")

        if not codPago:
            codPago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")
            if not codPago:
                codPago = "CONT"

        return codPago
