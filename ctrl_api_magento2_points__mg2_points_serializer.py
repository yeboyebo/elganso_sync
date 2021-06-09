from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer

class Mg2PointsSerializer(DefaultSerializer):

    def get_data(self):
        existe_tarjeta = qsatype.FLUtil.sqlSelect("tpv_tarjetaspuntos", "codtarjetapuntos", "email = '" + str(self.init_data["email"]) + "'")

        if existe_tarjeta:
            raise NameError("La tarjeta con email " + str(self.init_data["email"]) + " ya existe en la BBDD.")
            return False

        codtarjeta = self.get_codtarjeta("AWEB")
        self.set_data_value("activa", True)
        self.set_string_value("nombre", str(self.init_data["nombre"]))
        self.set_data_value("sincronizada", True)
        self.set_string_value("telefono", str(self.init_data["telefono"]))
        self.set_string_value("email", str(self.init_data["email"]))
        if str(self.init_data["cifnif"]) == "None":
            self.set_string_value("cifnif", "-")
        else:
            self.set_string_value("cifnif", str(self.init_data["cifnif"]))
        self.set_string_value("direccion", str(self.init_data["direccion"]))
        self.set_string_value("provincia", str(self.init_data["provincia"]))
        self.set_string_value("ciudad", str(self.init_data["ciudad"]))
        self.set_string_value("codpais", str(self.init_data["codpais"]))
        if str(self.init_data["genero"]) == "1":
            self.set_string_value("sexo", "Masculino")
        elif str(self.init_data["genero"]) == "1":
            self.set_string_value("sexo", "Femenino")
        else:
            self.set_string_value("sexo", "-")

        self.set_string_value("codtarjetapuntos", str(codtarjeta))
        self.set_string_value("codbarrastarjeta", str(codtarjeta))
        self.set_string_value("fechaalta", str(qsatype.Date())[:10])
        self.set_string_value("horaalta", str(qsatype.Date())[-8:])
        self.set_string_value("fechamod", str(qsatype.Date())[:10])
        self.set_string_value("horamod", str(qsatype.Date())[-8:])
        self.set_string_value("idusuariomod", str("sincro"))
        self.set_string_value("idusuarioalta", str("sincro"))

        return True

    def get_codtarjeta(self, prefijo):

        idUltima = qsatype.FLUtil.sqlSelect(u"tpv_tarjetaspuntos", u"codtarjetapuntos", ustr(u"codtarjetapuntos LIKE '", prefijo, u"%' ORDER BY codtarjetapuntos DESC LIMIT 1"))
        if idUltima:
            ultimaTarjeta = int(idUltima[4:])
        else:
            ultimaTarjeta = 0

        ultimaTarjeta += 1
        codigo = prefijo + qsatype.FactoriaModulos.get('flfacturac').iface.pub_cerosIzquierda(ultimaTarjeta, 15 - len(prefijo))
        return codigo

