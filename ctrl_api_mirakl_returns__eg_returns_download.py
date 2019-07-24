from YBLEGACY import qsatype
import xmltodict
import json

from controllers.base.mirakl.returns.controllers.returns_download import ReturnsDownload
from controllers.api.mirakl.returns.serializers.return_serializer import ReturnSerializer
from models.flfact_tpv.objects.egreturn_raw import EgReturn


class EgMiraklReturnsDownload(ReturnsDownload):
    returns_url = "https://marketplace.elcorteingles.es/api/messages?start_date={}"
    returns_test_url = "https://marketplace.elcorteingles.es/api/messages?start_date={}"

    # Para Test
    #returns_url = "https://marketplace.elcorteingles.es/api/messages"
    #returns_test_url = "https://marketplace.elcorteingles.es/api/messages"

    def __init__(self, params=None):
        super().__init__("egmiraklreturns", params)

        self.set_sync_params({
            "auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e",
            "test_auth": "1737f9fc-d5fc-4130-b127-72d15ee0870e"
        })

    def masAccionesProcessData(self, eciweb_data):
        eciweb_data["datosdevol"] = json.loads(json.dumps(xmltodict.parse(eciweb_data["datosdevol"])))
        return_data = self.get_return_serializer().serialize(eciweb_data)

        if not return_data:
            return

        objReturn = EgReturn(return_data)
        objReturn.save()

        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnSerializer()
