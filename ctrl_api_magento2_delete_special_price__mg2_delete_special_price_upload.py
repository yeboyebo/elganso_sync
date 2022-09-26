from YBLEGACY import qsatype
import requests
import json


from controllers.base.magento2.tierprice.controllers.tierprice_upload import TierpriceUpload

from controllers.api.magento2.delete_special_price.serializers.delete_special_price_serializer import DeleteSpecialPriceSerializer

class Mg2DeleteSpecialPriceUpload(TierpriceUpload):

    _ssw = None

    def __init__(self, params=None):
        super().__init__("mg2deletespecialprice", params)

        delete_special_price_params = self.get_param_sincro('mg2DeleteSpecialPricesUpload')
        self.delete_special_price_url = delete_special_price_params['url']
        self.delete_special_price_test_url = delete_special_price_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))
        
        self.small_sleep = 2

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            self.log("Exito", "No hay datos que sincronizar")
            return data

        new_price = []
        idObjeto = None
        for idx in range(len(data)):
            price = self.get_price_serializer().serialize(data[idx])
            new_price.append(price)
            if not idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._ssw = str(data[idx]["ls.id"])

            if str(data[idx]["ls.id"]) != idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._ssw += "," + str(data[idx]["ls.id"])

        if not new_price:
            return False

        return {
            "prices": new_price
        }

    def get_price_serializer(self):
        return DeleteSpecialPriceSerializer()

    def send_data(self, data):
        delete_special_price_url = self.delete_special_price_url if self.driver.in_production else self.delete_special_price_test_url

        for idx in range(len(data["prices"])):
            del data["prices"][idx]["children"]
        if data:
            result = True
            try:
                print("DATA: ", json.dumps(data))
                print("URL: ", delete_special_price_url)
                result = self.send_request("post", url=delete_special_price_url, data=json.dumps(data))
                print("RESULT: ", result)
            except Exception as e:
                print("exception")
                # print(json.dumps(e))
                self.error = True

        return data

    def get_db_data(self):
        body = []

        q = qsatype.FLSqlQuery()        
        q.setSelect("ls.id, at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, ap.activo, p.hasta || ' ' || p.horahasta, mg.idmagento")
        q.setFrom("eg_planprecios p INNER JOIN eg_articulosplan ap ON p.codplan = ap.codplan INNER JOIN atributosarticulos at ON ap.referencia = at.referencia INNER JOIN eg_tiendasplanprecios tp ON p.codplan = tp.codplan INNER JOIN mg_storeviews mg ON tp.codtienda = mg.egcodtiendarebajas INNER JOIN lineassincro_catalogo ls ON (p.codplan = ls.idobjeto AND at.referencia || '-' || at.talla || '-' || mg.idmagento = ls.descripcion)")        
        q.setWhere("p.elgansociety = FALSE AND ls.sincronizado = FALSE AND ls.tiposincro = 'Eliminar Planificador' AND (p.hasta < CURRENT_DATE OR (p.hasta = CURRENT_DATE AND p.horahasta <= CURRENT_TIME)) GROUP BY ls.id, at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, ap.activo, p.hasta || ' ' || p.horahasta, mg.idmagento ORDER BY ls.id LIMIT 20000")

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False
        return body

    def after_sync(self, response_data=None):
        print("SSW: ", self._ssw)
        if self.error:
            self.log("Error", "No se pudo eliminar las líneas de planificador: {})".format(self._ssw))
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id IN ({})".format(self._ssw))

        self.log("Exito", "Lineas de planificador eliminadas correctamente {}".format(self._ssw))

        return self.small_sleep
