import json

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.sync.base.controllers.aqsync_upload import AQSyncUpload


class EgPricesUpload(AQSyncUpload):

    _fechasincro = None

    def __init__(self, driver, params=None):
        super().__init__("mgsyncprices", driver, params)

        self.set_sync_params({
            "auth": "Basic c2luY3JvOmJVcWZxQk1ub0g=",
            "test_auth": "Basic dGVzdDp0ZXN0",
            "url": "https://www.elganso.com/syncapi/index.php/productupdates",
            "test_url": "http://local2.elganso.com/syncapi/index.php/productupdates",
            "success_code": 202
        })

    def before_sync(self):
        dow = qsatype.FLUtil.sqlSelect("empresa", "EXTRACT(DOW FROM CURRENT_DATE)", "1 = 1 LIMIT 1")

        if (self.start_time > "02:00:00" and self.start_time < "06:00:00" and int(dow) == 1) or self.params["first"]:
            return True

        return False

    def sync(self):
        data = self.get_data()

        if data == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return self.large_sleep

        new_data = []
        for idx in range(len(data)):
            if len(new_data) < 10 or idx == len(data) - 1:
                new_data.append(data[idx])

            if len(new_data) == 10 or idx == len(data) - 1:
                response_data = self.send_request("post", data=json.dumps(new_data))

                if response_data and "request_id" in response_data:
                    self.log("Éxito", "Precios sincronizados correctamente (id: {})".format(response_data["request_id"]))
                    new_data = []
                else:
                    raise NameError("No se recibió una respuesta correcta del servidor")

        return self.after_sync(response_data)

    def get_data(self):
        self._fechasincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro", "codtienda = 'AWEB' AND esquema = 'PRICES_WEB'")
        horasincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "horasincro", "codtienda = 'AWEB' AND esquema = 'PRICES_WEB'")

        if not self._fechasincro or self._fechasincro is None:
            self._fechasincro = "2014-08-01"
        else:
            self._fechasincro = str(self._fechasincro)[:10]

        if not horasincro or horasincro is None:
            horasincro = "00:00:00"
        else:
            horasincro = str(horasincro)[-(8):]

        filtro_fechas_alta = "(a.fechaalta > '{}' OR (a.fechaalta = '{}' AND a.horaalta >= '{}'))".format(self._fechasincro, self._fechasincro, horasincro)
        filtro_fechas_mod = "(a.fechamod > '{}' OR (a.fechamod = '{}' AND a.horamod >= '{}'))".format(self._fechasincro, self._fechasincro, horasincro)
        where = "{} OR {} ORDER BY a.referencia".format(filtro_fechas_alta, filtro_fechas_mod)

        q = qsatype.FLSqlQuery()
        q.setSelect("a.referencia, a.pvp, a.codtarifa, st.codwebsite, st.codstoreview")
        q.setFrom("mg_websites w inner join mg_storeviews st on w.codwebsite = st.codwebsite inner join articulostarifas a on a.codtarifa = st.codtarifa")
        q.setWhere(where)

        q.exec_()

        body = []
        if not q.size():
            return body

        while q.next():
            sku = q.value("a.referencia")
            price = parseFloat(q.value("a.pvp"))
            store_id = q.value("st.codstoreview")
            website = q.value("st.codwebsite")

            body.append({"sku": sku, "price": price, "sincroPrecios": True, "auto": True, "store_id": store_id, "website": website})

        return body

    def after_sync(self, response_data=None):
        if self._fechasincro != "2014-08-01":
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'PRICES_WEB'".format(self.start_date, self.start_time))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('AWEB', 'PRICES_WEB', '{}', '{}')".format(self.start_date, self.start_time))

        return self.small_sleep
