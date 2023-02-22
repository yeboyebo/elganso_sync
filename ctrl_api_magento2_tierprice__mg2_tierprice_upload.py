from YBLEGACY import qsatype
import requests
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
        self.small_sleep = 1

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
                idObjeto = str(data[idx]["id"])
                self._ssw = str(data[idx]["id"])

            if str(data[idx]["id"]) != idObjeto:
                idObjeto = str(data[idx]["id"])
                self._ssw += "," + str(data[idx]["id"])

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
            result = True
            try:
                print("DATA: ", json.dumps(data))
                print("URL: ", tierprice_url.format("es"))
                result = self.send_request("post", url=tierprice_url.format("es"), data=json.dumps(data))
                ### self.send_request("post", url=tierprice_url.format("fr"), data=json.dumps(data))
                ### self.send_request("post", url=tierprice_url.format("en"), data=json.dumps(data))
                ## result = self.send_request("post", url=delete_tierprice_url.format("es"), data=json.dumps(data))
                print("RESULT: ", result)
            except Exception as e:
                # print(str(e))
                # print("exception")
                # print(json.dumps(e))
                self.error = True

        return data

    def get_db_data(self):    
        body = []
        q = qsatype.FLSqlQuery()
        q.setSelect("id, referencia, talla, pvp, website, codgrupo")
        q.setFrom("lineassincro_planpreciosmagento")
        q.setWhere("sincronizado = FALSE AND activo AND (desde < CURRENT_DATE OR (desde = CURRENT_DATE AND horadesde <= CURRENT_TIME)) ORDER BY id LIMIT 1000")
        
        print("CONSULTA: ", q.sql())

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

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosmagento SET sincronizado = TRUE WHERE id IN ({})".format(self._ssw))

        self.log("Exito", "Lineas de planificador sincronizadas correctamente {}".format(self._ssw))

        return self.small_sleep
