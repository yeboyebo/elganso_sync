from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgOrderLine(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_lineascomanda", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))
        self.set_data_value("numlinea", self.get_numlinea())

        self.dump_to_cursor()
        idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", self.cursor)
        self.set_string_value("idsincro", idsincro, max_characters=30)

    def get_numlinea(self):
        numlinea = parseInt(qsatype.FLUtil.quickSqlSelect("tpv_comandas", "count(*)", "idtpv_comanda = {}".format(self.data["idtpv_comanda"])))

        if isNaN(numlinea):
            numlinea = 0

        return numlinea + 1
