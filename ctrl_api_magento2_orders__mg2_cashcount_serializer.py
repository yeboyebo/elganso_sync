from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2CashCountSerializer(DefaultSerializer):

    def get_data(self):
  
        idarqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = '{}' AND diadesde >= '{}' AND idasiento IS NULL ORDER BY diadesde ASC".format(self.init_data["codtienda"],self.init_data["fecha"]))
 
        if idarqueo:
            self.data = {"idtpv_arqueo": idarqueo, "skip": True}
            return True
        print("CODTIENDA: " ,  self.init_data["codtienda"])
        fecha = qsatype.Date()
        idarqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = '{}' AND diadesde = '{}'".format(self.init_data["codtienda"],fecha))

        if idarqueo:
            self.data = {"idtpv_arqueo": idarqueo, "skip": True}
            return True

        punto_venta = qsatype.FLUtil.sqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = '{}'".format(self.init_data["codtienda"]))

        self.set_string_value("codtienda", self.init_data["codtienda"])
        self.set_string_value("codtpv_agenteapertura", "0350")
        self.set_string_value("ptoventa", punto_venta, max_characters=6)
        self.set_string_value("diadesde", fecha)
        self.set_string_value("diahasta", fecha)
        self.set_string_value("horadesde", "00:00:01")
        self.set_string_value("horahasta", "23:59:59")

        self.set_data_value("abierta", True)
        self.set_data_value("sincronizado", True)
        self.set_data_value("idfactura", 0)

        fake_cursor = qsatype.FLSqlCursor("tpv_arqueos")
        fake_cursor.select("codtienda = '" + self.init_data["codtienda"] + "'")
        fake_cursor.first()
        fake_cursor.refreshBuffer()

        idarqueo = qsatype.FactoriaModulos.get("formRecordtpv_arqueos").iface.codigoArqueo(fake_cursor)
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)

        return True
