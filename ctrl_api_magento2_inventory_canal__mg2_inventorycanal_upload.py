from YBLEGACY import qsatype
import json
from datetime import datetime

from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload
from controllers.api.magento2.inventory_canal.serializers.inventorycanal_serializer import InventorySerializer

class Mg2InventoryCanalUpload(InventoryUpload):

    _ssw = ""

    def __init__(self, params=None):
        super().__init__("mg2inventorycanal", params)

        inventory_params = self.get_param_sincro('mg2InventoryCanalUpload')
        self.inventory_url = inventory_params['url']
        self.inventory_test_url = inventory_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 1
        self.large_sleep = 30
        self.no_sync_sleep = 60

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_inventory = []

        oCanales = json.loads(qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'CANALES_WEB'"))
        datos = {}
        datos["ocanales"] = oCanales
        for idx in range(len(data)):
            datos["linea"] = data[idx]
            inventory = self.get_inventorycanal_serializer().serialize(datos)
            new_inventory.append(inventory)
        if not new_inventory:
            return new_inventory

        return {
            "sourceItems": new_inventory
        }

    def get_inventorycanal_serializer(self):
        return InventorySerializer()

    def send_data(self, data):
        inventory_url = self.inventory_url if self.driver.in_production else self.inventory_test_url

        for idx in range(len(data["sourceItems"])):
            del data["sourceItems"][idx]["children"]
        if data:
            print(str(json.dumps(data)))
            result = self.send_request("post", url=inventory_url, data=json.dumps(data))
            print(str(result))

        return data

    def get_db_data(self):
        # hora1 = datetime.strptime("06:30:00", "%X").time()
        # hora2 = datetime.strptime("01:30:00", "%X").time()
        # hora_act = datetime.now().time()

        # if hora_act > hora1 or hora_act < hora2:
        body = []

        q = qsatype.FLSqlQuery()
        q.setSelect("ssw.idss, ssw.barcode, ssw.codcanalweb, aa.referencia, aa.talla")
        q.setFrom("eg_sincrostockwebcanalweb ssw INNER JOIN atributosarticulos aa ON ssw.barcode = aa.barcode")
        q.setWhere("(NOT ssw.sincronizado OR ssw.sincronizado = false) ORDER BY ssw.fecha desc, ssw.hora desc, ssw.idss LIMIT 100")

        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)
        for row in body:
            if self._ssw == "":
                self._ssw = str(row['ssw.idss'])
            else:
                self._ssw += ","
                self._ssw += str(row['ssw.idss'])
        # else:
            # return []

        return body

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockwebcanalweb SET sincronizado = true WHERE idss IN ({})".format(self._ssw))

        self.log("Exito", "Stock sincronizado correctamente")

        return self.small_sleep
