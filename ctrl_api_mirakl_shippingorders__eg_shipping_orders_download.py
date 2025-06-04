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

    def process_data(self, data):
        return True

    def get_data(self):
        
        return {
    "orders": [
        {
            "acceptance_decision_date": "2025-01-20T10:31:04Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900679567820250120112639_1",
            "created_date": "2025-01-20T10:26:56Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "ALCORCON",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "PEPA",
                    "lastname": "Fernández Romero",
                    "phone": "696671389",
                    "phone_secondary": "696671389",
                    "state": "None",
                    "street_1": "CL Los Arces 3 P.5 Pt.1 ",
                    "street_2": "  ",
                    "zip_code": "28922"
                },
                "civility": "None",
                "customer_id": "0107515280",
                "firstname": "Josefa",
                "lastname": "Fernandez",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "ALCORCON",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Pepa",
                    "lastname": "Fernández Romero",
                    "phone": "696671389",
                    "state": "None",
                    "street_1": "CL PRINCESA DOÑA SOFIA 1 P.1º Esc.iz Pt.B Telefonillo",
                    "street_2": "",
                    "zip_code": "28924"
                }
            },
            "customer_debited_date": "2025-01-20T10:56:23.275Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T10:56:23Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2502088002108"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06795678"
                }
            ],
            "order_id": "00100900679567820250120112639_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00344",
                    "category_label": "Moda Calzado MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:26:56Z",
                    "debited_date": "2025-01-20T10:56:23Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T10:56:23Z",
                    "offer_id": 36871877,
                    "offer_sku": "8445005601371",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900679567820250120112639_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 39.90,
                    "price_additional_info": "None",
                    "price_unit": 39.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005601371",
                    "product_title": "Zapatillas deportivas unisex estilo running",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 39.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "006",
            "payment_type": "006",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 39.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 39.90,
            "transaction_date": "2025-01-20T11:56:22.600Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:31:04Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900675685420250120112807_1",
            "created_date": "2025-01-20T10:28:12Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "PAMPLONA/IRUÑA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Milagros",
                    "lastname": "San Miguel Iragui",
                    "phone": "680794318",
                    "state": "None",
                    "street_1": "AV PIO XII 33 ",
                    "street_2": "  ",
                    "zip_code": "31008"
                },
                "civility": "None",
                "customer_id": "0284588399",
                "firstname": "Milagros",
                "lastname": "San Miguel",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "PAMPLONA/IRUÑA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Milagros",
                    "lastname": "San Miguel ",
                    "phone": "680794318",
                    "state": "None",
                    "street_1": "AV PIO XII 33 ",
                    "street_2": "",
                    "zip_code": "31008"
                }
            },
            "customer_debited_date": "2025-01-20T10:56:16.375Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T10:56:16Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020008622"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06756854"
                }
            ],
            "order_id": "00100900675685420250120112807_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00336",
                    "category_label": "Moda Mujer MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:28:13Z",
                    "debited_date": "2025-01-20T10:56:16Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T10:56:16Z",
                    "offer_id": 37498642,
                    "offer_sku": "8445005614395",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900675685420250120112807_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 99.90,
                    "price_additional_info": "None",
                    "price_unit": 99.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005614395",
                    "product_title": "Plumífero de mujer largo con cierre de cremallera",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 99.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "008",
            "payment_type": "008",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 99.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 99.90,
            "transaction_date": "2025-01-20T11:56:15.873Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:36:02Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900691445020250120113237_1",
            "created_date": "2025-01-20T10:32:56Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "MALAGA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "FLORINDO",
                    "lastname": "LOPEZ DELGADO",
                    "phone": "658325358",
                    "phone_secondary": "658325358",
                    "state": "None",
                    "street_1": "PS MARTIRICOS 15 Pt.27K ",
                    "street_2": "  ",
                    "zip_code": "29009"
                },
                "civility": "None",
                "customer_id": "0169599958",
                "firstname": "Florindo",
                "lastname": "Lopez",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "MALAGA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "FLORINDO",
                    "lastname": "LOPEZ DELGADO",
                    "phone": "658325358",
                    "state": "None",
                    "street_1": "PS MARTIRICOS 15 Pt.27K Edif.2 ",
                    "street_2": "",
                    "zip_code": "29009"
                }
            },
            "customer_debited_date": "2025-01-20T11:05:39.622Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:05:39Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2502050001852"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06914450"
                }
            ],
            "order_id": "00100900691445020250120113237_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:32:56Z",
                    "debited_date": "2025-01-20T11:05:39Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:05:39Z",
                    "offer_id": 36870650,
                    "offer_sku": "8445005613985",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900691445020250120113237_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 24.90,
                    "price_additional_info": "None",
                    "price_unit": 24.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005613985",
                    "product_title": "Jogger de hombre slim liso",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 24.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "006",
            "payment_type": "006",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 24.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 24.90,
            "transaction_date": "2025-01-20T12:05:39.308Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:41:01Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900661855320250120113701_1",
            "created_date": "2025-01-20T10:37:15Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "LA COMA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Miguel",
                    "lastname": "Mena Navarro",
                    "phone": "653354720",
                    "state": "None",
                    "street_1": "RD Narciso Monturiol 17 ",
                    "street_2": "  ",
                    "zip_code": "46980"
                },
                "civility": "None",
                "customer_id": "0124417296",
                "firstname": "Miguel",
                "lastname": "Mena",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "LA COMA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Miguel",
                    "lastname": "Mena Navarro",
                    "phone": "653354720",
                    "state": "None",
                    "street_1": "RD Narciso Monturiol 17 P.2 Pt.9 Edif.1 MENA ARQUITECTO",
                    "street_2": "",
                    "zip_code": "46980"
                }
            },
            "customer_debited_date": "2025-01-20T11:14:40.640Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:14:40Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020009195"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06618553"
                }
            ],
            "order_id": "00100900661855320250120113701_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00344",
                    "category_label": "Moda Calzado MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:37:15Z",
                    "debited_date": "2025-01-20T11:14:40Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:14:40Z",
                    "offer_id": 37710118,
                    "offer_sku": "8445005620167",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900661855320250120113701_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 59.90,
                    "price_additional_info": "None",
                    "price_unit": 59.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005620167",
                    "product_title": "Mocasines de hombre de ante liso",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 59.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "004",
            "payment_type": "004",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 59.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 59.90,
            "transaction_date": "2025-01-20T12:14:40.298Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:46:01Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00109410111795420250120113507_1",
            "created_date": "2025-01-20T10:40:46Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "OVIEDO",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Ricardo Miguel",
                    "lastname": "Arbizu Rodriguez",
                    "phone": "+34699794684",
                    "state": "None",
                    "street_1": "CL BENJAMIN ORTIZ 11 ",
                    "street_2": "  ",
                    "zip_code": "33011"
                },
                "civility": "None",
                "customer_id": "0074320607",
                "firstname": "Ricardo Miguel",
                "lastname": "Arbizu",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "llamar antes de efectuar entrega, martes y jueves turno mañanas, resto de dias tardes. 666336506",
                    "city": "OVIEDO",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Ricardo Miguel",
                    "lastname": "Arbizu Rodriguez",
                    "phone": "699794684",
                    "state": "None",
                    "street_1": "CL BENJAMIN ORTIZ 11 P.5 Pt.e ",
                    "street_2": "",
                    "zip_code": "33011"
                }
            },
            "customer_debited_date": "2025-01-20T11:19:28.347Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:19:28Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2502068001982"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-28"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "01117954"
                }
            ],
            "order_id": "00109410111795420250120113507_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:40:46Z",
                    "debited_date": "2025-01-20T11:19:28Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:19:28Z",
                    "offer_id": 37006219,
                    "offer_sku": "8445005584636",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00109410111795420250120113507_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 139.90,
                    "price_additional_info": "None",
                    "price_unit": 139.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005584636",
                    "product_title": "Americana de hombre de lana con motivo de espiga",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 139.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "006",
            "payment_type": "006",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 139.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 139.90,
            "transaction_date": "2025-01-20T12:19:27.916Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:51:02Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900618210320250120114350_1",
            "created_date": "2025-01-20T10:43:55Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "ELCHE/ELX",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Diana Gabriela",
                    "lastname": "Petrisor Petrisor",
                    "phone": "661010066",
                    "state": "None",
                    "street_1": "CL JOSE MAS ESTEVE 34 ",
                    "street_2": "  ",
                    "zip_code": "03201"
                },
                "civility": "None",
                "customer_id": "0288372741",
                "firstname": "Diana Gabriela",
                "lastname": "Petrisor ",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "ELCHE/ELX",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Diana Gabriela",
                    "lastname": "Petrisor Petrisor",
                    "phone": "661010066",
                    "state": "None",
                    "street_1": "CL JOSE MAS ESTEVE 34 P.3  Pt.Izq  ",
                    "street_2": "",
                    "zip_code": "03201"
                }
            },
            "customer_debited_date": "2025-01-20T11:20:24.637Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:20:29Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020009393"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06182103"
                }
            ],
            "order_id": "00100900618210320250120114350_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:43:55Z",
                    "debited_date": "2025-01-20T11:20:24Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:20:24Z",
                    "offer_id": 36802278,
                    "offer_sku": "8445005610724",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900618210320250120114350_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 44.90,
                    "price_additional_info": "None",
                    "price_unit": 44.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005610724",
                    "product_title": "Sudadera de hombre con logo Ganso y cuello redondo",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 44.90
                },
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00344",
                    "category_label": "Moda Calzado MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:43:55Z",
                    "debited_date": "2025-01-20T11:20:24Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:20:24Z",
                    "offer_id": 36871850,
                    "offer_sku": "8445005622383",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900618210320250120114350_1-A-2",
                    "order_line_index": 2,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 44.90,
                    "price_additional_info": "None",
                    "price_unit": 44.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005622383",
                    "product_title": "Zapatillas deportivas de hombre estilo retro",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 44.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "004",
            "payment_type": "004",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 89.80,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 89.80,
            "transaction_date": "2025-01-20T12:20:23.682Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:51:02Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900664514020250120114453_1",
            "created_date": "2025-01-20T10:45:01Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "TUDELA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "M. Concepcion",
                    "lastname": "Fernandez Amez",
                    "phone": "652049221",
                    "state": "None",
                    "street_1": "CL MIGUEL SERVET 2 ",
                    "street_2": "  ",
                    "zip_code": "31500"
                },
                "civility": "None",
                "customer_id": "0124667585",
                "firstname": "M. Concepcion",
                "lastname": "Fernandez",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "TUDELA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "ADRIAN",
                    "lastname": "HERRERO FERNANDEZ",
                    "phone": "658058295",
                    "state": "None",
                    "street_1": "CL MIGUEL SERVET 2 P.2A ",
                    "street_2": "",
                    "zip_code": "31500"
                }
            },
            "customer_debited_date": "2025-01-20T11:20:11.161Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:20:23Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020009555"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06645140"
                }
            ],
            "order_id": "00100900664514020250120114453_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:45:01Z",
                    "debited_date": "2025-01-20T11:20:11Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:20:11Z",
                    "offer_id": 36870714,
                    "offer_sku": "8445005595731",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900664514020250120114453_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 54.90,
                    "price_additional_info": "None",
                    "price_unit": 54.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005595731",
                    "product_title": "Jersey de hombre con cuello camionero",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 54.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "006",
            "payment_type": "006",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 54.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 54.90,
            "transaction_date": "2025-01-20T12:20:10.612Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:56:01Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900627607020250120115135_1",
            "created_date": "2025-01-20T10:51:45Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "SIGÜENZA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Jose Javier",
                    "lastname": "Cerezo Cabrera",
                    "phone": "607202070",
                    "state": "None",
                    "street_1": "ED Registro de la propiedad de sigüenza S/N ",
                    "street_2": "  ",
                    "zip_code": "19250"
                },
                "civility": "None",
                "customer_id": "0132445834",
                "firstname": "Jose Javier",
                "lastname": "Cerezo",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "SIGÜENZA",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "ANA",
                    "lastname": "GUERRERO ALONSO",
                    "phone": "607202070",
                    "state": "None",
                    "street_1": "ED Registro de la propiedad de sigüenza S/N registro propiedad",
                    "street_2": "",
                    "zip_code": "19250"
                }
            },
            "customer_debited_date": "2025-01-20T11:24:28.793Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:24:33Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020009877"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06276070"
                }
            ],
            "order_id": "00100900627607020250120115135_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:51:45Z",
                    "debited_date": "2025-01-20T11:24:28Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:24:28Z",
                    "offer_id": 37701840,
                    "offer_sku": "8445005604402",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900627607020250120115135_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 39.90,
                    "price_additional_info": "None",
                    "price_unit": 39.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005604402",
                    "product_title": "Chino de hombre de invierno regular",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 39.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "006",
            "payment_type": "006",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 39.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 39.90,
            "transaction_date": "2025-01-20T12:24:27.901Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T10:56:02Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900662435120250120115201_1",
            "created_date": "2025-01-20T10:52:09Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "MADRID",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Alvaro",
                    "lastname": "De la Fuente Martin",
                    "phone": "696723272",
                    "state": "None",
                    "street_1": "CL Alcalde sainz de baranda 8 ",
                    "street_2": "  ",
                    "zip_code": "28009"
                },
                "civility": "None",
                "customer_id": "0157618349",
                "firstname": "Alvaro",
                "lastname": "De la Fuente",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "MADRID",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Álvaro",
                    "lastname": "de la Fuente Martín",
                    "phone": "696723272",
                    "state": "None",
                    "street_1": "CL Alcalde sainz de baranda 8 P.4 Pt.D ",
                    "street_2": "",
                    "zip_code": "28009"
                }
            },
            "customer_debited_date": "2025-01-20T11:24:23.754Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:24:24Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020009569"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06624351"
                }
            ],
            "order_id": "00100900662435120250120115201_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T10:52:09Z",
                    "debited_date": "2025-01-20T11:24:23Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:24:23Z",
                    "offer_id": 37450959,
                    "offer_sku": "8445005598237",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900662435120250120115201_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 44.90,
                    "price_additional_info": "None",
                    "price_unit": 44.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005598237",
                    "product_title": "Sudadera de hombre de cuello gaja garment dyed",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 44.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "004",
            "payment_type": "004",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 44.90,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 44.90,
            "transaction_date": "2025-01-20T12:24:22.985Z"
        },
        {
            "acceptance_decision_date": "2025-01-20T11:16:01Z",
            "can_cancel": False,
            "can_shop_ship": "True",
            "channel": {
                "code": "eciStore",
                "label": "ECI - España"
            },
            "commercial_id": "00100900613982620250120115915_1",
            "created_date": "2025-01-20T11:07:45Z",
            "currency_iso_code": "EUR",
            "customer": {
                "billing_address": {
                    "city": "MADRID",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Jorge",
                    "lastname": "Esteve Bru",
                    "phone": "630040334",
                    "state": "None",
                    "street_1": "AV MONASTERIO DE SILOS 80 ",
                    "street_2": "  ",
                    "zip_code": "28049"
                },
                "civility": "None",
                "customer_id": "0223916578",
                "firstname": "Jorge",
                "lastname": "Esteve",
                "locale": "None",
                "shipping_address": {
                    "additional_info": "",
                    "city": "MADRID",
                    "company": "None",
                    "company_2": "None",
                    "country": "ES",
                    "country_iso_code": "None",
                    "firstname": "Jorge",
                    "lastname": "Esteve Bru",
                    "phone": "630040334",
                    "state": "None",
                    "street_1": "AV MONASTERIO DE SILOS 80 P.4 Esc.A Pt.1 ",
                    "street_2": "",
                    "zip_code": "28049"
                }
            },
            "customer_debited_date": "2025-01-20T11:43:54.209Z",
            "customer_directly_pays_seller": False,
            "delivery_date": "None",
            "fulfillment": {
                "center": {
                    "code": "DEFAULT"
                }
            },
            "fully_refunded": False,
            "has_customer_message": False,
            "has_incident": False,
            "has_invoice": False,
            "last_updated_date": "2025-01-20T11:43:54Z",
            "leadtime_to_ship": 1,
            "order_additional_fields": [
                {
                    "code": "codigo-cesta",
                    "type": "STRING",
                    "value": "2592020009954"
                },
                {
                    "code": "fecha-emision",
                    "type": "STRING",
                    "value": "20250120"
                },
                {
                    "code": "fecha-maxima-entrega",
                    "type": "STRING",
                    "value": "2025-01-27"
                },
                {
                    "code": "talon-venta",
                    "type": "STRING",
                    "value": "06139826"
                }
            ],
            "order_id": "00100900613982620250120115915_1-A",
            "order_lines": [
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T11:07:45Z",
                    "debited_date": "2025-01-20T11:43:54Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:43:54Z",
                    "offer_id": 38272560,
                    "offer_sku": "8445005543091",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900613982620250120115915_1-A-1",
                    "order_line_index": 1,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 39.90,
                    "price_additional_info": "None",
                    "price_unit": 39.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005543091",
                    "product_title": "Pantalón de hombre de cuadro tartan en dos colores",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 39.90
                },
                {
                    "can_refund": "True",
                    "cancelations": [],
                    "category_code": "00342",
                    "category_label": "Moda Hombre MarketPlace",
                    "commission_fee": 0.00,
                    "commission_rate_vat": 21.0000,
                    "commission_taxes": [
                        {
                            "amount": 0.00,
                            "code": "TAXDEFAULT",
                            "rate": 21.0000
                        }
                    ],
                    "commission_vat": 0.00,
                    "created_date": "2025-01-20T11:07:45Z",
                    "debited_date": "2025-01-20T11:43:54Z",
                    "description": "None",
                    "fees": [],
                    "last_updated_date": "2025-01-20T11:43:54Z",
                    "offer_id": 37701814,
                    "offer_sku": "8445005583691",
                    "offer_state_code": "11",
                    "order_line_additional_fields": [
                        {
                            "code": "recycling-service",
                            "type": "BOOLEAN",
                            "value": "False"
                        }
                    ],
                    "order_line_id": "00100900613982620250120115915_1-A-2",
                    "order_line_index": 2,
                    "order_line_state": "SHIPPING",
                    "order_line_state_reason_code": "None",
                    "order_line_state_reason_label": "None",
                    "price": 139.90,
                    "price_additional_info": "None",
                    "price_unit": 139.90,
                    "product_medias": [],
                    "product_shop_sku": "None",
                    "product_sku": "8445005583691",
                    "product_title": "Abrigo de hombre de plumas largo",
                    "promotions": [],
                    "quantity": 1,
                    "received_date": "None",
                    "refunds": [],
                    "shipped_date": "None",
                    "shipping_from": {
                        "address": {
                            "city": "None",
                            "country_iso_code": "ESP",
                            "state": "None",
                            "street_1": "None",
                            "street_2": "None",
                            "zip_code": "None"
                        },
                        "warehouse": "None"
                    },
                    "shipping_price": 0.00,
                    "shipping_price_additional_unit": "None",
                    "shipping_price_unit": "None",
                    "shipping_taxes": [],
                    "taxes": [],
                    "total_commission": 0.00,
                    "total_price": 139.90
                }
            ],
            "order_refunds": "None",
            "order_state": "SHIPPING",
            "order_state_reason_code": "None",
            "order_state_reason_label": "None",
            "order_tax_mode": "TAX_EXCLUDED",
            "order_taxes": "None",
            "paymentType": "006",
            "payment_type": "006",
            "payment_workflow": "PAY_ON_ACCEPTANCE",
            "price": 179.80,
            "promotions": {
                "applied_promotions": [],
                "total_deduced_amount": 0
            },
            "quote_id": "None",
            "shipping_carrier_code": "None",
            "shipping_carrier_standard_code": "None",
            "shipping_company": "None",
            "shipping_deadline": "2025-01-21T22:59:59.999Z",
            "shipping_price": 0.00,
            "shipping_pudo_id": "None",
            "shipping_tracking": "None",
            "shipping_tracking_url": "None",
            "shipping_type_code": "HD",
            "shipping_type_label": "Entrega a domicilio",
            "shipping_type_standard_code": "CU_ADD-STD",
            "shipping_zone_code": "180032032358",
            "shipping_zone_label": "Península y Baleares",
            "total_commission": 0.00,
            "total_price": 179.80,
            "transaction_date": "2025-01-20T12:43:53.282Z"
        }
    ],
    "total_count": 34
}