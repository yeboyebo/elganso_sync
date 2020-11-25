from abc import ABC
from YBLEGACY import qsatype

from controllers.api.amazon.feeds.controllers.az_feeds_upload import AzFeedsUpload
from controllers.api.amazon.orderfulfillment.serializers.fulfillment_serializer import FulfillmentSerializer


class AzOrderFulfillmentUpload(AzFeedsUpload, ABC):

    def __init__(self, params=None):
        super().__init__("azorderfulfillmentupload", params)

        self.id_field = 'azv.idamazon'

    def get_query(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("azv.idamazon, s.coddocumento, s.numalbaranmrw, e.transportista, e.metodoenvioidl, p.fechapreparacion, p.horapreparacion")
        q.setFrom("az_ventasamazon azv INNER JOIN idl_ecommerce e ON azv.idtpv_comanda = e.idtpv_comanda INNER JOIN eg_seguimientoenvios s ON e.codcomanda = s.coddocumento INNER JOIN idl_preparaciones p on p.idpreparacion = e.idpreparacion")
        q.setWhere("NOT azv.envioinformado AND s.numalbaranmrw IS NOT NULL AND s.numalbaranmrw <> '' LIMIT 1")

        return q

    def after_sync(self, response_data=None):
        amazon_id = super().after_sync(response_data)

        if not amazon_id:
            return self.large_sleep

        qsatype.FLSqlQuery().execSql("UPDATE az_ventasamazon SET envioinformado = true WHERE idamazon IN ('{}')".format("','".join(self.referencias)))

        return self.small_sleep

    def get_child_serializer(self):
        return FulfillmentSerializer()

    def get_msgtype(self):
        return 'OrderFulfillment'

    def get_feedtype(self):
        return '_POST_ORDER_FULFILLMENT_DATA_'
