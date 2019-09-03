from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgRefoundLine(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_lineascomanda", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)

        return cursor

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))
        self.set_data_value("numlinea", self.get_numlinea())

        self.dump_to_cursor()
        idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", self.cursor)
        self.set_string_value("idsincro", idsincro, max_characters=30)
        self.crear_registro_movistock(self.cursor)

    def crear_registro_movistock(self, cursor):

        idStock = str(qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "barcode = '" + str(cursor.valueBuffer("barcode")) + "' AND codalmacen = 'AWEB'"))

        if not idStock or str(idStock) == "None":
            return False

        curMoviStock = qsatype.FLSqlCursor("movistock")
        curMoviStock.setModeAccess(curMoviStock.Insert)
        curMoviStock.refreshBuffer()
        curMoviStock.setValueBuffer("idlineaco", cursor.valueBuffer("idtpv_linea"))
        curMoviStock.setValueBuffer("estado", "PTE")
        curMoviStock.setValueBuffer("cantidad", (parseFloat(cursor.valueBuffer("cantidad")) * (-1)))
        curMoviStock.setValueBuffer("referencia", str(cursor.valueBuffer("referencia")))
        curMoviStock.setValueBuffer("barcode", str(cursor.valueBuffer("barcode")))
        curMoviStock.setValueBuffer("idstock", idStock)
        curMoviStock.setValueBuffer("concepto", "DEVOLUCION " + str(cursor.valueBuffer("codcomanda")))
        if not curMoviStock.commitBuffer():
            return False

        return True

    def get_numlinea(self):
        numlinea = parseInt(qsatype.FLUtil.quickSqlSelect("tpv_comandas", "count(*)", "idtpv_comanda = {}".format(self.data["idtpv_comanda"])))

        if isNaN(numlinea):
            numlinea = 0

        return numlinea + 1
