from YBLEGACY import qsatype
from YBLEGACY.constantes import *
import time

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class EgB2bCustomerrequestSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_value("codigoweb", self.init_data["codigoweb"])
        self.set_string_value("nombre", self.init_data["firstname"] + " " + self.init_data["lastname"])
        self.set_string_value("estado", "Pendiente")
        self.set_string_value("cifnif", self.init_data["taxvat"])
        self.set_string_value("email", self.init_data["email"])
        self.set_string_value("provincia", self.init_data["addresses"][0]["region"]["region"])
        self.set_string_value("pais", self.init_data["addresses"][0]["countryId"])
        self.set_string_value("telefono", self.init_data["addresses"][0]["telephone"])
        self.set_string_value("ciudad", self.init_data["addresses"][0]["city"])
        self.set_string_value("codpostal", self.init_data["addresses"][0]["postcode"])
        self.set_string_value("direccion", self.init_data["addresses"][0]["street"][0])
        # self.set_string_value("dirnum", self.init_data["addresses"][0]["street"][1])
        # self.set_string_value("dirotros", self.init_data["addresses"][0]["street"][2])
        self.set_string_value("fechaalta", time.strftime("%y/%m/%d"))
        self.set_string_value("horaalta", time.strftime("%H:%M:%S"))

        return True