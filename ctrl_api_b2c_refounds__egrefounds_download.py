from YBLEGACY import qsatype

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.b2c.refounds.serializers.egrefound_serializer import EgRefoundsSerializer

from models.flfact_tpv.objects.egrefound_raw import EgRefound


class EgRefoundsDownload(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("mgsyncdevweb", driver, params)

        self.set_sync_params(self.get_param_sincro('b2c'))
        self.set_sync_params(self.get_param_sincro('b2cRefoundsDownload'))

        self.origin_field = "refound_id"

    def process_data(self, data):
        refound_data = EgRefoundsSerializer().serialize(data)
        if not refound_data:
            return False

        refound = EgRefound(refound_data)
        refound.save()

    def after_sync(self):
        self.set_sync_params(self.get_param_sincro('b2cRefoundsDownloadSync'))

        success_records = []
        error_records = [refound["refound_id"] for refound in self.error_data]
        after_sync_error_records = []

        for refound in self.success_data:
            try:
                self.send_request("put", replace=[refound["refound_id"]])
                success_records.append(refound["refound_id"])
            except Exception as e:
                self.after_sync_error(refound, e)
                after_sync_error_records.append(refound["refound_id"])

        for refound in self.error_data:
            try:
                self.send_request("put", replace=[refound["refound_id"]])
            except Exception as e:
                self.after_sync_error(refound, e)
                after_sync_error_records.append(refound["refound_id"])

        if success_records:
            self.log("Éxito", "Las siguientes devoluciones se han sincronizado correctamente: {}".format(success_records))

        if error_records:
            self.log("Error", "Las siguientes devoluciones no se han sincronizado correctamente: {}".format(error_records))

        if after_sync_error_records:
            self.log("Error", "Las siguientes devoluciones no se han marcado como sincronizados: {}".format(after_sync_error_records))

        return self.small_sleep
