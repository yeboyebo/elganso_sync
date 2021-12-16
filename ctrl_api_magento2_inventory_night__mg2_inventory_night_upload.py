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

        self.small_sleep = 1
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

        hora1 = datetime.strptime("01:30:00", "%X").time()
        hora2 = datetime.strptime("06:30:00", "%X").time()
        hora_act = datetime.now().time()

        if hora_act > hora1 and hora_act < hora2:
            body = []

            q = qsatype.FLSqlQuery()
            q.setSelect("aa.referencia, aa.talla, aa.barcode, s.disponible, s.cantidad, s.idstock, ssw.idssw, s.codalmacen")
            q.setFrom("eg_sincrostockweb ssw INNER JOIN stocks s ON s.idstock = ssw.idstock INNER JOIN atributosarticulos aa ON s.barcode = aa.barcode INNER JOIN articulos a ON aa.referencia = a.referencia")
            q.setWhere("ssw.sincronizado = FALSE GROUP BY aa.referencia, aa.talla, aa.barcode, s.disponible, s.cantidad, s.idstock, ssw.idssw, s.codalmacen ORDER BY aa.referencia,aa.talla, ssw.idssw, s.idstock LIMIT 1000")

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

        qsatype.FLSqlQuery().execSql("DELETE FROM eg_sincromovistockweb WHERE sincronizado = false AND idstock IN (SELECT idstock from eg_sincrostockweb where idssw IN ({}))".format(self._ssw))

        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincromovistockweb (idstock, idmovimiento, referencia, talla, barcode, sincronizado, cantidad, fecha, hora) (SELECT m.idstock, m.idmovimiento, l.referencia, l.talla, l.barcode, false, lv.cantenviada, CURRENT_DATE, CURRENT_TIME FROM tpv_comandas c INNER JOIN tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea INNER JOIN tpv_lineasmultitransstock lv ON (e.idviajemultitrans = lv.idviajemultitrans AND l.barcode = lv.barcode) INNER JOIN movistock m ON lv.idlinea = m.idlineatto INNER JOIN stocks s ON (s.idstock = m.idstock AND s.codalmacen = e.codalmacen) INNER JOIN eg_sincrostockweb i ON s.idstock = i.idstock WHERE c.fecha > CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = false AND e.pedidopreparado = false AND e.faltantecreada = false AND i.idssw IN ({}))".format(self._ssw))

        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincromovistockweb (idstock, idmovimiento, referencia, talla, barcode, sincronizado, cantidad, fecha, hora) (SELECT m.idstock, m.idmovimiento, l.referencia, l.talla, l.barcode, false, l.cantidad, CURRENT_DATE, CURRENT_TIME from idl_ecommerce e INNER JOIN tpv_comandas c on e.idtpv_comanda = c.idtpv_comanda INNER JOIN tpv_lineascomanda l on c.idtpv_comanda = l.idtpv_comanda INNER JOIN movistock m on l.idtpv_linea = m.idlineaco INNER JOIN stocks s on m.idstock = s.idstock INNER JOIN eg_sincrostockweb i ON s.idstock = i.idstock left outer join eg_lineasecommerceexcluidas ex on l.idtpv_linea = ex.idtpv_linea WHERE (e.confirmacionenvio = 'No' OR e.confirmacionenvio = 'Parcial') AND idlogenvio > 0 AND idlogenvio <> 999999 AND c.codtienda = 'AWEB' AND (c.codigo like 'WEB%' or c.codigo like 'WDV') AND c.fecha >= CURRENT_DATE-30 AND m.estado = 'PTE' AND ex.id is null AND s.codalmacen = 'AWEB' AND i.idssw IN ({}))".format(self._ssw))

        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincromovistockweb (idstock, idmovimiento, referencia, talla, barcode, sincronizado, cantidad, fecha, hora) (SELECT m.idstock, m.idmovimiento, l.referencia, l.talla, l.barcode, false, l.cantidad, CURRENT_DATE, CURRENT_TIME from pedidoscli p INNER JOIN lineaspedidoscli l on p.idpedido = l.idpedido INNER JOIN movistock m on l.idlinea = m.idlineapc INNER JOIN eg_sincrostockwebinmediato i ON m.idstock = i.idstock WHERE p.codserie = 'SW' AND i.idssw IN ({}))".format(self._ssw))

        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincromovistockweb (idstock, idmovimiento, referencia, talla, barcode, sincronizado, cantidad, fecha, hora) (SELECT m.idstock, m.idmovimiento, l.referencia, l.talla, l.barcode, false, lv.cantenviada, CURRENT_DATE, CURRENT_TIME FROM eg_seguimientoenvios sg INNER JOIN almacenes a on sg.codalmacen = a.codalmacen inner join tpv_comandas c on sg.coddocumento = c.codigo INNER JOIN tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea INNER JOIN tpv_lineasmultitransstock lv ON (e.idviajemultitrans = lv.idviajemultitrans AND l.barcode = lv.barcode) INNER JOIN movistock m ON lv.idlinea = m.idlineatto INNER JOIN stocks s ON (s.idstock = m.idstock AND s.codalmacen = e.codalmacen) INNER JOIN eg_sincrostockwebinmediato i ON s.idstock = i.idstock WHERE c.fecha > CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = true AND e.pedidopreparado = true AND e.faltantecreada = false AND (e.codalmacen = 'LFWB' OR lower(a.egtipoalmacen) = 'community') AND (sg.numseguimiento IS NULL OR sg.numseguimiento = '') AND i.idssw IN ({}))".format(self._ssw))

        self.log("Exito", "Stock sincronizado correctamente")

        return self.small_sleep
