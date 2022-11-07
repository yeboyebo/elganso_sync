from YBLEGACY import qsatype
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2RefoundPaymentSerializer(DefaultSerializer):

    def get_data(self):

        idarqueo = self.init_data["idarqueo"]
        if not idarqueo:
            return False

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
        importe = float(self.init_data["total_pay"])  * self.init_data["tasaconv"]
        if str(self.init_data["tipo_pago"]) == "Negativo":
            importe = importe * (-1)

        if "cod_uso" in self.init_data:
            self.set_string_value("importe", self.init_data["importe_gastado"])
            self.set_string_value("coduso", self.init_data["cod_uso"])
            self.set_string_value("codpago", self.get_formaPagoTarjetaMonedero())
        else:
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

    def get_formaPagoTarjetaMonedero(self):
        return qsatype.FLUtil.quickSqlSelect("tpv_datosgenerales", "pagotr", "1=1")
