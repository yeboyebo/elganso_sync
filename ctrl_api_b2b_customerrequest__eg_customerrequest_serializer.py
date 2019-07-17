from YBLEGACY import qsatype
from YBLEGACY.constantes import *
import time

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class EgB2bCustomerrequestSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_value("codigoweb", self.init_data["codigoweb"])
        self.set_string_value("nombre", self.init_data["nombre"])
        self.set_string_value("email", self.init_data["email"])
        self.set_string_value("cifnif", self.init_data["cifnif"])
        self.set_string_value("telefono", self.init_data["telefono"])
        self.set_string_value("dirtipovia", self.init_data["dirtipovia"])
        self.set_string_value("direccion", self.init_data["direccion"])
        self.set_string_value("dirotros", self.init_data["dirotros"])
        self.set_string_value("codpostal", self.init_data["codpostal"])
        self.set_string_value("ciudad", self.init_data["ciudad"])
        self.set_string_value("provincia", self.init_data["provincia"])
        self.set_string_value("pais", self.init_data["pais"])
        self.set_string_value("estado", "Pendiente")
        self.set_string_value("fechaalta", time.strftime("%y/%m/%d"))
        self.set_string_value("horaalta", time.strftime("%H:%M:%S"))

        return True