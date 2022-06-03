from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel
from models.flfact_tpv.objects.egrefound_lineasdevolucioneswebtienda_raw import EgRefoundLineasDevolucionesWebTienda

class Mg2RefoundLine(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_lineascomanda", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)

        return cursor

    def get_children_data(self):
        if "lineadevolucionwebtienda" in self.data["children"]:
            if self.data["children"]["lineadevolucionwebtienda"]:
                self.children.append(EgRefoundLineasDevolucionesWebTienda(self.data["children"]["lineadevolucionwebtienda"]))

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))
        self.set_data_value("numlinea", self.get_numlinea())

        self.dump_to_cursor()
        idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", self.cursor)
        self.set_string_value("idsincro", idsincro, max_characters=30)
        self.crear_registro_movistock(self.cursor, parent_cursor)
        self.actualizar_cantidad_devuelta(self.cursor, parent_cursor)

    def crear_registro_movistock(self, cursor, parent_cursor):
        codtiendaentrega = "AWEB"
        if "codtiendaentrega" in self.data and parseFloat(cursor.valueBuffer("cantidad")) < 0:
            codtiendaentrega = str(self.data["codtiendaentrega"])

        idStock = str(qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "barcode = '" + str(cursor.valueBuffer("barcode")) + "' AND codalmacen = 'AWEB'"))
        if not idStock or str(idStock) == "None":
            raise NameError("No se ha encontrado idstock para el barcode: " + str(cursor.valueBuffer("barcode")))
            return False

        curMoviStock = qsatype.FLSqlCursor("movistock")
        curMoviStock.setModeAccess(curMoviStock.Insert)
        curMoviStock.refreshBuffer()
        curMoviStock.setValueBuffer("idlineaco", cursor.valueBuffer("idtpv_linea"))
        if str(codtiendaentrega) == "AWEB":
            curMoviStock.setValueBuffer("estado", "PTE")
        else:
            curMoviStock.setValueBuffer("estado", "HECHO")
            now = str(qsatype.Date())
            current_date = now[:10]
            current_time = now[-(8):]
            curMoviStock.setValueBuffer("fechareal", current_date)
            curMoviStock.setValueBuffer("horareal", current_time)

        if self.data["creditmemo"]:
            fecha_comanda_original = str(qsatype.FLUtil.quickSqlSelect("tpv_comandas", "fecha", "codigo = '" + str(parent_cursor.valueBuffer("codcomandadevol")) + "'"))
            hora_comanda_original = str(qsatype.FLUtil.quickSqlSelect("tpv_comandas", "hora", "codigo = '" + str(parent_cursor.valueBuffer("codcomandadevol")) + "'"))
            curMoviStock.setValueBuffer("estado", "HECHO")
            curMoviStock.setValueBuffer("fechareal", fecha_comanda_original)
            curMoviStock.setValueBuffer("horareal", hora_comanda_original)

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

    def actualizar_cantidad_devuelta(self, cursor, parent_cursor):
        idtpv_comanda_original = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(parent_cursor.valueBuffer("codcomandadevol")))

        cant_devuelta = parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "SUM(cantdevuelta)", "barcode = '{}' AND idtpv_comanda = '{}'".format(cursor.valueBuffer("barcode"), idtpv_comanda_original)))
        cant_devuelta = cant_devuelta + (cursor.valueBuffer("cantidad") * (-1))

        total_lineas_barcode = parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "COUNT(*)", "barcode = '{}' AND idtpv_comanda = '{}'".format(cursor.valueBuffer("barcode"), idtpv_comanda_original)))

        cant_linea = int(cursor.valueBuffer("cantidad") * -1)
        if total_lineas_barcode > 1:
            for i in range(cant_linea):
                idtpv_linea_sin_devolver = qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "idtpv_linea", "barcode = '{}' AND idtpv_comanda = '{}' AND cantdevuelta < cantidad".format(cursor.valueBuffer("barcode"), idtpv_comanda_original))
                qsatype.FLSqlQuery().execSql("UPDATE tpv_lineascomanda SET cantdevuelta = cantdevuelta + cantidad WHERE idtpv_linea = {}".format(idtpv_linea_sin_devolver))
        else:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_lineascomanda SET cantdevuelta = {} WHERE cantdevuelta < cantidad AND barcode = '{}' AND idtpv_comanda = {}".format(cant_devuelta, cursor.valueBuffer("barcode"), idtpv_comanda_original))

        return True
