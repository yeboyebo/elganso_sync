# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
from YBLEGACY.constantes import *
from models.flsyncppal import flsyncppal_def as syncppal
import time

class elganso_sync(interna):

    params = {}

    def elganso_sync_crearsolicitudcliente(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:
                if "customer" not in params:
                    return {"Error": "No viene informado el nodo Customer", "status": 500}

                if "codigoweb" not in params["customer"] or not params["customer"]["codigoweb"] or params["customer"]["codigoweb"] == "":
                    return {"Error": "Codigo WEB no informado", "status": 500}
            
                if "estado" not in params["customer"] or not params["customer"]["estado"] or params["customer"]["estado"] == "":
                    return {"Error": "Estado no informado", "status": 500}

                if "nombre" not in params["customer"] or not params["customer"]["nombre"] or params["customer"]["nombre"] == "":
                    return {"Error": "Nombre no informado", "status": 500}

                if "cifnif" not in params["customer"] or not params["customer"]["cifnif"] or params["customer"]["cifnif"] == "":
                    return {"Error": "Cifnif no informado", "status": 500}

                if "email" not in params["customer"] or not params["customer"]["email"] or params["customer"]["email"] == "":
                    return {"Error": "Email no informado", "status": 500}

                if "direccion" not in params["customer"] or not params["customer"]["direccion"] or params["customer"]["direccion"] == "":
                    return {"Error": "Direccion no informado", "status": 500}

                if "codpostal" not in params["customer"] or not params["customer"]["codpostal"] or params["customer"]["codpostal"] == "":
                    return {"Error": "Codigo Postal no informado", "status": 500}

                if "ciudad" not in params["customer"] or not params["customer"]["ciudad"] or params["customer"]["ciudad"] == "":
                    return {"Error": "Ciudad no informado", "status": 500}

                if "provincia" not in params["customer"] or not params["customer"]["provincia"] or params["customer"]["provincia"] == "":
                    return {"Error": "Provincia no informado", "status": 500}

                if "pais" not in params["customer"] or not params["customer"]["pais"] or params["customer"]["pais"] == "":
                    return {"Error": "Pais no informado", "status": 500}

                if "dirtipovia" not in params["customer"] or not params["customer"]["dirtipovia"] or params["customer"]["dirtipovia"] == "":
                    return {"Error": "Tipo Via no informado", "status": 500} 

                if "dirotros" not in params["customer"] or not params["customer"]["dirotros"] or params["customer"]["dirotros"] == "":
                    return {"Error": "Otros datos de direccion no informado", "status": 500}
                            

                if not qsatype.FLUtil.execSql("INSERT INTO solicitudescliente (codigoweb,estado,nombre,cifnif,email,telefono,direccion,codpostal,ciudad,provincia,pais,codcliente,fechaalta,horaalta,dirtipovia,dirotros) VALUES ('" + str(params["customer"]["codigoweb"]) + "', '" + str("Pendiente") + "', '" + str(params["customer"]["nombre"]) + "', '" + str(params["customer"]["cifnif"]) + "', '" + str(params["customer"]["email"]) + "', '" + str(params["customer"]["telefono"]) + "', '" + str(params["customer"]["direccion"]) + "', '" + str(params["customer"]["codpostal"]) + "', '" + str(params["customer"]["ciudad"]) + "', '" + str(params["customer"]["provincia"]) + "', '" + str(params["customer"]["pais"]) + "', NULL, '" + str(time.strftime("%y/%m/%d")) + "', '" + str(time.strftime("%H:%M:%S")) + "', '" + str(params["customer"]["dirtipovia"]) + "', '" + str(params["customer"]["dirotros"]) + "')"):
                        return {"Error": "No se ha podido realizar el insert", "status": 500}

                return True
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado consulta de bono: ", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_getDesc(self):
        return None

    def __init__(self, context=None):
        super().__init__(context)

    def getDesc(self):
        return self.ctx.elganso_sync_getDesc()

    def crearsolicitudcliente(self, params):
        return self.ctx.elganso_sync_crearsolicitudcliente(params)


# @class_declaration head #
class head(elganso_sync):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super().__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)
