from controllers.base.default.serializers.default_serializer import DefaultSerializer


class StockSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("Inventory//SKU", "aa.barcode")

        disponible = int(self.init_data["s.disponible"])
        reserva = int(self.init_data["p.valor"])

        if disponible and disponible > reserva:
            disponible -= reserva
        else:
            disponible = 0

        self.set_data_value("Inventory//Quantity", disponible)
        self.set_string_value("Inventory//FulfillmentLatency", "1")

        return True
