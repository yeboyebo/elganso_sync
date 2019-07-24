from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgMovistockSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("referencia", "referencia")
        self.set_string_relation("barcode", "barcode")
        self.set_string_value("estado", "PTE")
        self.set_string_relation("cantidad", "cantidad")
        self.set_string_value("concepto", "DEVOLUCION " + self.init_data["codcomanda"])
        self.set_string_value("idstock", self.get_idstock())

        return True

    def get_idstock(self):
        idStock = str(qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "barcode = '" + str(self.data["barcode"]) + "' AND codalmacen = 'AWEB'"))

        if not idStock or idStock == "None":
            raise NameError("No se encontró el stock para el artículo {} en el almacén AWEB".format(str(self.data["barcode"])))

        return idStock