from YBLEGACY import qsatype

from controllers.api.sync.base.serializers.aqserializer import AQSerializer


class EgCashCountSerializer(AQSerializer):

    def get_data(self):
        idarqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = 'AWEB' AND diadesde >= '{}' AND idasiento IS NULL ORDER BY diadesde ASC".format(self.init_data["fecha"]))

        if idarqueo:
            self.data = {"idtpv_arqueo": idarqueo, "skip": True}
            return True

        fecha = qsatype.Date()
        idarqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = 'AWEB' AND diadesde = '{}'".format(fecha))

        if idarqueo:
            self.data = {"idtpv_arqueo": idarqueo, "skip": True}
            return True

        punto_venta = qsatype.FLUtil.sqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = 'AWEB'")

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("codtpv_agenteapertura", "0350")
        self.set_string_value("ptoventa", punto_venta, max_characters=6)
        self.set_string_value("diadesde", fecha)
        self.set_string_value("diahasta", fecha)
        self.set_string_value("horadesde", "00:00:01")
        self.set_string_value("horahasta", "23:59:59")

        self.set_data_value("abierta", True)
        self.set_data_value("sincronizado", True)
        self.set_data_value("idfactura", 0)
