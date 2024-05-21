from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgStoreOrderSerializer(DefaultSerializer):

    def get_data(self):
        del self.init_data["cabecera"]["idtpv_comanda"]
        del self.init_data["cabecera"]["idfactura"]
        del self.init_data["cabecera"]["egidfacturarec"]
        del self.init_data["cabecera"]["idprovincia"]

        for field in self.init_data["cabecera"]:
            self.init_data["cabecera"][field] = self.format_value(field, self.init_data["cabecera"][field])

        for linea in self.init_data["lineas"]:
            del linea["idtpv_comanda"]
            del linea["idtpv_linea"]

            for field in linea:
                linea[field] = self.format_value(field, linea[field])

        for pago in self.init_data["pagos"]:
            del pago["idtpv_comanda"]
            del pago["idpago"]
            del pago["idasiento"]

            for field in pago:
                pago[field] = self.format_value(field, pago[field])

        for motivo in self.init_data["motivos"]:
            del motivo["id"]

            for field in motivo:
                motivo[field] = self.format_value(field, motivo[field])

        for datosenvio in self.init_data["datosenvio"]:
            del datosenvio["iddatosenviocomanda"]

            for field in datosenvio:
                datosenvio[field] = self.format_value(field, datosenvio[field])


        self.set_string_value("datos", self.init_data, max_characters=None, skip_replace=True)
        self.set_string_value("estado", "PTE")
        self.set_string_value("fecha", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameFechaActual())
        self.set_string_value("hora", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameHoraActual())

        self.set_string_relation("codtienda", "cabecera//codtienda")
        self.set_string_relation("codigo", "cabecera//codigo")

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
