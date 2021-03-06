from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.orderacknowledgement.serializers.acknowledgement_serializer import AcknowledgementSerializer


class AzOrderAcknowledgementUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azorderacknowledgementupload", params)

        self.id_field = 'azv.idamazon'

        self.small_sleep = 10
        self.large_sleep = 180
        self.no_sync_sleep = 300

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("azv.idamazon, c.codigo")
        q.setFrom("az_ventasamazon azv INNER JOIN tpv_comandas c ON azv.idtpv_comanda = c.idtpv_comanda")
        q.setWhere("azv.lineassincronizadas AND NOT pedidoinformado LIMIT 1")

        return q

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_ventasamazon SET pedidoinformado = true WHERE idamazon IN ('{}')".format("','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return AcknowledgementSerializer()

    def get_msgtype(self):
        return 'OrderAcknowledgement'

    def get_feedtype(self):
        return '_POST_ORDER_ACKNOWLEDGEMENT_DATA_'
