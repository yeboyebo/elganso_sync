from YBLEGACY import qsatype
import requests
import json
from controllers.base.magento2.price.controllers.price_upload import PriceUpload
from controllers.api.magento2.price.serializers.price_serializer import PriceSerializer

class Mg2PriceUpload(PriceUpload):

    codwebsite = None
    referencia = None
    idArticulo = None
    fechasincro = None
    start_date = None
    start_time = None
    error = False
    refSincros = None

    def __init__(self, params=None):
        super().__init__("mg2price", params)

        price_params = self.get_param_sincro('mg2PricesUpload')
        self.price_url = price_params['url']
        self.price_test_url = price_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 10
        self.large_sleep = 180
        self.no_sync_sleep = 300


    def get_data(self):

        data = self.get_db_data()
        price_url = self.price_url if self.driver.in_production else self.price_test_url
        if data == []:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'PRICES_WEB'".format(self.start_date, self.start_time))
            self.log("Éxito", "No hay datos que sincronizar")
            return data

        referencia = ""
        refConsulta = ""
        tarifaConsulta = ""
        self.refSincros = ""
        for idx in range(len(data)):
            if idx == 0:
                refConsulta = str(data[idx]["at.referencia"])
                tarifaConsulta = str(data[idx]["a.codtarifa"])
                self.refSincros = refConsulta

            self.codwebsite = data[idx]["st.codstoreview"]
            self.idArticulo = data[idx]["a.id"]
            referencia = str(data[idx]["at.referencia"]) + "-" + str(data[idx]["at.talla"])
            if str(data[idx]["at.talla"]) == "TU":
                referencia = str(data[idx]["at.referencia"])
            self.referencia = referencia

            price = self.get_price_serializer().serialize(data[idx])
            cuerpoPrice = {
                "product": price
            }
            del cuerpoPrice["product"]["children"]
            try:
                result = self.send_request("put", url=price_url.format(self.codwebsite, self.referencia), data=json.dumps(cuerpoPrice))
                if "id" in result:
                    if (refConsulta != str(data[idx]["at.referencia"])) or (tarifaConsulta != str(data[idx]["a.codtarifa"])) or idx == len(data):
                        if refConsulta != str(data[idx]["at.referencia"]):
                            refConsulta = str(data[idx]["at.referencia"])
                            if self.refSincros == "":
                                self.refSincros = str(data[idx]["at.referencia"])
                            else:
                                self.refSincros += "," + str(data[idx]["at.referencia"])

                        if tarifaConsulta != str(data[idx]["a.codtarifa"]):
                            tarifaConsulta = str(data[idx]["a.codtarifa"])
                        qsatype.FLSqlQuery().execSql("UPDATE articulostarifas SET sincronizado = TRUE WHERE id = {}".format(self.idArticulo))
            except Exception as e:
                print("exception")
                self.error = True
                self.log("Error", "Referencia no procesada: {})".format(self.referencia))

        return data

    def get_price_serializer(self):
        return PriceSerializer()

    def send_data(self, data):
        """del data["product"]["children"]
        if data:
            result = True
            try:
                print("URL ", price_url.format(self.codwebsite, self.referencia))
                print("DATA: ", json.dumps(data))
                result = self.send_request("put", url=price_url.format(self.codwebsite, self.referencia), data=json.dumps(data))
            except Exception as e:
                print("exception")
                # print(json.dumps(e))
                self.error = True"""

        return data

    def get_db_data(self):
        body = []

        self._fechasincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "fechasincro", "codtienda = 'AWEB' AND esquema = 'PRICES_WEB'")
        horasincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "horasincro", "codtienda = 'AWEB' AND esquema = 'PRICES_WEB'")

        if not self._fechasincro or self._fechasincro is None:
            self._fechasincro = "2021-06-01"
        else:
            self._fechasincro = str(self._fechasincro)[:10]

        if not horasincro or horasincro is None:
            horasincro = "00:00:00"
        else:
            horasincro = str(horasincro)[-(8):]

        filtro_fechas_alta = "(a.fechaalta > '{}' OR (a.fechaalta = '{}' AND a.horaalta >= '{}'))".format(self._fechasincro, self._fechasincro, horasincro)
        filtro_fechas_mod = "(a.fechamod > '{}' OR (a.fechamod = '{}' AND a.horamod >= '{}'))".format(self._fechasincro, self._fechasincro, horasincro)
        filtro_fechas_limite = "(fechaalta > '{}' OR (fechaalta = '{}' AND horaalta >= '{}'))".format(self._fechasincro, self._fechasincro, horasincro)
        filtro_fechas_limite_mod = "(fechamod > '{}' OR (fechamod = '{}' AND horamod >= '{}'))".format(self._fechasincro, self._fechasincro, horasincro)
        where = "a.sincronizado = FALSE AND ({} OR {}) AND a.referencia IN (SELECT referencia FROM articulostarifas WHERE sincronizado = FALSE AND ({} OR {}) GROUP BY referencia LIMIT 25) ORDER BY a.referencia,a.codtarifa".format(filtro_fechas_alta, filtro_fechas_mod,  filtro_fechas_limite, filtro_fechas_limite_mod)

        q = qsatype.FLSqlQuery()
        q.setSelect("a.id,at.referencia, at.talla, a.pvp, st.codstoreview, a.codtarifa")
        q.setFrom("mg_websites w inner join mg_storeviews st on w.codwebsite = st.codwebsite inner join articulostarifas a on a.codtarifa = st.codtarifa inner join atributosarticulos at ON a.referencia = at.referencia")
        q.setWhere(where)

        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False

        return body

    def after_sync(self, response_data=None):
        if self.error:
            self.log("Error", "No se pudo sincronizar la tarifa")
            return self.small_sleep

        self.log("Éxito", "Tarifas de precio sincronizadas correctamente (Referencias: {})".format(self.refSincros))

        return self.small_sleep
