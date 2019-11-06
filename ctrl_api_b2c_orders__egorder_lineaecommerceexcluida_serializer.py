from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class EgLineaEcommerceExcluida(DefaultSerializer):

    def get_data(self):

        if not self.init_data["almacen"] or str(self.init_data["almacen"]) == "" or str(self.init_data["almacen"]) == "None" or self.init_data["almacen"] == None:
            return False

        self.set_string_value("codalmacen", str(self.init_data["almacen"]))
        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)
        self.set_string_value("viajecreado", False)

        return True