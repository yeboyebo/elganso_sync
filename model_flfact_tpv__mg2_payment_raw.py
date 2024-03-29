from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class Mg2Payment(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_pagoscomanda", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()
        cursor.setActivatedCommitActions(False)
        return cursor

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))

        self.dump_to_cursor()
        idsincro = qsatype.FactoriaModulos.get("formRecordtpv_pagoscomanda").iface.pub_commonCalculateField("idsincro", self.cursor)
        self.set_string_value("idsincro", idsincro, max_characters=30)
        self.crear_registro_movivale(self.cursor, parent_cursor)

    def crear_registro_movivale(self, cursor, parent_cursor):
        if str(cursor.valueBuffer("codpago")) != "VAL":
            return True

        curMoviVale = qsatype.FLSqlCursor("tpv_movivale")
        curMoviVale.setModeAccess(curMoviVale.Insert)
        curMoviVale.refreshBuffer()
        curMoviVale.setValueBuffer("refvale", cursor.valueBuffer("refvale"))
        curMoviVale.setValueBuffer("idsincropago", qsatype.FactoriaModulos.get("formRecordtpv_pagoscomanda").iface.pub_commonCalculateField("idsincro", cursor))
        curMoviVale.setValueBuffer("total", 0)

        if not curMoviVale.commitBuffer():
            return False
        return True
