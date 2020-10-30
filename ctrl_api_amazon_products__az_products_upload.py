from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.products.serializers.product_feed_serializer import ProductFeedSerializer
from controllers.api.amazon.products.serializers.parent_product_serializer import ParentProductSerializer
from controllers.api.amazon.products.serializers.product_serializer import ProductSerializer


class AzProductsUpload(AzFeedsUpload, ABC):

    ids = []

    def __init__(self, params=None):
        super().__init__("azproductsupload", params)

    def get_db_data(self):
        body = super().get_db_data()

        for row in body:
            if row['lsc.id'] not in self.ids:
                self.ids.append(row['lsc.id'])

        return body

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, az.referencia, aa.barcode, aa.talla, a.egcolor, a.mgdescripcion, a.mgdescripcioncorta, a.codgrupomoda, f.codfamiliaaz")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN az_articulosamazon az ON lsc.idobjeto = az.referencia INNER JOIN articulos a ON lsc.idobjeto = a.referencia INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN familias f ON a.codfamilia = f.codfamilia")
        q.setWhere("tiposincro = 'Enviar productos' AND NOT sincronizado AND website = 'AMAZON'")

        return q

    def get_serializer(self):
        serializer = ProductFeedSerializer()
        serializer.msg_type = self.get_msgtype()
        serializer.parent_serializer = ParentProductSerializer()
        serializer.child_serializer = self.get_child_serializer()

        return serializer

    def get_child_serializer(self):
        return ProductSerializer()

    def get_msgtype(self):
        return 'Product'

    def get_feedtype(self):
        return '_POST_PRODUCT_DATA_'

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = true WHERE id IN ({})".format(','.join([str(key) for key in self.ids])))
        qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo s SET ptesincro = false WHERE ptesincro AND (SELECT COUNT(lsc.id) FROM lineassincro_catalogo lsc WHERE lsc.idsincro = s.idsincro AND NOT sincronizado) = 0")

        qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincroarticulo = true, idlog_articulo = (SELECT id FROM az_logamazon WHERE idamazon = '{}') WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep
