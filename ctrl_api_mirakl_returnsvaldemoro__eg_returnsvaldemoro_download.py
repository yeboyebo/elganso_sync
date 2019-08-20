from abc import ABC
from YBLEGACY import qsatype
import json
import xmltodict

from controllers.base.mirakl.returnsvaldemoro.controllers.returnsvaldemoro_download import ReturnsValdemoroDownload
from controllers.api.mirakl.returns.serializers.return_serializer import ReturnSerializer
from models.flfact_tpv.objects.egreturn_raw import EgReturn

class EgMiraklReturnsValdemoroDownload(ReturnsValdemoroDownload, ABC):

    returns_url = "https://marketplace.elcorteingles.es/api/messages?start_date={}"
    returns_test_url = "https://marketplace.elcorteingles.es/api/messages?start_date={}"

    def __init__(self, params=None):
        super().__init__("egmiraklreturnsvaldemoro", params)

        self.set_sync_params({
            "auth": "a83379cd-1f31-4b05-8175-5c5173620a4a",
            "test_auth": "a83379cd-1f31-4b05-8175-5c5173620a4a"
        })

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