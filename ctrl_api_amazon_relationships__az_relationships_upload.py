from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.relationships.serializers.relationship_serializer import RelationshipSerializer


class AzRelationshipsUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azrelationshipsupload", params)

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("az.referencia, aa.barcode")
        q.setFrom("articulos a INNER JOIN az_articulosamazon az ON a.referencia = az.referencia INNER JOIN atributosarticulos aa ON az.referencia = aa.referencia")
        q.setWhere("az.referencia IN (SELECT referencia FROM az_articulosamazon WHERE sincroarticulo AND articulocreado AND NOT sincrorelacion AND NOT errorsincro LIMIT {}) AND barcode not in (select barcode from atributosarticulos where a.referencia = aa.referencia and aa.talla in ('35','36','37','38','39','40') and (a.codgrupomoda = '3' OR a.codgrupomoda = '5'))".format(self.driver.azQueryLimit))

        return q

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_articulosamazon SET sincrorelacion = true, idlog_relacion = (SELECT id FROM az_logamazon WHERE idamazon = '{}') WHERE referencia IN ('{}')".format(amazon_id, "','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return RelationshipSerializer()

    def get_msgtype(self):
        return 'Relationship'

    def get_feedtype(self):
        return '_POST_PRODUCT_RELATIONSHIP_DATA_'
