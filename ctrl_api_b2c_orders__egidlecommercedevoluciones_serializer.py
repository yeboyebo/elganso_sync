from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgIdlEcommerceDevoluciones(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)
        self.set_string_value("tipo", 'DEVOLUCION')
        self.set_data_value("envioidl", False)
        self.set_data_value("informadomagento", False)
        self.set_string_value("confirmacionrecepcion", 'No')
        self.set_data_value("excluirenvioidl", False)
        self.set_string_value("codtiendaentrega", "AWEB")

        return True
