from controllers.base.default.serializers.default_serializer import DefaultSerializer


class InventorySerializer(DefaultSerializer):

    def get_data(self):

        referencia = str(self.init_data["aa.referencia"]) + "-" + str(self.init_data["aa.talla"])
        if str(self.init_data["aa.talla"]) == "TU":
            referencia = str(self.init_data["aa.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_value("source_code", str(self.init_data["s.codalmacen"]))
        status = 0
        disponible = self.init_data["s.disponible"]
        if self.init_data["s.disponible"] > 0:
            status = 1
        # else:
            # status = 0
            # disponible = 0

        self.set_string_value("quantity", disponible)
        self.set_string_value("status", status)
        return True
