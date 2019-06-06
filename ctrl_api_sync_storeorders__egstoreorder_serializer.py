from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgStoreOrderSerializer(DefaultSerializer):

    def get_data(self):
        del self.init_data["header"]["idtpv_comanda"]
        del self.init_data["header"]["idfactura"]
        del self.init_data["header"]["egidfacturarec"]
        del self.init_data["header"]["idprovincia"]

        for field in self.init_data:
            self.init_data[field] = self.format_value(field, self.init_data[field])

        for line in self.init_data["lines"]:
            del line["idtpv_comanda"]
            del line["idtpv_linea"]

            for field in line:
                self.line[field] = self.format_value(field, line[field])

        for payment in self.init_data["payments"]:
            del payment["idtpv_comanda"]
            del payment["idpago"]
            del payment["idasiento"]

            for field in payment:
                self.payment[field] = self.format_value(field, payment[field])

        for reason in self.init_data["reasons"]:
            del reason["id"]

            for field in reason:
                self.reason[field] = self.format_value(field, reason[field])

        self.set_string_value("datos", str(self.init_data))
        self.set_string_value("estado", "PTE")
        self.set_string_value("fecha", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameFechaActual())
        self.set_string_value("hora", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameHoraActual())

        self.set_string_relation("codigo", "header//codigo")
        self.set_string_relation("codtienda", "header//codtienda")

        return True

    def format_value(self, field, value):
        if value is None:
            return ""

        if field == "fecha" or field == "fechasincro" or field == "hora":
            return str(value)

        if field == "ptesincrofactura":
            return "true"

        if str(value) == "True" or str(value) == "False":
            return str(value).lower()

        return value
