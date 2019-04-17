from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.sync.base.aqsync_upload import AQSyncUpload


class EgStockUpload(AQSyncUpload):

    _ssw = None

    def __init__(self, driver, params=None):
        super().__init__("mgsyncstock", driver, params)

        self.set_sync_params({
            "auth": "Basic c2luY3JvOmJVcWZxQk1ub0g=",
            "test_auth": "Basic dGVzdDp0ZXN0",
            "url": "https://www.elganso.com/syncapi/index.php/productupdates",
            "test_url": "http://local2.elganso.com/syncapi/index.php/productupdates",
            "success_code": 202
        })

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("aa.referencia, aa.talla, aa.barcode, s.disponible, ssw.idssw")
        q.setFrom("articulos a INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON (aa.barcode = s.barcode AND s.codalmacen = 'AWEB') LEFT OUTER JOIN eg_sincrostockweb ssw ON s.idstock = ssw.idstock")
        q.setWhere("NOT ssw.sincronizado OR ssw.sincronizado = false ORDER BY aa.referencia LIMIT 25")

        q.exec_()

        body = []
        if not q.size():
            return body

        while q.next():
            sku = self.dame_sku(q.value("aa.referencia"), q.value("aa.talla"))
            qty = parseInt(self.dame_stock(q.value("s.disponible")))

            body.append({"sku": sku, "qty": qty, "sincroStock": True})

            if not self._ssw:
                self._ssw = ""
            else:
                self._ssw += ","
            self._ssw += str(q.value("ssw.idssw"))

        return body

    def dame_sku(self, referencia, talla):
        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def dame_stock(self, disponible):
        if not disponible or isNaN(disponible) or disponible < 0:
            return 0

        return disponible

    def after_sync(self, response_data=None):
        if response_data and "request_id" in response_data:
            qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = true WHERE idssw IN ({})".format(self._ssw))
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'STOCK_WEB'".format(self.start_date, self.start_time))
            self.log("Éxito", "Stock sincronizado correctamente (id: {})".format(response_data["request_id"]))
        else:
            raise NameError("No se recibió una respuesta correcta del servidor")

        return self.small_sleep
