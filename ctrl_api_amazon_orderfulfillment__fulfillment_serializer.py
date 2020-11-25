from controllers.base.default.serializers.default_serializer import DefaultSerializer


class FulfillmentSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")

        self.set_string_relation("OrderFulfillment//MerchantOrderID", "s.coddocumento")
        # self.set_string_relation("OrderFulfillment//MerchantFulfillmentID", "c.codigo")
        self.set_string_value("OrderFulfillment//FulfillmentDate", self.get_fulfillment_date())

        transportista = self.init_data['e.transportista']
        if transportista in self.get_carrier_codes():
            self.set_string_value("OrderFulfillment//FulfillmentData//CarrierCode", transportista)
        else:
            self.set_string_value("OrderFulfillment//FulfillmentData//CarrierName", transportista)

        self.set_string_relation("OrderFulfillment//FulfillmentData//ShippingMethod", "e.metodoenvioidl")
        self.set_string_relation("OrderFulfillment//FulfillmentData//ShipperTrackingNumber", "s.numalbaranmrw")

        return True

    def get_carrier_codes(self):
        return ['USPS', 'UPS', 'FedEx', 'DHL', 'Fastway', 'GLS', 'Go!', 'Hermes Logistik Gruppe', 'Royal Mail', 'Parcelforce', 'City Link', 'TNT', 'Target', 'SagawaExpress', 'NipponExpress', 'YamatoTransport']

    def get_fulfillment_date(self):
        return '{}T00:00:00.000Z'.format(self.init_data['p.fechapreparacion'])
