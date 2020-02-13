from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict

from controllers.api.mirakl.returnsvaldemoro.controllers.eg_returnsvaldemoro_download import ReturnsValdemoroDownload


class EgMiraklReturnsValdemoroIdDownload(ReturnsValdemoroDownload, ABC):

    def __init__(self, params=None):
        super().__init__("egmiraklreturnsvaldemoroid", params)

        returns_params = self.get_param_sincro('miraklReturnsValdemoroIdDownload')
        self.returns_url = returns_params['url']
        self.returns_test_url = returns_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def process_all_data(self, all_data):
        if all_data["messages"] == []:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        processData = False
        for data in all_data["messages"]:
            try:
                if data["subject"] != "Devolución artículo":
                    continue

                if not data["body"].startswith("<?xml"):
                    continue

                datosDevol = json.loads(json.dumps(xmltodict.parse(data["body"])))
                tipoMsg = datosDevol["Mensaje"]["tipoMensaje"]

                if tipoMsg != "001":
                    continue

                dirRecogida = datosDevol["Mensaje"]["Recogida"]["direccionRecogida"]
                if dirRecogida != "CTRA/ANDALUCIA KM 23,5S/N,(ATT.DVD). CP: 28343. VALDEMORO":
                    continue

                processData = True
                if self.process_data(data):
                    self.success_data.append(data)
            except Exception as e:
                self.sync_error(data, e)

        if not processData:
            self.log("Éxito", "No hay datos que sincronizar")
            return False

        return True

    def get_data(self):
        returns_url = self.returns_url if self.driver.in_production else self.returns_test_url

        orderId = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'RETURN_VALDEMORO_ID'")
        if not orderId:
            orderId = "false"

        result = self.send_request("get", url=returns_url.format(orderId))
        return result

    def after_sync(self):
        if self.success_data:
            self.log("Éxito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format([order["order_id"] for order in self.success_data]))

        return self.large_sleep
