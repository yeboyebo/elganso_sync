from YBLEGACY import qsatype
import requests
import json
from controllers.base.magento2.price.controllers.price_upload import PriceUpload
from controllers.api.magento2.price.serializers.price_serializer import PriceSerializer

class Mg2PriceUpload(PriceUpload):

    codwebsite = None
    referencia = None
    fechasincro = None
    start_date = None
    start_time = None

    def __init__(self, params=None):
        super().__init__("mg2price", params)

        price_params = self.get_param_sincro('mg2PricesUpload')
        self.price_url = price_params['url']
        self.price_test_url = price_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

    def get_data(self):
        data = self.get_db_data()
        price_url = self.price_url if self.driver.in_production else self.price_test_url
        if data == []:
            self.log("Exito", "No hay datos que sincronizar")
            return data

        referencia = ""
        for idx in range(len(data)):
            self.codwebsite = data[idx]["st.codstoreview"]
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
                print(json.dumps(cuerpoPrice))
                print("URL_: ", price_url.format(self.codwebsite, self.referencia))
                result = self.send_request("put", url=price_url.format(self.codwebsite, self.referencia), data=json.dumps(cuerpoPrice))
                print("RESULT: ", result)
            except Exception as e:
                print("exception")
                self.error = True

        return []

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
        where = "{} OR {} ORDER BY a.referencia".format(filtro_fechas_alta, filtro_fechas_mod)

        q = qsatype.FLSqlQuery()
        q.setSelect("at.referencia, at.talla, a.pvp, st.codstoreview")
        q.setFrom("mg_websites w inner join mg_storeviews st on w.codwebsite = st.codwebsite inner join articulostarifas a on a.codtarifa = st.codtarifa inner join atributosarticulos at ON a.referencia = at.referencia")
        q.setWhere(where)

        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)

        return body

    def after_sync(self, response_data=None):
        print("ENTRA")
        if self.error:
            self.log("Error", "No se pudo sincronizar la tarifa")
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('AWEB', 'PRICES_WEB', '{}', '{}')".format(self.start_date, self.start_time))

        self.log("Exito", "Tarifa de precio sincronizada correctamente.")
        return self.small_sleep
