from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.stocks.serializers.stock_serializer import StockSerializer


class AzStocksUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azstocksupload", params)

        self.small_sleep = 300
        self.large_sleep = 300
        self.no_sync_sleep = 300

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("az.referencia, aa.barcode, s.disponible, p.valor")
        q.setFrom("articulos a INNER JOIN az_articulosamazon az ON a.referencia = az.referencia INNER JOIN atributosarticulos aa ON az.referencia = aa.referencia LEFT JOIN stocks s ON aa.barcode = s.barcode INNER JOIN param_parametros p ON p.nombre = 'RSTOCK_AMAZ'")
        q.setWhere("az.referencia IN (SELECT referencia FROM az_articulosamazon WHERE articulocreado AND NOT sincrostock LIMIT {}) AND s.codalmacen = 'AWEB' AND aa.barcode not in (select barcode from atributosarticulos where a.referencia = aa.referencia and aa.talla >= '35' and (a.codgrupomoda = '3' OR a.codgrupomoda = '5'))".format(self.driver.azQueryLimit))

        return q

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincrostock = true, idlog_stock = (SELECT id FROM az_logamazon WHERE idamazon = '{}') WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return StockSerializer()

    def get_msgtype(self):
        return 'Inventory'

    def get_feedtype(self):
        return '_POST_INVENTORY_AVAILABILITY_DATA_'
