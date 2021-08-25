from YBLEGACY import qsatype
import json

from controllers.base.magento2.inventory.controllers.inventory_upload import InventoryUpload
from controllers.api.magento2.inventory.serializers.inventory_serializer import InventorySerializer

class Mg2InventoryUpload(InventoryUpload):

    _ssw = ""

    def __init__(self, params=None):
        super().__init__("mg2inventory", params)

        inventory_params = self.get_param_sincro('mg2InventoryUpload')
        self.inventory_url = inventory_params['url']
        self.inventory_test_url = inventory_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 5
        self.large_sleep = 60
        self.no_sync_sleep = 120

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
        return InventorySerializer()

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
        q.setFrom("articulos a INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON aa.barcode = s.barcode LEFT OUTER JOIN eg_sincrostockwebinmediato ssw ON s.idstock = ssw.idstock")
        q.setWhere("NOT ssw.sincronizado OR ssw.sincronizado = false ORDER BY aa.referencia, aa.talla, ssw.idssw LIMIT 2000")

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
        qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockwebinmediato SET sincronizado = true WHERE idssw IN ({})".format(self._ssw))

        qsatype.FLSqlQuery().execSql("DELETE FROM eg_sincromovistockweb WHERE sincronizado = false AND idstock IN (SELECT idstock from eg_sincrostockwebinmediato where idssw IN ({}))".format(self._ssw))

        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincromovistockweb (idstock, idmovimiento, referencia, talla, barcode, sincronizado, cantidad, fecha, hora) (SELECT m.idstock, m.idmovimiento, l.referencia, l.talla, l.barcode, false, lv.cantenviada, CURRENT_DATE, CURRENT_TIME FROM tpv_comandas c INNER JOIN tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea INNER JOIN tpv_lineasmultitransstock lv ON (e.idviajemultitrans = lv.idviajemultitrans AND l.barcode = lv.barcode) INNER JOIN movistock m ON lv.idlinea = m.idlineatto INNER JOIN stocks s ON (s.idstock = m.idstock AND s.codalmacen = e.codalmacen) INNER JOIN eg_sincrostockwebinmediato i ON s.idstock = i.idstock WHERE c.fecha > CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = false AND e.pedidopreparado = false AND e.faltantecreada = false AND i.idssw IN ({}))".format(self._ssw))

        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincromovistockweb (idstock, idmovimiento, referencia, talla, barcode, sincronizado, cantidad, fecha, hora) (SELECT m.idstock, m.idmovimiento, l.referencia, l.talla, l.barcode, false, l.cantidad, CURRENT_DATE, CURRENT_TIME from idl_ecommerce e INNER JOIN tpv_comandas c on e.idtpv_comanda = c.idtpv_comanda INNER JOIN tpv_lineascomanda l on c.idtpv_comanda = l.idtpv_comanda INNER JOIN movistock m on l.idtpv_linea = m.idlineaco INNER JOIN stocks s on m.idstock = s.idstock INNER JOIN eg_sincrostockwebinmediato i ON s.idstock = i.idstock left outer join eg_lineasecommerceexcluidas ex on l.idtpv_linea = ex.idtpv_linea WHERE e.confirmacionenvio = 'No' AND idlogenvio > 0 AND idlogenvio <> 999999 AND c.codtienda = 'AWEB' AND (c.codigo like 'WEB%' or c.codigo like 'WDV') AND c.fecha >= CURRENT_DATE-30 AND m.estado = 'PTE' AND ex.id is null AND s.codalmacen = 'AWEB' AND i.idssw IN ({}))".format(self._ssw))

        self.log("Exito", "Stock sincronizado correctamente")

        return self.small_sleep
