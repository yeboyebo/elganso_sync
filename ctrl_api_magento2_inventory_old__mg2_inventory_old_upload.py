from YBLEGACY import qsatype
import json

from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload
from controllers.api.magento2.inventory_old.serializers.inventory_old_serializer import InventoryOldSerializer

class Mg2InventoryOldUpload(InventoryUpload):

    _ssw = ""

    def __init__(self, params=None):
        super().__init__("mg2inventoryold", params)

        inventory_params = self.get_param_sincro('mg2InventoryUpload')
        self.inventory_url = inventory_params['url']
        self.inventory_test_url = inventory_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 10
        self.large_sleep = 30
        self.no_sync_sleep = 60

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_inventory = []
        for idx in range(len(data)):
            inventory = self.get_inventory_serializer().serialize(data[idx])
            new_inventory.append(inventory)
        if not new_inventory:
            return new_inventory

        return {
            "sourceItems": new_inventory
        }

    def get_inventory_serializer(self):
        return InventoryOldSerializer()

    def send_data(self, data):
        inventory_url = self.inventory_url if self.driver.in_production else self.inventory_test_url

        for idx in range(len(data["sourceItems"])):
            del data["sourceItems"][idx]["children"]
        if data:
            result = self.send_request("post", url=inventory_url, data=json.dumps(data))

        return data

    def get_db_data(self):
        body = []

        q = qsatype.FLSqlQuery()
        q.setSelect("ssw.idssw, aa.referencia, aa.talla, s.disponible, s.codalmacen, s.idstock")
        q.setFrom("articulos a INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON aa.barcode = s.barcode LEFT OUTER JOIN eg_sincrostockweb ssw ON s.idstock = ssw.idstock")
        q.setWhere("NOT ssw.sincronizado OR ssw.sincronizado = false ORDER BY aa.referencia LIMIT 1000")

        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)
        for row in body:
            if self._ssw == "":
                self._ssw = str(row['ssw.idssw'])
            else:
                self._ssw += ","
                self._ssw += str(row['ssw.idssw'])

        return body

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = true WHERE idssw IN ({})".format(self._ssw))

        self.log("Exito", "Stock sincronizado correctamente")

        return self.small_sleep
