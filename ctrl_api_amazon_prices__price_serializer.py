from controllers.base.default.serializers.default_serializer import DefaultSerializer


class PriceSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("Price//SKU", "aa.barcode")
        # if self.init_data["aa.barcode"] == '8445005225577':
        #     self.set_string_value("Price//SKU", "1050s200003-XXL")
        # elif self.init_data["aa.barcode"] == '8445005225546':
        #     self.set_string_value("Price//SKU", "1050s200003-S")
        # elif self.init_data["aa.barcode"] == '8445005225553':
        #     self.set_string_value("Price//SKU", "1050s200003-L")
        # elif self.init_data["aa.barcode"] == '8445005225560':
        #     self.set_string_value("Price//SKU", "1050s200003-XL")

        tarifa = float(self.init_data["at.pvp"])

        if not tarifa or tarifa == 0 or tarifa == 0.0:
            tarifa = float(self.init_data["a.pvp"])

        self.set_data_relation("Price//StandardPrice//xml_node_value", tarifa)
        self.set_string_value("Price//StandardPrice//@currency", "EUR")

        # Aqui va la oferta
        # self.set_string_relation("Price//Sale//StartDate", fechaInicio)
        # self.set_string_relation("Price//Sale//EndDate", fechaFin)
        # self.set_data_relation("Price//Sale//SalePrice", precioOferta)

        return True
