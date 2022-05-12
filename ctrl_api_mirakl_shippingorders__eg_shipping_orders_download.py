from YBLEGACY import qsatype

from controllers.base.mirakl.orders.controllers.shipping_orders_download import ShippingOrdersDownload
from controllers.api.mirakl.shippingorders.serializers.egorder_serializer import EgOrderSerializer

class EgMiraklShippingOrdersDownload(ShippingOrdersDownload):

    def __init__(self, params=None):
        super().__init__("egmiraklshippingorders", params)

        shipping_params = self.get_param_sincro('miraklShippingOrdersDownload')
        self.shipping_url = shipping_params['url']
        self.shipping_test_url = shipping_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def get_order_serializer(self):
        return EgOrderSerializer()

    def get_data(self):
        shipping_url = self.shipping_url if self.driver.in_production else self.shipping_test_url

        order_ids = self.get_order_ids()
        print("/////////ORDER IDS: ", order_ids)
        if not order_ids or order_ids == "NOIDS":
            return {"orders": [], "total_count": 0}
        print("////////77URL_ ", shipping_url.format(",".join(order_ids)))

        return {"orders": [{'quote_id': None, 'shipping_type_code': 'HD', 'currency_iso_code': 'EUR', 'can_cancel': False, 'price': 69.9, 'has_incident': False, 'has_invoice': False, 'leadtime_to_ship': 5, 'commercial_id': '20200314115017-UATG5542230851', 'total_commission': 0.0, 'order_state_reason_code': None, 'order_state_reason_label': None, 'paymentType': '1', 'total_price': 69.9, 'created_date': '2020-03-14T10:51:53Z', 'payment_workflow': 'PAY_ON_ACCEPTANCE', 'shipping_zone_code': '180032032358', 'shipping_company': None, 'fulfillment': {'center': {'code': 'DEFAULT'}}, 'shipping_zone_label': 'Península y Baleares', 'hannel': None, 'order_id': '20200314115017-UATG5542230851-A', 'transaction_date': '2020-03-14T12:15:02.742Z', 'shipping_price': 0.0, 'promotions': {'total_deduced_amount': 0, 'applied_promotions': []}, 'order_lines': [{'refunds': [], 'quantity': 1, 'product_sku': '8445005239871', 'commission_taxes': [{'rate': 21.0, 'code': 'TAXDEFAULT', 'amount': 0.0}], 'category_code': '00234', 'commission_fee': 0.0, 'can_refund': True, 'order_line_state_reason_code': None, 'order_line_additional_fields': [], 'shipping_taxes': [], 'offer_state_code': '11', 'product_medias': [], 'total_price': 69.9, 'total_commission': 0.0, 'category_label': 'Moda', 'product_title': 'Chino de hombre slim en color piedra', 'shipped_date': None, 'created_date': '2020-03-14T10:51:53Z', 'commission_vat': 0.0, 'shipping_price_additional_unit': None, 'shipping_price': 0.0, 'cancelations': [], 'commission_rate_vat': 21.0, 'offer_id': 16043023, 'order_line_state': 'SHIPPING', 'price': 69.9, 'promotions': [], 'price_additional_info': None, 'taxes': [], 'received_date': None, 'price_unit': 69.9, 'shipping_price_unit': None, 'offer_sku': '8445005239871', 'order_line_index': 1, 'last_updated_date': '2020-03-14T11:15:09Z', 'description': None, 'order_line_state_reason_label': None, 'debited_date': '2020-03-14T11:15:09Z', 'order_line_id': '20200314115017-UATG5542230851-A-1'}], 'shipping_deadline': '2020-03-19T10:51:53.349Z', 'order_additional_fields': [{'type': 'STRING', 'code': 'codigo-cesta', 'value': '2007478001319'}, {'type': 'STRING', 'code': 'fecha-emision', 'value': '2020-03-14'}, {'type': 'STRING', 'code': 'fecha-maxima-entrega', 'value': '2020-03-21'}, {'type': 'STRING', 'code': 'talon-venta', 'value': '02690121'}], 'shipping_type_label': 'Entrega a domicilio', 'payment_type': '1', 'order_state': 'SHIPPING', 'customer': {'civility': None, 'lastname': 'PIRES', 'firstname': 'CLORINDA', 'customer_id': 'UATG5542230851', 'shipping_address': {'country': 'ESPAñA', 'lastname': 'PIRES GOMES', 'city': 'MADRID', 'additional_info': '', 'company': None, 'country_iso_code': None, 'firstname': 'CLORINDA', 'state': None, 'street_1': 'CL CL UCEDA 20 P2', 'zip_code': '28053', 'phone': '686142184', 'phone_secondary': '', 'street_2': '  '}, 'billing_address': {'country': '011', 'lastname': 'PIRES GOMES', 'city': 'MADRID', 'company': None, 'country_iso_code': None, 'firstname': 'CLORINDA', 'state': None, 'street_1': 'CL CL UCEDA 20 P2', 'zip_code': '28053', 'phone': '686142184', 'phone_secondary': '', 'street_2': '  '}, 'locale': None}, 'shipping_tracking': None, 'shipping_tracking_url': None, 'shipping_carrier_code': None, 'last_updated_date': '2020-03-14T11:15:11Z', 'customer_debited_date': '2020-03-14T11:15:09.141Z', 'has_customer_message': False, 'acceptance_decision_date': '2020-03-14T10:56:01Z'}], "total_count": 1}
        result = self.send_request("get", url=shipping_url.format(",".join(order_ids)))
        return result