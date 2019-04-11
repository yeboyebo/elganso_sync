from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgCashCount(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_arqueos", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)
        cursor.setActivatedCheckIntegrity(False)

        return cursor

    def get_parent_data(self, parent_cursor):
        self.dump_to_cursor()

        idarqueo = qsatype.FactoriaModulos.get("formRecordtpv_arqueos").iface.codigoArqueo(self.cursor)
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)
