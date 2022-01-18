from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgStoreInventarioSerializer(DefaultSerializer):

    def get_data(self):
        del self.init_data["cabecera"]["idinventario"]

        for field in self.init_data["cabecera"]:
            self.init_data["cabecera"][field] = self.format_value(field, self.init_data["cabecera"][field])

        for linea in self.init_data["lineas"]:
            del linea["id"]
            del linea["idstock"]
            del linea["ptecalculo"]
            del linea["referenciapack"]

            for field in linea:
                linea[field] = self.format_value(field, linea[field])

        self.set_string_value("datos", self.init_data, max_characters=None, skip_replace=True)
        self.set_string_value("estado", "PTE")
        self.set_string_value("fecha", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameFechaActual())
        self.set_string_value("hora", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameHoraActual())

        self.set_string_relation("codtienda", "cabecera//codalmacen")
        self.set_string_relation("idsincro", "cabecera//idsincro")

        return True

    def format_value(self, field, value):
        if value is None:
            return ""

        if field in ("fecha", "fechasincro", "hora", "fechaenvio", "horaenvio"):
            return str(value)

        if str(value) == "True" or str(value) == "False":
            return str(value).lower()

        return value
