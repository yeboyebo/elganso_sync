from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgShippingLabel(DefaultSerializer):

    def get_data(self):

        metodoEnvio = str(self.init_data["shipping_method"])
        transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")
        self.set_string_relation("codcomanda", "codcomanda")
        self.set_string_value("transportista", transIDL)
        self.set_string_value("shippinglabel", str(self.init_data["shipping_label"]), max_characters=1000000)

        return True
