from controllers.base.default.serializers.default_serializer import DefaultSerializer


class PriceSerializer(DefaultSerializer):

    def get_data(self):

        self.set_string_relation("sku", "at.referencia || '-' || at.talla")
        self.set_string_relation("price", "ap.pvp")
        self.set_string_value("store_id", "0")
        self.set_string_relation("price_from", "p.desde || ' ' || p.horadesde")
        self.set_string_relation("price_to", "p.hasta || ' ' || p.horahasta")

        return True
