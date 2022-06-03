from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class Mg2LineasDevolucionesWebTienda(DefaultSerializer):

    def get_data(self):
        if not self.init_data["codtiendaentrega"] or str(self.init_data["codtiendaentrega"]) == "" or str(self.init_data["codtiendaentrega"]) == "None" or self.init_data["codtiendaentrega"] == None:
            raise NameError("Error. Almacén de la línea incorrecto {}".format(str(self.init_data["codtiendaentrega"])))
            return False

        self.set_string_value("codalmacen", str(self.init_data["codtiendaentrega"]))
        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)
        self.set_string_value("viajecreado", False)
        self.set_string_value("correoenviado", False)
        self.set_string_value("devolucionrecibida", False)

        return True
