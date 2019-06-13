from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class EgMagentoCustomerSerializer(DefaultSerializer):

    def get_data(self):
        sexo = "Masculino" if self.init_data["gender"] == 1 else "Femenino" if self.init_data["gender"] == 2 else None

        now = str(qsatype.Date())
        current_date = now[:10]
        current_time = now[-(8):]

        self.set_string_relation("email", "email")
        self.set_string_relation("cifnif", "taxvat")
        self.set_string_relation("nombre", "firstname")
        self.set_string_relation("apellidos", "lastname")
        self.set_string_relation("codwebsite", "website_id")
        self.set_string_relation("suscrito", "suscribed")

        self.set_string_value("sexo", sexo)

        self.set_string_value("idusuariomod", "sincro")
        self.set_string_value("fechamod", current_date)
        self.set_string_value("horamod", current_time)

        self.set_string_value("idusuarioalta", "sincro")
        self.set_string_value("fechaalta", current_date)
        self.set_string_value("horaalta", current_time)

        if self.init_data["dob"] and self.init_data["dob"] != "" and self.init_data["dob"] is not None:
            self.set_string_relation("fechanacimiento", "dob", max_characters=10)
        else:
            self.set_data_value("fechanacimiento", None)

        if self.init_data["billing_address"]:
            self.set_string_relation("nombrefac", "billing_address//firstname")
            self.set_string_relation("apellidosfac", "billing_address//lastname")
            self.set_string_relation("telefonofac", "billing_address//telephone")
            self.set_string_relation("direccionfac", "billing_address//street")
            self.set_string_relation("codpostalfac", "billing_address//postcode")
            self.set_string_relation("ciudadfac", "billing_address//city")
            self.set_string_relation("provinciafac", "billing_address//region")
            self.set_string_relation("paisfac", "billing_address//country_id")

        if self.init_data["shipping_address"]:
            self.set_string_relation("nombreenv", "shipping_address//firstname")
            self.set_string_relation("apellidosenv", "shipping_address//lastname")
            self.set_string_relation("telefonoenv", "shipping_address//telephone")
            self.set_string_relation("direccionenv", "shipping_address//street")
            self.set_string_relation("codpostalenv", "shipping_address//postcode")
            self.set_string_relation("ciudadenv", "shipping_address//city")
            self.set_string_relation("provinciaenv", "shipping_address//region")
            self.set_string_relation("paisenv", "shipping_address//country_id")

        return True
