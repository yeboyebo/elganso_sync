from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
# from controllers.api.amazon.images.serializers.image_serializer import ImageSerializer


class AzOrderFulfillmentUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azorderfulfillmentupload", params)

    def get_query(self):
        q = qsatype.FLSqlQuery()
        # q.setSelect("az.referencia, aa.barcode, urls.urls")
        # q.setFrom("az_articulosamazon az INNER JOIN atributosarticulos aa ON az.referencia = aa.referencia LEFT JOIN eg_urlsimagenesarticulosmgt urls ON az.referencia = urls.referencia")
        # q.setWhere("az.sincroarticulo AND az.articulocreado AND az.sincrorelacion AND NOT az.sincroimagenes AND NOT az.errorsincro")

        return q

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        # qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincroprecio = true, idlog_precio = (SELECT id FROM az_logamazon WHERE idamazon = '{}') WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        # return PriceSerializer()
        return None

    def get_msgtype(self):
        return 'OrderFulfillment'

    def get_feedtype(self):
        return '_POST_ORDER_FULFILLMENT_DATA_'
