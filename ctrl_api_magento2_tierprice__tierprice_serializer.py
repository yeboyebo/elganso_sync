from controllers.base.default.serializers.default_serializer import DefaultSerializer


class TierpriceSerializer(DefaultSerializer):

    def get_data(self):
        referencia = str(self.init_data["at.referencia"]) + "-" + str(self.init_data["at.talla"])
        if str(self.init_data["at.talla"]) == "TU":
            referencia = str(self.init_data["at.referencia"])

        self.set_string_value("sku", referencia)
        self.set_data_relation("price", "ap.pvp")
        self.set_data_relation("website_id", "mg.idmagento")
        self.set_string_value("customer_group", "General")
        self.set_string_value("price_type", "fixed")
        self.set_data_value("quantity", 1)

        return True
