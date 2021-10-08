from YBLEGACY import qsatype
import json

from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload
from controllers.api.magento2.stock_incremental.serializers.stock_incremental_serializer import StockIncrementalSerializer

class Mg2StockIncrementalUpload(InventoryUpload):

    _ssw = ""

    def __init__(self, params=None):
        super().__init__("mg2stockincremental", params)

        stock_incremental_params = self.get_param_sincro('mg2StockIncrementalUpload')
        self.stock_incremental_url = stock_incremental_params['url']
        self.stock_incremental_test_url = stock_incremental_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))
        self.small_sleep = 1
        self.large_sleep = 30
        self.no_sync_sleep = 60

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_stock_incremental = []

        for idx in range(len(data)):
            stock_incremental = self.get_stock_incremental_serializer().serialize(data[idx])
            new_stock_incremental.append(stock_incremental)
        if not new_stock_incremental:
            return new_stock_incremental
        return {
            "sourceItems": new_stock_incremental
        }

    def get_stock_incremental_serializer(self):
        return StockIncrementalSerializer()

    def send_data(self, data):
        stock_incremental_url = self.stock_incremental_url if self.driver.in_production else self.stock_incremental_test_url

        for idx in range(len(data["sourceItems"])):
            del data["sourceItems"][idx]["children"]
        if data:
            result = self.send_request("post", url=stock_incremental_url, data=json.dumps(data))

        return data

    def get_db_data(self):
        body = []

        q = qsatype.FLSqlQuery()
        q.setSelect("ssw.id, ssw.referencia, ssw.talla, ssw.cantidad, s.codalmacen")
        q.setFrom("eg_sincromovistockweb ssw INNER JOIN stocks s ON ssw.idstock = s.idstock")
        q.setWhere("NOT ssw.sincronizado OR ssw.sincronizado = false ORDER BY ssw.referencia LIMIT 500")

        q.exec_()

        body = []
        if not q.size():
            return body

        body = self.fetch_query(q)
        for row in body:
            if self._ssw == "":
                self._ssw = str(row['ssw.id'])
            else:
                self._ssw += ","
                self._ssw += str(row['ssw.id'])

        return body

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE eg_sincromovistockweb SET sincronizado = true WHERE id IN ({})".format(self._ssw))

        self.log("Exito", "Stock Incremental sincronizado correctamente. Id: {}".format(self._ssw))

        return self.small_sleep
