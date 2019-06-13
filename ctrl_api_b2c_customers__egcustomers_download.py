from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.b2c.customers.serializers.egmagento_customer_serializer import EgMagentoCustomerSerializer

from models.flfactalma.objects.egmagento_customer_raw import EgMagentoCustomer


class EgCustomersDownload(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mgsynccust", driver, params)

        self.set_sync_params({
            "auth": "Basic c2luY3JvOmJVcWZxQk1ub0g=",
            "test_auth": "Basic dGVzdDp0ZXN0",
            "url": "https://www.elganso.com/syncapi/index.php/customers/unsynchronized",
            "test_url": "http://local2.elganso.com/syncapi/index.php/customers/unsynchronized"
        })

        self.origin_field = "email"

    def process_data(self, data):
        customer_data = EgMagentoCustomerSerializer().serialize(data)

        if "email" not in customer_data or not customer_data["email"] or customer_data["email"] == "":
            raise NameError("No es posible sincronizar un cliente sin email. Cliente {}".format(data["entity_id"]))

        customer = EgMagentoCustomer(customer_data)
        customer.save()

    def after_sync(self):
        self.set_sync_params({
            "url": "https://www.elganso.com/syncapi/index.php/customers/{}/synchronized",
            "test_url": "http://local2.elganso.com/syncapi/index.php/customers/{}/synchronized"
        })

        success_records = []
        error_records = [customer["email"] if "email" in customer and customer["email"] else "{}-{}".format(customer["entity_id"], customer["firstname"]) for customer in self.error_data]
        after_sync_error_records = []

        for customer in self.success_data:
            try:
                self.send_request("put", replace=[customer["entity_id"]])
                success_records.append(customer["email"])
            except Exception as e:
                self.after_sync_error(customer, e)
                after_sync_error_records.append(customer["email"])

        for customer in self.error_data:
            try:
                self.send_request("put", replace=[customer["entity_id"]])
            except Exception as e:
                self.after_sync_error(customer, e)
                after_sync_error_records.append(customer["email"])

        if success_records:
            success_records = ", ".join(success_records)
            self.log("Éxito", "Los siguientes clientes se han sincronizado correctamente: [{}]".format(success_records))

        if error_records:
            error_records = ", ".join(error_records)
            self.log("Error", "Los siguientes clientes no se han sincronizado correctamente: [{}]".format(error_records))

        if after_sync_error_records:
            after_sync_error_records = ", ".join(after_sync_error_records)
            self.log("Error", "Los siguientes clientes no se han marcado como sincronizados: [{}]".format(after_sync_error_records))

        return self.small_sleep
