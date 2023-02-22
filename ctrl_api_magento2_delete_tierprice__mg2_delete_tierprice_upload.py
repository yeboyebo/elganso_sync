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
                idObjeto = str(data[idx]["id"])
                self._ssw = str(data[idx]["id"])

            if str(data[idx]["id"]) != idObjeto:
                idObjeto = str(data[idx]["id"])
                self._ssw += "," + str(data[idx]["id"])

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
                print("URL: ", delete_tierprice_url.format("es"))
                result = self.send_request("post", url=delete_tierprice_url.format("es"), data=json.dumps(data))
                print("RESULT: ", str(result))
            except Exception as e:
                print(str(e))
                self.error = True

        return data

    def get_db_data(self):    
        body = []
        q = qsatype.FLSqlQuery()
        q.setSelect("id, referencia, talla, pvp, website, codgrupo")
        q.setFrom("lineassincro_eliminarplanpreciosmagento")
        q.setWhere("sincronizado = FALSE AND (hasta < CURRENT_DATE OR (hasta = CURRENT_DATE AND horahasta <= CURRENT_TIME)) ORDER BY id LIMIT 1000")
        
        print("CONSULTA: ", q.sql())

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

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_eliminarplanpreciosmagento SET sincronizado = TRUE WHERE id IN ({})".format(self._ssw))

        self.log("Exito", "Lineas de planificador eliminadas correctamente {}".format(self._ssw))

        return self.small_sleep
