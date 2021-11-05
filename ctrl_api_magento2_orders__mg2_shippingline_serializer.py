from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2ShippingLineSerializer(DefaultSerializer):

    def get_data(self):
        street = self.init_data["shipping_address"]["street"].split("\n")
        dirtipoviaenv = street[0] if len(street) >= 1 else ""
        direccionenv = street[1] if len(street) >= 2 else ""
        dirnumenv = street[2] if len(street) >= 3 else ""
        dirotrosenv = street[3] if len(street) >= 4 else ""

        self.set_string_value("mg_dirtipoviaenv", dirtipoviaenv, max_characters=100)
        self.set_string_value("mg_direccionenv", direccionenv, max_characters=200)
        self.set_string_value("mg_dirnumenv", dirnumenv, max_characters=100)
        self.set_string_value("mg_dirotrosenv", dirotrosenv, max_characters=100)

        self.set_string_relation("mg_numseguimiento", "tracking_number", max_characters=100)
        self.set_string_relation("mg_numcliente", "customer_id", max_characters=15)
        self.set_string_relation("mg_email", "email", max_characters=200)
        self.set_string_relation("mg_metodopago", "payment_method", max_characters=30)
        self.set_string_relation("mg_metodoenvio", "shipping_description", max_characters=500)

        self.set_data_relation("mg_unidadesenv", "units")

        tasaconv = self.init_data["tasaconv"]

        shippingprice = round(parseFloat(self.init_data["shipping_price"] * tasaconv), 2)
        self.set_data_value("mg_gastosenv", shippingprice)
        # self.set_data_relation("mg_gastosenv", "shipping_price")

        self.set_string_relation("mg_nombreenv", "shipping_address//firstname", max_characters=100)
        self.set_string_relation("mg_apellidosenv", "shipping_address//lastname", max_characters=200)
        self.set_string_relation("mg_codpostalenv", "shipping_address//postcode", max_characters=10)
        self.set_string_relation("mg_ciudadenv", "shipping_address//city", max_characters=100)
        self.set_string_relation("mg_paisenv", "shipping_address//country_id", max_characters=100)
        self.set_string_relation("mg_provinciaenv", "shipping_address//region", max_characters=100)
        self.set_string_relation("mg_telefonoenv", "shipping_address//telephone", max_characters=30)

        self.set_data_value("mg_confac", False)

        if self.init_data["shipping_method"].startswith("pl_store_pickup"):
            self.set_string_relation("mg_telefonoenv", "billing_address//telephone", max_characters=30)

        return True
