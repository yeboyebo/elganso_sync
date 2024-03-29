from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SimplePrerebajasSerializer(DefaultSerializer):

    def get_data(self):

        referencia = self.get_init_value("at.referencia") + "-" + self.get_init_value("at.talla")
        if self.get_init_value("at.talla") == "TU":
            referencia = self.get_init_value("at.referencia")

        self.set_string_value("sku", referencia)
        self.set_string_value("yeboyebo_carrito_promociones_precio", self.get_init_value("pr.pvp"))
        self.set_string_value("yeboyebo_carrito_promociones_fecha_hasta", self.get_init_value("pr.desde"))
        self.set_string_value("store_id", self.get_init_value("mg.idmagento"))

        return True