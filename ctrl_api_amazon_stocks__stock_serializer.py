from controllers.base.default.serializers.default_serializer import DefaultSerializer


class StockSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("Inventory//SKU", "aa.barcode")
        # if self.init_data["aa.barcode"] == '8445005225577':
        #     self.set_string_value("Inventory//SKU", "1050s200003-XXL")
        # elif self.init_data["aa.barcode"] == '8445005225546':
        #     self.set_string_value("Inventory//SKU", "1050s200003-S")
        # elif self.init_data["aa.barcode"] == '8445005225553':
        #     self.set_string_value("Inventory//SKU", "1050s200003-L")
        # elif self.init_data["aa.barcode"] == '8445005225560':
        #     self.set_string_value("Inventory//SKU", "1050s200003-XL")

        disponible = int(self.init_data["s.disponible"])
        reserva = int(self.init_data["p.valor"])

        if disponible and disponible > reserva:
            disponible -= reserva
        else:
            disponible = 0

        self.set_data_value("Inventory//Quantity", disponible)
        self.set_string_value("Inventory//FulfillmentLatency", "1")

        return True
