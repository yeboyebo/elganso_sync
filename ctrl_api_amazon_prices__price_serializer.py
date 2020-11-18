from controllers.base.default.serializers.default_serializer import DefaultSerializer


class PriceSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("Price//SKU", "aa.barcode")

        tarifa = None
        if self.init_data["at.pvp"]:
            tarifa = float(self.init_data["at.pvp"])

        if not tarifa or tarifa == 0 or tarifa == 0.0:
            tarifa = float(self.init_data["a.pvp"])

        self.set_data_value("Price//StandardPrice//xml_node_value", tarifa)
        self.set_string_value("Price//StandardPrice//@currency", "EUR")

        if self.init_data["pp.desde"] and self.init_data["pp.hasta"] and self.init_data["app.pvp"] and self.init_data["pp.horadesde"] and self.init_data["pp.horahasta"]:
            self.set_string_value("Price//Sale//StartDate", "{}T{}".format(self.init_data["pp.desde"], self.init_data["pp.horadesde"]))
            self.set_string_value("Price//Sale//EndDate", "{}T{}".format(self.init_data["pp.hasta"], self.init_data["pp.horahasta"]))

            self.set_data_relation("Price//Sale//SalePrice//xml_node_value", "app.pvp")
            self.set_string_value("Price//Sale//SalePrice//@currency", "EUR")

        return True
