from controllers.base.default.serializers.default_serializer import DefaultSerializer


class PriceSerializer(DefaultSerializer):

    def get_data(self):
        idobjeto = str(self.init_data["ls.idobjeto"]).split("-")
        referencia = str(idobjeto[0])
        talla = str(idobjeto[1])
        precio = str(idobjeto[2])
        idstore = str(idobjeto[3])

        if talla != "TU":
            referencia = referencia + "-" + talla

        self.set_string_value("sku", referencia)
        self.set_string_value("price", precio)
        self.set_string_value("store_id", idstore)

        return True
