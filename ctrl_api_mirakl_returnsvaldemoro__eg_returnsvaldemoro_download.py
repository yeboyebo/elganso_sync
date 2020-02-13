from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict

from controllers.base.mirakl.returnsvaldemoro.controllers.returnsvaldemoro_download import ReturnsValdemoroDownload
from controllers.api.mirakl.returns.serializers.return_serializer import ReturnSerializer
from models.flfact_tpv.objects.egreturn_raw import EgReturn


class EgMiraklReturnsValdemoroDownload(ReturnsValdemoroDownload, ABC):

    def __init__(self, params=None):
        super().__init__("egmiraklreturnsvaldemoro", params)

        returns_params = self.get_param_sincro('miraklReturnsValdemoroDownload')
        self.returns_url = returns_params['url']
        self.returns_test_url = returns_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def masAccionesProcessData(self, eciweb_data):
        print("entra masAccionesProcessData")
        eciweb_data["datosdevol"] = json.loads(json.dumps(xmltodict.parse(eciweb_data["datosdevol"])))
        return_data = self.get_return_serializer().serialize(eciweb_data)

        if not return_data:
            return False

        return_data["valdemoro"] = True
        objReturn = EgReturn(return_data)
        objReturn.save()

        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnSerializer()
