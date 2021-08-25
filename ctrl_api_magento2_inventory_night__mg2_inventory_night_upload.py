from YBLEGACY import qsatype
import json
from datetime import datetime

from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload
from controllers.api.magento2.inventory_night.serializers.inventory_night_serializer import InventoryNightSerializer

class Mg2InventoryNightUpload(InventoryUpload):

    _ssw = ""

    def __init__(self, params=None):
        super().__init__("mg2inventorynight", params)

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
        return InventoryNightSerializer()

    def send_data(self, data):
        inventory_url = self.inventory_url if self.driver.in_production else self.inventory_test_url

        for idx in range(len(data["sourceItems"])):
            del data["sourceItems"][idx]["children"]
        if data:
            result = self.send_request("post", url=inventory_url, data=json.dumps(data))

        return data

    def get_db_data(self):

        hora1 = datetime.strptime("09:00:00", "%X").time()
        hora2 = datetime.strptime("10:00:00", "%X").time()
        hora_act = datetime.now().time()

        if hora_act > hora1 and hora_act < hora2:
            body = []

            q = qsatype.FLSqlQuery()
            q.setSelect("aa.referencia, aa.talla, aa.barcode, s.disponible, s.cantidad, s.idstock, ssw.idssw, s.codalmacen")
            q.setFrom("articulos a INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON aa.barcode = s.barcode LEFT OUTER JOIN eg_sincrostockweb ssw ON s.idstock = ssw.idstock LEFT OUTER JOIN eg_sincromovistockweb smv ON s.idstock = smv.idstock")
            q.setWhere("(NOT ssw.sincronizado OR ssw.sincronizado = false) AND (smv.sincronizado = true OR smv.idstock IS NULL) ORDER BY aa.referencia LIMIT 2000")

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
        else:
            return []
        return body

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = true WHERE idssw IN ({})".format(self._ssw))

        self.log("Exito", "Stock sincronizado correctamente")

        return self.small_sleep
