from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class Mg2LineaEcommerceExcluidaSerializer(DefaultSerializer):

    def get_data(self):

        if not self.init_data["almacen"] or str(self.init_data["almacen"]) == "" or str(self.init_data["almacen"]) == "None" or self.init_data["almacen"] == None:
            raise NameError("Error. Almacén de la línea incorrecto {}".format(str(self.init_data["almacen"])))
            return False

        if not self.init_data["emailtienda"] or str(self.init_data["emailtienda"]) == "" or str(self.init_data["emailtienda"]) == "None" or self.init_data["emailtienda"] == None:
            raise NameError("Error. Email de la tienda incorrecto {}".format(str(self.init_data["almacen"])))
            return False

        self.set_string_value("codalmacen", str(self.init_data["almacen"]))
        self.set_string_value("email", str(self.init_data["emailtienda"]))
        # self.set_string_value("codalmacen", 'AWEB')
        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)
        self.set_string_value("viajecreado", False)
        self.set_string_value("correoenviado", False)

        return True
