from YBLEGACY import qsatype

from controllers.base.magento2.drivers.magento2 import Magento2Driver
from controllers.base.default.controllers.recieve_sync import RecieveSync
from controllers.api.b2b.customerrequest.serializers.eg_customerrequest_serializer import EgB2bCustomerrequestSerializer


class EgB2bCustomerrequestRecieve(RecieveSync):

    def __init__(self, params=None):
        super().__init__("mgb2bcustomerrequest", params)

    def sync(self):
        data = self.get_customerrequest_serializer().serialize(self.params["customer"])

        if not data:
            return {"data": {"log": "Error al obtener los datos de la solicitud"},
                "status": 500
            }

        if "codigoweb" not in data or not data["codigoweb"] or data["codigoweb"] == "":
            return {"data": {"log": "Error. Código web no informado"},
                    "status": 500
                }

        if "estado" not in data or not data["estado"] or data["estado"] == "":
            return {"data": {"log": "Error. Error al obtener el estado"},
                    "status": 500
                }

        if "nombre" not in data or not data["nombre"] or data["nombre"] == "":
            return {"data": {"log": "Error. Nombre no informado"},
                    "status": 500
                }

        if "cifnif" not in data or not data["cifnif"] or data["cifnif"] == "":
            return {"data": {"log": "Error. Cif/Nif no informado"},
                    "status": 500
                }

        if "email" not in data or not data["email"] or data["email"] == "":
            return {"data": {"log": "Error. Email no informado"},
                    "status": 500
                }

        if "direccion" not in data or not data["direccion"] or data["direccion"] == "":
            return {"data": {"log": "Error. Dirección no informada"},
                    "status": 500
                }
        if "codpostal" not in data or not data["codpostal"] or data["codpostal"] == "":
            return {"data": {"log": "Error. Cod. Postal no informado"},
                    "status": 500
                }

        if "ciudad" not in data or not data["ciudad"] or data["ciudad"] == "":
            return {"data": {"log": "Error. Ciudad no informada"},
                    "status": 500
                }

        if "provincia" not in data or not data["provincia"] or data["provincia"] == "":
            return {"data": {"log": "Error. Provincia no informada"},
                    "status": 500
                }

        if "pais" not in data or not data["pais"] or data["pais"] == "":
            return {"data": {"log": "Error. Pais no informado"},
                    "status": 500
                }

        if "dirtipovia" not in data or not data["dirtipovia"] or data["dirtipovia"] == "":
            return {"data": {"log": "Error. Dir tipo vía no informado"},
                    "status": 500
                }    

        if "dirotros" not in data or not data["dirotros"] or data["dirotros"] == "":
            return {"data": {"log": "Error. Dir otros no informado"},
                    "status": 500
                }
                    

        if not qsatype.FLUtil.execSql("INSERT INTO solicitudescliente (codigoweb,estado,nombre,cifnif,email,telefono,direccion,codpostal,ciudad,provincia,pais,codcliente,fechaalta,horaalta,dirtipovia,dirotros) VALUES ('" + str(data["codigoweb"]) + "', '" + str(data["estado"]) + "', '" + str(data["nombre"]) + "', '" + str(data["cifnif"]) + "', '" + str(data["email"]) + "', '" + str(data["telefono"]) + "', '" + str(data["direccion"]) + "', '" + str(data["codpostal"]) + "', '" + str(data["ciudad"]) + "', '" + str(data["provincia"]) + "', '" + str(data["pais"]) + "', NULL, '" + str(data["fechaalta"]) + "', '" + str(data["horaalta"]) + "', '" + str(data["dirtipovia"]) + "', '" + str(data["dirotros"]) + "')"):
                return {"data": {"log": "Error al hacer el insert de la solicitud"},
                    "status": 500
                }

        return {"data": {"log": "Sincronizado con éxito"},
                "status": 200
                }

    def get_customerrequest_serializer(self):
        return EgB2bCustomerrequestSerializer()