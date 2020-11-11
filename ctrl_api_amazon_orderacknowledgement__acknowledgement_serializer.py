from controllers.base.default.serializers.default_serializer import DefaultSerializer


class AcknowledgementSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")

        self.set_string_relation("OrderAcknowledgement//AmazonOrderID", "azv.idamazon")
        self.set_string_relation("OrderAcknowledgement//MerchantOrderID", "c.codigo")

        self.set_string_value("OrderAcknowledgement//StatusCode", "Success")

        return True
