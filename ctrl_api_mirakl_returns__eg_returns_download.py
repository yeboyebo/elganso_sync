from YBLEGACY import qsatype
import xmltodict
import json

from controllers.base.mirakl.returns.controllers.returns_download import ReturnsDownload
from controllers.api.mirakl.returns.serializers.return_serializer import ReturnSerializer
from models.flfact_tpv.objects.egreturn_raw import EgReturn


class EgMiraklReturnsDownload(ReturnsDownload):

    def __init__(self, params=None):
        super().__init__("egmiraklreturns", params)

        returns_params = self.get_param_sincro('miraklReturnsDownload')
        self.returns_url = returns_params['url']
        self.returns_test_url = returns_params['test_url']

        self.set_sync_params(self.get_param_sincro('mirakl'))

    def masAccionesProcessData(self, eciweb_data):
        eciweb_data["datosdevol"] = json.loads(json.dumps(xmltodict.parse(eciweb_data["datosdevol"])))
        return_data = self.get_return_serializer().serialize(eciweb_data)

        if not return_data:
            return

        return_data["valdemoro"] = False
        objReturn = EgReturn(return_data)
        objReturn.save()

        return objReturn.cursor.valueBuffer("idtpv_comanda")

    def get_return_serializer(self):
        return ReturnSerializer()
