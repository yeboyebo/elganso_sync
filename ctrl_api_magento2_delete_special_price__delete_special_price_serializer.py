from controllers.base.default.serializers.default_serializer import DefaultSerializer
from datetime import datetime, timedelta

class DeleteSpecialPriceSerializer(DefaultSerializer):

    def get_data(self):

        referencia = str(self.init_data["at.referencia"]) + "-" + str(self.init_data["at.talla"])
        if str(self.init_data["at.talla"]) == "TU":
            referencia = str(self.init_data["at.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_relation("price", "ap.pvp")
        self.set_string_relation("store_id", "mg.idmagento")
        self.set_string_relation("price_from", "p.desde || ' ' || p.horadesde")

        if self.init_data["ap.activo"] == True:
            self.set_string_relation("price_to", "p.hasta || ' ' || p.horahasta")
        else:
            ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            self.set_string_value("price_to", ayer)
        return True
