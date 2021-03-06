from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgRefoundPayment(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_pagoscomanda", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))

        self.dump_to_cursor()
        idsincro = qsatype.FactoriaModulos.get("formRecordtpv_pagoscomanda").iface.pub_commonCalculateField("idsincro", self.cursor)
        self.set_string_value("idsincro", idsincro, max_characters=30)
