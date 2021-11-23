from YBLEGACY import qsatype
import requests
import json

from controllers.base.magento2.tierprice.controllers.tierprice_upload import TierpriceUpload
from controllers.api.magento2.delete_tierprice.serializers.delete_tierprice_serializer import DeleteTierpriceSerializer

class Mg2DeleteTierPriceUpload(TierpriceUpload):

    error = False
    _ssw = None

    def __init__(self, params=None):
        super().__init__("mg2deletetierprice", params)

        delete_tierprice_params = self.get_param_sincro('mg2DeleteTierpricesUpload')
        self.delete_tierprice_url = delete_tierprice_params['url']
        self.delete_tierprice_test_url = delete_tierprice_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))
        self.small_sleep = 1

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_delete_tierprice = []
        idObjeto = None
        for idx in range(len(data)):
            price = self.get_delete_tierprice_serializer().serialize(data[idx])
            new_delete_tierprice.append(price)
            if not idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._ssw = str(data[idx]["ls.id"])

            if str(data[idx]["ls.id"]) != idObjeto:
                idObjeto = str(data[idx]["ls.id"])
                self._ssw += "," + str(data[idx]["ls.id"])

        if not new_delete_tierprice:
            return False

        return {
            "prices": new_delete_tierprice
        }

    def send_data(self, data):
        delete_tierprice_url = self.delete_tierprice_url if self.driver.in_production else self.delete_tierprice_test_url

        for idx in range(len(data["prices"])):
            del data["prices"][idx]["children"]
        if data:
            result = True
            try:
                print("DATA: ", json.dumps(data))
                print("URL: ", delete_tierprice_url)
                self.send_request("post", url=delete_tierprice_url.format("es"), data=json.dumps(data))
                self.send_request("post", url=delete_tierprice_url.format("fr"), data=json.dumps(data))
                self.send_request("post", url=delete_tierprice_url.format("en"), data=json.dumps(data))
                ## result = self.send_request("post", url=delete_tierprice_url.format("es"), data=json.dumps(data))
                ## print("RESULT: ", str(result))
            except Exception as e:
                # print(str(e))
                # print("exception")
                print(str(e))
                self.error = True

        return data

    def get_db_data(self):
        body = []

        q = qsatype.FLSqlQuery()
        q.setSelect("ls.id, at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, ap.activo, p.hasta || ' ' || p.horahasta, mg.idwebsite, mg.codstoreview")
        q.setFrom("eg_planprecios p INNER JOIN eg_articulosplan ap ON p.codplan = ap.codplan INNER JOIN atributosarticulos at ON ap.referencia = at.referencia INNER JOIN eg_tiendasplanprecios tp ON p.codplan = tp.codplan INNER JOIN mg_storeviews mg ON tp.codtienda = mg.egcodtiendarebajas INNER JOIN lineassincro_catalogo ls ON (p.codplan = ls.idobjeto AND at.referencia || '-' || at.talla || '-' || mg.idmagento = ls.descripcion)")
        q.setWhere("p.elgansociety = TRUE AND ls.sincronizado = FALSE AND ls.tiposincro = 'Eliminar Planificador' AND (p.hasta < CURRENT_DATE OR (p.hasta = CURRENT_DATE AND p.horahasta <= CURRENT_TIME)) GROUP BY ls.id,at.referencia, at.talla, ap.pvp, p.desde || ' ' || p.horadesde, p.hasta || ' ' || p.horahasta, mg.idwebsite, ap.activo, mg.codstoreview ORDER BY ls.id LIMIT 10000")

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.error = False
        return body

    def get_delete_tierprice_serializer(self):
        return DeleteTierpriceSerializer()

    def after_sync(self, response_data=None):
        print("SSW: ", self._ssw)
        if self.error:
            self.log("Error", "No se pudo eliminar las líneas de planificador: {})".format(self._ssw))
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id IN ({})".format(self._ssw))

        self.log("Exito", "Lineas de planificador eliminadas correctamente {}".format(self._ssw))

        return self.small_sleep
