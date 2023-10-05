from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SimplePrerebajasSerializer(DefaultSerializer):

    def get_data(self):


        self.set_string_value("product//sku", self.get_init_value("sku"))


        custom_attributes = [
            {"attribute_code": "yeboyebo_carrito_promociones_precio", "value": self.get_init_value("pvp")},
            {"attribute_code": "yeboyebo_carrito_promociones_fecha_hasta", "value": self.get_init_value("desde")}
        ]


        self.set_data_value("product//custom_attributes", custom_attributes)

        return True