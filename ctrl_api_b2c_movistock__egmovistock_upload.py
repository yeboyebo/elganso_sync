from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.controllers.upload_sync import UploadSync


class EgMovistockUpload(UploadSync):

    _smsw = None

    def __init__(self, driver, params=None):
        super().__init__("mgsyncmovistock", driver, params)

        self.set_sync_params(self.get_param_sincro('b2c'))
        self.set_sync_params(self.get_param_sincro('b2cMovistockUpload'))

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("smw.referencia, smw.talla, smw.cantidad, smw.id, smw.idstock, s.codalmacen")
        q.setFrom("eg_sincromovistockweb  smw INNER JOIN stocks s ON smw.idstock = s.idstock")
        q.setWhere("NOT smw.sincronizado OR smw.sincronizado = false ORDER BY smw.referencia LIMIT 25")

        q.exec_()

        body = []
        if not q.size():
            return body

        while q.next():
            sku = self.dame_sku(q.value("smw.referencia"), q.value("smw.talla"))
            cant_disponible = parseInt(q.value("cantidad"))
            hoy = qsatype.Date()
            
            aListaAlmacenes = self.dame_almacenessincroweb().split(",")
            if q.value("s.codalmacen") not in aListaAlmacenes:
                raise NameError("Error. Existe un registro cuyo almacén no está en la lista de almacenes de sincronización con Magento. " + str(q.value("ssw.idssw")))


            body.append({"sku": sku, "qty": cant_disponible, "almacen": q.value("s.codalmacen")})

            if not self._smsw:
                self._smsw = ""
            else:
                self._smsw += ","
            self._smsw += str(q.value("smw.id"))

        return body

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE eg_sincromovistockweb SET sincronizado = true WHERE id IN ({})".format(self._smsw))

        qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'MOVISTOCK_WEB'".format(self.start_date, self.start_time))

        self.log("Exito", "Movistocks sincronizados correctamente ({})".format(self._smsw))
        
        return self.small_sleep

    def dame_sku(self, referencia, talla):
        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def dame_almacenessincroweb(self):
        listaAlmacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'")
        if not listaAlmacenes or listaAlmacenes == "" or str(listaAlmacenes) == "None" or listaAlmacenes == None:
            return "AWEB"

        return listaAlmacenes

