from YBLEGACY import qsatype
import json
from controllers.base.magento2.tierprice.controllers.tierprice_upload import TierpriceUpload
from controllers.api.magento2.tierprice.serializers.tierprice_serializer import TierpriceSerializer

class Mg2TierpriceUpload(TierpriceUpload):

    error = False
    _ssw = None

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
        idObjeto = None
        for idx in range(len(data)):
            price = self.get_tierprice_serializer().serialize(data[idx])
            new_tierprice.append(price)
            if not idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._ssw = str(data[idx]["ls.id"])

            if str(data[idx]["ls.id"]) != idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._ssw += "," + str(data[idx]["ls.id"])

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

        q = qsatype.FLSqlQuery()
        q.setSelect("ls.id, at.referencia, at.talla, ap.pvp, mg.idmagento")
        q.setFrom("eg_planprecios p INNER JOIN eg_articulosplan ap ON p.codplan = ap.codplan INNER JOIN atributosarticulos at ON ap.referencia = at.referencia INNER JOIN eg_tiendasplanprecios tp ON p.codplan = tp.codplan INNER JOIN mg_storeviews mg ON tp.codtienda = mg.egcodtiendarebajas INNER JOIN lineassincro_catalogo ls ON (p.codplan = ls.idobjeto AND at.referencia = ls.descripcion)")
        q.setWhere("p.elgansociety = TRUE AND ls.id IN (SELECT id FROM lineassincro_catalogo WHERE sincronizado = FALSE AND tiposincro = 'Planificador Precios' LIMIT 25) GROUP BY ls.id, at.referencia, at.talla, ap.pvp, mg.idmagento ORDER BY ls.id")

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False
        return body

    def get_tierprice_serializer(self):
        return TierpriceSerializer()

    def after_sync(self, response_data=None):
        print("SSW: ", self._ssw)
        if self.error:
            self.log("Error", "No se pudo sincronizar las líneas de planificador: {})".format(self._ssw))
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id IN ({})".format(self._ssw))

        self.log("Exito", "Lineas de planificador sincronizadas correctamente {}".format(self._ssw))

        return self.small_sleep
