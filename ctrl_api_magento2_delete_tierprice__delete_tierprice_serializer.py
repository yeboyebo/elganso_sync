from controllers.base.default.serializers.default_serializer import DefaultSerializer


class DeleteTierpriceSerializer(DefaultSerializer):

    def get_data(self):
        referencia = str(self.init_data["referencia"]) + "-" + str(self.init_data["talla"])
        if str(self.init_data["talla"]) == "TU":
            referencia = str(self.init_data["referencia"])

        self.set_string_value("sku", referencia)
        self.set_data_relation("price", "pvp")
        self.set_data_relation("website_id", "website")
        self.set_data_relation("customer_group", "codgrupo")
        self.set_string_value("price_type", "fixed")
        self.set_data_value("quantity", 1)

        return True
