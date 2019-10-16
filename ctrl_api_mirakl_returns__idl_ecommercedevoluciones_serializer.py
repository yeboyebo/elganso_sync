from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class IdlEcommerceDevolucionesSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("codcomanda", "codcomanda")
        self.set_string_value("tipo", "DEVOLUCION")
        self.set_data_value("envioidl", False)
        self.set_data_value("confirmacionrecepcion", "No")
        self.set_string_value("informadomagento", False)
        self.set_data_value("eseciweb", True)
        self.set_data_value("excluirenvioidl", False)
        self.set_string_value("codtiendaentrega", "NULL")

        return True
