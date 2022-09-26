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
        self.no_sync_sleep = 120

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
        qLook.setSelect("l.idlook, l.referencia")
        qLook.setFrom("eg_look l INNER JOIN lineassincro_catalogo ls ON l.referencia = ls.idobjeto")
        qLook.setWhere("l.sincronizado = FALSE AND ls.sincronizado = TRUE AND ls.tiposincro = 'Enviar productos' AND ls.website = 'MG2' GROUP BY l.idlook, l.referencia ORDER BY l.idlook ASC LIMIT 20")

        qLook.exec_()
        if not qLook.size() or qLook.size() == 0:
            self.log("Exito", "No hay nada que sincronizar")
            return []

        bodyLook = self.fetch_query(qLook)
        
        items_related = []
        jRelated = []
        
        for idLook in bodyLook:
            if self._ssw == "":
                self._ssw = str(idLook["l.idlook"])
            else:
                self._ssw += "," + str(idLook["l.idlook"])
                
            print(str(idLook["l.idlook"]))
            
            items_related = []
            qry = qsatype.FLSqlQuery()
            qry.setSelect("a.referencia")
            qry.setFrom("eg_articuloslook a INNER JOIN lineassincro_catalogo ls ON a.referencia = ls.idobjeto")
            qry.setWhere("ls.sincronizado AND ls.tiposincro = 'Enviar productos' AND ls.website = 'MG2' AND a.idlook = " + str(idLook["l.idlook"]) + " GROUP BY a.referencia")
            qry.exec_()
            
            if not qry.size() or qLook.size() == 0:
                continue

            bQry = self.fetch_query(qry)
            for ref in bQry:
                items_related.append({"sku": ref["a.referencia"]})

            jRelated.append({"sku": str(idLook["l.referencia"]), "items_related": items_related})

        return jRelated
            
        ''' if not qsatype.FLUtil.quickSqlSelect("eg_articuloslook a INNER JOIN lineassincro_catalogo ls ON a.referencia = ls.idobjeto", "a.referencia", "ls.sincronizado = FALSE AND ls.tiposincro = 'Enviar productos' AND ls.website = 'MG2' AND a.idlook = " + str(idLook["idlook"]) + " GROUP BY referencia"):
            if self._ssw == "":
                self._ssw = str(idLook["idlook"])
            else:
                self._ssw += "," + str(idLook["idlook"])

        if self._ssw == "":
            self.log("Exito", "No hay nada que sincronizar")
            return []

        q = qsatype.FLSqlQuery()
        q.setSelect("referencia")
        q.setFrom("eg_look")
        q.setWhere("idlook IN (" + str(self._ssw) + ") ORDER BY idlook")

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
            qry.setWhere("idlook = " + str(self._ssw))
            qry.exec_()
            bQry = self.fetch_query(qry)
            for ref in bQry:
                items_related.append({"sku": ref["referencia"]})

            jRelated.append({"sku": row["referencia"], "items_related": items_related})

        return jRelated '''

    def after_sync(self, response_data=None):

        if self._ssw != "":
            qsatype.FLSqlQuery().execSql("UPDATE eg_look SET sincronizado = true WHERE idlook IN ({})".format(self._ssw))
            self.log("Exito", "LOOK sincronizado correctamente")
            return self.small_sleep

        return self.no_sync_sleep
