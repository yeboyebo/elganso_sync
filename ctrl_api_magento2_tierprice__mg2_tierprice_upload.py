from YBLEGACY import qsatype
import json
from controllers.base.magento2.tierprice.controllers.tierprice_upload import TierpriceUpload
from controllers.api.magento2.tierprice.serializers.tierprice_serializer import TierpriceSerializer

class Mg2TierpriceUpload(TierpriceUpload):

    _fechasincro = None
    error = False

    def __init__(self, params=None):
        super().__init__("mg2tierprice", params)

        tierprice_params = self.get_param_sincro('mg2TierpricesUpload')
        self.tierprice_url = tierprice_params['url']
        self.tierprice_test_url = tierprice_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_tierprice = []
        for idx in range(len(data)):
            price = self.get_tierprice_serializer().serialize(data[idx])
            new_tierprice.append(price)

        if not new_tierprice:
            return False

        return {
            "prices": new_tierprice
        }

    def send_data(self, data):
        tierprice_url = self.tierprice_url if self.driver.in_production else self.tierprice_test_url

        for idx in range(len(data["prices"])):
            del data["prices"][idx]["children"]

        if data:
            try:
                print("DATA: ", json.dumps(data))
                print("URL: ", tierprice_url)
                self.send_request("post", url=tierprice_url, data=json.dumps(data))
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
        q.setWhere("p.codplan = '{}' AND p.elgansociety = TRUE GROUP BY at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, p.hasta || ' ' || p.horahasta".format(self.idobjeto))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False
        return body

    def get_tierprice_serializer(self):
        return TierpriceSerializer()

    def after_sync(self, response_data=None):
        if self.error:
            self.log("Error", "No se pudo sincronizar la tarifa")
            return self.small_sleep

        if self._fechasincro != "2014-08-01":
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'PRICES_WEB'".format(self.start_date, self.start_time))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('AWEB', 'PRICES_WEB', '{}', '{}')".format(self.start_date, self.start_time))

        self.log("Exito", "Tarifa de precio sincronizada correctamente.")
        return self.small_sleep
