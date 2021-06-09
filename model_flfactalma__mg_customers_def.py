# @class_declaration interna #
from YBLEGACY import qsatype


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
from YBLEGACY.constantes import *
from models.flsyncppal import flsyncppal_def as syncppal


class elganso_sync(interna):

    params = syncppal.iface.get_param_sincro('apipass')

    def elganso_sync_getDesc(self):
        return None

    def elganso_sync_mg2customer(self, params):
        try:
            if "auth" not in self.params:
                self.params = syncppal.iface.get_param_sincro('apipass')
            if "passwd" in params and params['passwd'] == self.params['auth']:

                if "email" not in params:
                    return {"Error": "Formato Incorrecto. No viene informado el parametro customer", "status": 0}

                if not self.crearClienteMagento2(params):
                    return False

                return True
            else:
                return {"Error": "Petición Incorrecta", "status": 10}
        except Exception as e:
            print(e)
            qsatype.debug(ustr(u"Error inesperado", e))
            return {"Error": "Petición Incorrecta", "status": 0}
        return False

    def elganso_sync_crearClienteMagento2(self, params):

        curCustomer = qsatype.FLSqlCursor("mg_customers")
        curCustomer.select("email = '" + params["email"] + "'")
        if curCustomer.first():
            curCustomer.setModeAccess(curCustomer.Edit)
            curCustomer.setActivatedCommitActions(False)
            curCustomer.refreshBuffer()
        else:
            curCustomer.setModeAccess(curCustomer.Insert)
            curCustomer.setActivatedCommitActions(False)
            curCustomer.refreshBuffer()

        sexo = "Masculino" if params["gender"] == 1 else "Femenino" if params["gender"] == 2 else None

        now = str(qsatype.Date())
        current_date = now[:10]
        current_time = now[-(8):]

        curCustomer.setValueBuffer("email", params["email"])
        curCustomer.setValueBuffer("cifnif", params["taxvat"])
        curCustomer.setValueBuffer("nombre", params["firstname"])
        curCustomer.setValueBuffer("apellidos", params["lastname"])
        curCustomer.setValueBuffer("codwebsite", params["website_id"])
        curCustomer.setValueBuffer("suscrito", params["extension_attributes"]["is_subscribed"])
        curCustomer.setValueBuffer("sexo", sexo)
        curCustomer.setValueBuffer("idusuariomod", "sincro")
        curCustomer.setValueBuffer("fechamod", current_date)
        curCustomer.setValueBuffer("horamod", current_time)
        curCustomer.setValueBuffer("idusuarioalta", "sincro")
        curCustomer.setValueBuffer("fechaalta", current_date)
        curCustomer.setValueBuffer("horaalta", current_time)

        if params["dob"] and params["dob"] != "" and params["dob"] is not None:
            curCustomer.setValueBuffer("fechanacimiento", params["dob"])

        for idx in range(len(params["addresses"])):
            if params["addresses"][idx]["default_billing"]:
                curCustomer.setValueBuffer("nombrefac", params["addresses"][idx]["firstname"])
                curCustomer.setValueBuffer("apellidosfac", params["addresses"][idx]["lastname"])
                curCustomer.setValueBuffer("telefonofac", params["addresses"][idx]["telephone"])
                curCustomer.setValueBuffer("direccionfac", params["addresses"][idx]["street"][0])
                curCustomer.setValueBuffer("codpostalfac", params["addresses"][idx]["postcode"])
                curCustomer.setValueBuffer("ciudadfac", params["addresses"][idx]["city"])
                curCustomer.setValueBuffer("provinciafac", params["addresses"][idx]["region"]["region"])
                curCustomer.setValueBuffer("paisfac", params["addresses"][idx]["country_id"])

            if params["addresses"][idx]["default_shipping"]:
                curCustomer.setValueBuffer("nombreenv", params["addresses"][idx]["firstname"])
                curCustomer.setValueBuffer("apellidosenv", params["addresses"][idx]["lastname"])
                curCustomer.setValueBuffer("telefonoenv", params["addresses"][idx]["telephone"])
                curCustomer.setValueBuffer("direccionenv", params["addresses"][idx]["street"][0])
                curCustomer.setValueBuffer("codpostalenv", params["addresses"][idx]["postcode"])
                curCustomer.setValueBuffer("ciudadenv", params["addresses"][idx]["city"])
                curCustomer.setValueBuffer("provinciaenv", params["addresses"][idx]["region"]["region"])
                curCustomer.setValueBuffer("paisenv", params["addresses"][idx]["country_id"])

        if not curCustomer.commitBuffer():
            return False

        return True

    def __init__(self, context=None):
        super().__init__(context)

    def getDesc(self):
        return self.ctx.elganso_sync_getDesc()

    def mg2customer(self, params):
        return self.ctx.elganso_sync_mg2customer(params)

    def crearClienteMagento2(self, params):
        return self.ctx.elganso_sync_crearClienteMagento2(params)


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
