from YBLEGACY import qsatype
import requests
import json
from controllers.base.magento2.price.controllers.price_upload import PriceUpload
from controllers.api.magento2.price.serializers.price_serializer import PriceSerializer

class Mg2PriceUpload(PriceUpload):

    def __init__(self, params=None):
        super().__init__("mg2price", params)

        price_params = self.get_param_sincro('mg2PricesUpload')
        self.price_url = price_params['url']
        self.price_test_url = price_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            self.log("Exito", "No hay datos que sincronizar")
            return data

        new_price = []
        for idx in range(len(data)):
            price = self.get_price_serializer().serialize(data[idx])
            new_price.append(price)

        if not new_price:
            return False

        return {
            "prices": new_price
        }

    def get_price_serializer(self):
        return PriceSerializer()

    def send_data(self, data):
        price_url = self.price_url if self.driver.in_production else self.price_test_url

        for idx in range(len(data["prices"])):
            del data["prices"][idx]["children"]
        if data:
            result = True
            try:
                result = self.send_request("post", url=price_url, data=json.dumps(data))
            except Exception as e:
                print("exception")
                # print(json.dumps(e))
                self.error = True

        return data

    def get_db_data(self):
        body = []

        idobjeto = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "idobjeto", "tiposincro = 'Planificador Precios' AND NOT sincronizado AND website = 'magento2' ORDER BY id LIMIT 1")

        if not idobjeto:
            return body

        self.idobjeto = idobjeto

        q = qsatype.FLSqlQuery()
        q.setSelect("at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, p.hasta || ' ' || p.horahasta")
        q.setFrom("eg_planprecios p INNER JOIN eg_articulosplan ap ON p.codplan = ap.codplan INNER JOIN atributosarticulos at ON ap.referencia = at.referencia")
        q.setWhere("p.codplan = '{}' GROUP BY at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, p.hasta || ' ' || p.horahasta".format(self.idobjeto))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False
        return body

    def after_sync(self, response_data=None):
        if self.error:
            self.log("Error", "No se pudo sincronizar el planificador: {})".format(self.idobjeto))
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE idobjeto = '{}'".format(self.idobjeto))

        self.log("Exito", "Planificador {} sincronizado correctamente".format(self.idobjeto))

        return self.small_sleep
