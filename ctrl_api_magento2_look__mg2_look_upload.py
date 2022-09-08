from YBLEGACY import qsatype
import json
from datetime import datetime

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
# from controllers.api.magento2.look.serializers.mg2_look_serializer import Mg2LookSerializer

class Mg2LookUpload(ProductsUpload):

    _ssw = ""

    def __init__(self, params=None):
        super().__init__("mg2look", params)

        look_params = self.get_param_sincro('mg2LookUpload')
        self.look_url = look_params['url']
        self.look_test_url = look_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 1
        self.large_sleep = 30
        self.no_sync_sleep = 60

    def get_data(self):
        data = self.get_db_data()
        return {"related": data}
        

    """def get_look_serializer(self):
        return Mg2LookSerializer()"""

    def send_data(self, data):
        look_url = self.look_url if self.driver.in_production else self.look_test_url

        if data:
            print(str(json.dumps(data)))
            result = self.send_request("post", url=look_url, data=json.dumps(data))
            print(str(result))

        return data

    def get_db_data(self):
        body = []

        qLook = qsatype.FLSqlQuery()
        qLook.setSelect("idlook")
        qLook.setFrom("eg_look")
        qLook.setWhere("sincronizado = FALSE ORDER BY idlook ASC")

        qLook.exec_()
        if not qLook.size() or qLook.size() == 0:
            self.log("Exito", "No hay nada que sincronizar")
            return []

        bodyLook = self.fetch_query(qLook)
        for idLook in bodyLook:
            if self._ssw == "":
                self._ssw = str(idLook["idlook"])
            else:
                self._ssw += "," + str(idLook["idlook"])

        q = qsatype.FLSqlQuery()
        q.setSelect("referencia")
        q.setFrom("eg_articuloslook")
        q.setWhere("idlook IN (" + str(self._ssw) + ") GROUP BY referencia ORDER BY referencia")

        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)
        items_related = []
        jRelated = []
        for row in body:
            items_related = []
            qry = qsatype.FLSqlQuery()
            qry.setSelect("referencia")
            qry.setFrom("eg_articuloslook")
            qry.setWhere("idlook IN (SELECT idlook FROM eg_articuloslook WHERE idLook IN (" + str(self._ssw) + ") AND referencia = '" + row["referencia"] + "') AND referencia <> '" + row["referencia"] + "'")
            qry.exec_()
            bQry = self.fetch_query(qry)
            for ref in bQry:
                items_related.append({"sku": ref["referencia"]})

            jRelated.append({"sku": row["referencia"], "items_related": items_related})

        return jRelated

    def after_sync(self, response_data=None):

        if self._ssw != "":
            qsatype.FLSqlQuery().execSql("UPDATE eg_look SET sincronizado = true WHERE idlook IN ({})".format(self._ssw))
            self.log("Exito", "LOOK sincronizado correctamente")

        return self.small_sleep
