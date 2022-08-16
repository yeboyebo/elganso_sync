from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.prices.serializers.price_serializer import PriceSerializer


class AzPricesUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azpricesupload", params)

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("az.referencia, aa.barcode, at.pvp, a.pvp, app.pvp, pp.desde, pp.hasta, pp.horadesde, pp.horahasta")
        q.setFrom("az_articulosamazon az INNER JOIN articulos a ON az.referencia = a.referencia INNER JOIN atributosarticulos aa ON az.referencia = aa.referencia LEFT OUTER JOIN articulostarifas at ON (a.referencia = at.referencia AND at.codtarifa = (SELECT valor FROM param_parametros WHERE nombre = 'TARIFA_AMAZON')) LEFT OUTER JOIN eg_articulosplan app ON (a.referencia = app.referencia AND app.codplan in (SELECT pp2.codplan FROM eg_planprecios pp2 INNER JOIN eg_tiendasplanprecios tp2 on (pp2.codplan = tp2.codplan AND tp2.codtienda = 'AMAZ') INNER JOIN eg_articulosplan ap2 on (pp2.codplan = ap2.codplan AND a.referencia = ap2.referencia) WHERE pp2.hasta >= CURRENT_DATE AND pp2.vigente ORDER BY pp2.desde DESC, pp2.hasta ASC LIMIT 1)) LEFT OUTER JOIN eg_planprecios pp ON app.codplan = pp.codplan")
        q.setWhere("az.referencia IN (SELECT referencia FROM az_articulosamazon WHERE sincroarticulo AND articulocreado AND sincroimagenes AND sincrorelacion AND NOT sincroprecio AND NOT errorsincro LIMIT {}) AND barcode not in (select barcode from atributosarticulos where a.referencia = aa.referencia and aa.talla in ('35','36','37','38','39','40') and (a.codgrupomoda = '3' OR a.codgrupomoda = '5')) GROUP BY az.referencia, aa.barcode, at.pvp, a.pvp, app.pvp, pp.desde, pp.hasta, pp.horadesde, pp.horahasta".format(self.driver.azQueryLimit))

        return q

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincroprecio = true, idlog_precio = (SELECT id FROM az_logamazon WHERE idamazon = '{}') WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return PriceSerializer()

    def get_msgtype(self):
        return 'Price'

    def get_feedtype(self):
        return '_POST_PRODUCT_PRICING_DATA_'
