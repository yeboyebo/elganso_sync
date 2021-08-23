from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgOrderLineaEcommerceExcluida(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("eg_lineasecommerceexcluidas", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        return cursor

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_linea", parent_cursor.valueBuffer("idtpv_linea"))
        self.dump_to_cursor()
        if not self.crear_viaje_lineasecommerce(str(self.cursor.valueBuffer("codcomanda"))):
            raise NameError("Error al crear el viaje de recogida en tienda.")

    def crear_viaje_lineasecommerce(self, codcomanda):
        qsatype.FactoriaModulos.get('flfactalma').iface.movimientoStockWeb_ = True

        id_viaje = qsatype.FactoriaModulos.get("formRecordtpv_comandas").iface.obtenerIdViaje()

        if not id_viaje or str(id_viaje) == "None" or id_viaje == None:
            raise NameError("No se ha podido calcular el idviaje.")
            return False
        nombre_origen = str(qsatype.FLUtil.quickSqlSelect("almacenes", "nombre", "codalmacen = '" + str(self.cursor.valueBuffer("codalmacen")) + "'"))

        curViaje = qsatype.FLSqlCursor("tpv_viajesmultitransstock")
        curViaje.setModeAccess(curViaje.Insert)
        curViaje.refreshBuffer()
        curViaje.setValueBuffer("idviajemultitrans", id_viaje)
        curViaje.setValueBuffer("fecha", qsatype.Date())
        curViaje.setValueBuffer("tiempotransito", str(qsatype.Date())[:10])
        curViaje.setValueBuffer("codalmaorigen", str(self.cursor.valueBuffer("codalmacen")))
        curViaje.setValueBuffer("nombreorigen", nombre_origen)
        curViaje.setValueBuffer("codalmadestino", "AWEB")
        curViaje.setValueBuffer("nombredestino", "WEB")
        curViaje.setValueBuffer("cantidad", parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "cantidad", "idtpv_linea = {}".format(self.cursor.valueBuffer("idtpv_linea")))))
        curViaje.setValueBuffer("enviocompletado", True)
        curViaje.setValueBuffer("codmultitransstock", "")
        curViaje.setValueBuffer("ptesincroenvio", False)
        curViaje.setValueBuffer("estado", "RECIBIDO")
        curViaje.setValueBuffer("recepcioncompletada", True)
        curViaje.setValueBuffer("azkarok", True)

        if not curViaje.commitBuffer():
            raise NameError("Error al guardar la cabecera del viaje.")
            return False

        if not self.crear_lineas_viaje_lineasecommerce(id_viaje):
            raise NameError("Error al crear las líneas del viaje.")
            return False

        if not qsatype.FLUtil.execSql("INSERT INTO eg_viajeswebtiendaptes (idviajemultitrans) VALUES ('{}')".format(id_viaje)):
            raise NameError("Error al insertar el registro en eg_viajeswebtiendaptes.")
            return False

        qsatype.FactoriaModulos.get('flfactalma').iface.movimientoStockWeb_ = False

        return True

    def crear_lineas_viaje_lineasecommerce(self, id_viaje):

        curLV = qsatype.FLSqlCursor("tpv_lineasmultitransstock")
        curLV.setModeAccess(curLV.Insert)
        curLV.setActivatedCommitActions(False)
        curLV.setActivatedCheckIntegrity(False)
        curLV.refreshBuffer()

        curLC = qsatype.FLSqlCursor("tpv_lineascomanda")
        curLC.select("idtpv_linea = {}".format(self.cursor.valueBuffer("idtpv_linea")))

        if curLC.first():
            curLC.setModeAccess(curLC.Browse)
            curLC.refreshBuffer()

            curLV.setValueBuffer("idviajemultitrans", id_viaje)
            curLV.setValueBuffer("referencia", curLC.valueBuffer("referencia"))
            curLV.setValueBuffer("descripcion", curLC.valueBuffer("descripcion"))
            curLV.setValueBuffer("barcode", curLC.valueBuffer("barcode"))
            curLV.setValueBuffer("talla", curLC.valueBuffer("talla"))
            curLV.setValueBuffer("codalmaorigen", str(self.cursor.valueBuffer("codalmacen")))
            curLV.setValueBuffer("codalmadestino", "AWEB")
            curLV.setValueBuffer("estado", "RECIBIDO")
            curLV.setValueBuffer("cantidad", parseFloat(curLC.valueBuffer("cantidad")))
            curLV.setValueBuffer("numlinea", 1)
            curLV.setValueBuffer("cantpteenvio", 0)
            curLV.setValueBuffer("cantenviada", parseFloat(curLC.valueBuffer("cantidad")))
            curLV.setValueBuffer("cantpterecibir", parseFloat(curLC.valueBuffer("cantidad")))
            curLV.setValueBuffer("cantrecibida", parseFloat(curLC.valueBuffer("cantidad")))
            curLV.setValueBuffer("excentral", "OK")
            curLV.setValueBuffer("extienda", "OK")
            curLV.setValueBuffer("rxcentral", "OK")
            curLV.setValueBuffer("rxtienda", "OK")
            curLV.setValueBuffer("ptestockcentral", False)
            curLV.setValueBuffer("cerradorx", False)
            curLV.setValueBuffer("cerradoex", False)
            curLV.setValueBuffer("revisada", False)
            curLV.setValueBuffer("ptestockrx", True)
            curLV.setValueBuffer("fechaex", str(qsatype.Date())[:10])
            curLV.setValueBuffer("fecharx", str(qsatype.Date())[:10])
            curLV.setValueBuffer("horaex", self.get_hora(str(qsatype.Date())))
            curLV.setValueBuffer("horarx", self.get_hora(str(qsatype.Date())))
            curLV.setValueBuffer("idsincro", "CENTRAL_" + str(curLV.valueBuffer("idlinea")))

            if not curLV.commitBuffer():
                raise NameError("Error al guardar la línea del viaje.")
                return False

            if not qsatype.FactoriaModulos.get("flfactalma").iface.borrarEstructuraMTOrigen(curLV):
                raise NameError("No se ha podido borrar los movimientos de stock de origen.")
                return False

            if not qsatype.FactoriaModulos.get("flfactalma").iface.generarEstructuraMTOrigen(curLV):
                raise NameError("No se ha podido crear los movimientos de stock de origen.")
                return False

            if not qsatype.FactoriaModulos.get("flfactalma").iface.borrarEstructuraMTDestino(curLV):
                raise NameError("No se ha podido borrar los movimientos de stock de destino.")
                return False

            if not qsatype.FactoriaModulos.get("flfactalma").iface.generarEstructuraMTDestino(curLV):
                raise NameError("No se ha podido crear los movimientos de stock de destino.")
                return False

        return True

    def get_hora(self, fecha):
        h = fecha[-(8):]
        h = "23:59:59" if h == "00:00:00" else h
        return h
