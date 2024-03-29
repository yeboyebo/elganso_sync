from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class Mg2RefoundPayment(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_pagoscomanda", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))

        self.dump_to_cursor()
        idsincro = qsatype.FactoriaModulos.get("formRecordtpv_pagoscomanda").iface.pub_commonCalculateField("idsincro", self.cursor)
        self.set_string_value("idsincro", idsincro, max_characters=30)
        self.crear_registro_vale(self.cursor, parent_cursor)

    def crear_registro_vale(self, cursor, parent_cursor):
        if str(cursor.valueBuffer("codpago")) != "VAL":
            return True

        curVale = qsatype.FLSqlCursor("tpv_vales")
        curVale.setModeAccess(curVale.Insert)
        curVale.refreshBuffer()
        curVale.setValueBuffer("total", cursor.valueBuffer("importe"))
        curVale.setValueBuffer("saldopendiente", cursor.valueBuffer("importe"))
        curVale.setValueBuffer("saldoconsumido", 0)
        curVale.setValueBuffer("codigo", cursor.valueBuffer("codcomanda"))
        curVale.setValueBuffer("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))
        curVale.setValueBuffer("referencia", cursor.valueBuffer("codcomanda"))
        curVale.setValueBuffer("coddivisa", "EUR")
        curVale.setValueBuffer("fechamod", str(qsatype.Date())[:10])
        curVale.setValueBuffer("horamod", self.get_hora(str(qsatype.Date())))

        if not curVale.commitBuffer():
            return False
        return True

    def get_hora(self, fecha):
        h = fecha[-(8):]
        h = "23:59:59" if h == "00:00:00" else h
        return h
