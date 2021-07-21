from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SpecialPriceSerializer(DefaultSerializer):

    def get_data(self):

        referencia = str(self.init_data["at.referencia"]) + "-" + str(self.init_data["at.talla"])
        if str(self.init_data["at.talla"]) == "TU":
            referencia = str(self.init_data["at.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_relation("price", "ap.pvp")
        self.set_string_value("store_id", "0")
        self.set_string_relation("price_from", "p.desde || ' ' || p.horadesde")
        self.set_string_relation("price_to", "p.hasta || ' ' || p.horahasta")

        return True
