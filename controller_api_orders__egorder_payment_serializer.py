from controllers.api.sync.base.serializers.aqserializer import AQSerializer


class EgOrderPaymentSerializer(AQSerializer):

    def get_data(self):
        idarqueo = self.init_data["idarqueo"]
        if not idarqueo:
            return False

        self.set_data_value("anulado", False)
        self.set_data_value("editable", True)
        self.set_data_value("nogenerarasiento", True)

        self.set_string_value("estado", "Pagado")
        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)

        self.set_data_relation("importe", "total", default=0)

        self.set_string_relation("fecha", "fecha")
        self.set_string_relation("codpago", "codpago", max_characters=10)
        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)
        self.set_string_relation("codtpv_puntoventa", "codtpv_puntoventa", max_characters=6)
