from controllers.base.default.serializers.default_serializer import DefaultSerializer


class FulfillmentSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")

        self.set_string_relation("OrderFulfillment//MerchantOrderID", "c.codigo")
        # Codigo de nose, envio interno? Opcional
        self.set_string_relation("OrderFulfillment//MerchantFulfillmentID", "c.codigo")
        # Fecha de envio Opcional 2002-05-01T15:36:33-08:00
        self.set_string_relation("OrderFulfillment//FulfillmentDate", "c.codigo")

        # Transportista Todo esto opcional
        transportista = None
        if transportista in self.get_carrier_codes():
            self.set_string_relation("OrderFulfillment//FulfillmentData//CarrierCode", "c.codigo")
        else:
            self.set_string_relation("OrderFulfillment//FulfillmentData//CarrierName", "c.codigo")
        # Shipping Method String
        self.set_string_relation("OrderFulfillment//FulfillmentData//ShippingMethod", "c.codigo")
        # TrackingNumber
        self.set_string_relation("OrderFulfillment//FulfillmentData//ShipperTrackingNumber", "c.codigo")

        return True

    def get_carrier_codes(self):
        return ['USPS', 'UPS', 'FedEx', 'DHL', 'Fastway', 'GLS', 'Go!', 'Hermes Logistik Gruppe', 'Royal Mail', 'Parcelforce', 'City Link', 'TNT', 'Target', 'SagawaExpress', 'NipponExpress', 'YamatoTransport']
