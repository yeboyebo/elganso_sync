from controllers.base.default.serializers.default_serializer import DefaultSerializer


class StockIncrementalSerializer(DefaultSerializer):

    def get_data(self):

        referencia = str(self.init_data["ssw.referencia"]) + "-" + str(self.init_data["ssw.talla"])
        if str(self.init_data["ssw.talla"]) == "TU":
            referencia = str(self.init_data["ssw.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_value("source_code", str(self.init_data["s.codalmacen"]))
        self.set_string_value("qty", self.init_data["ssw.cantidad"])

        return True
