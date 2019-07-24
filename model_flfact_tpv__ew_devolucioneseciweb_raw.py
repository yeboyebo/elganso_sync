from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EwDevolucioneseciweb(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("ew_devolucioneseciweb", init_data, params)

    def get_cursor(self):
        cursor = qsatype.FLSqlCursor(self.table)
        cursor.select("idventaweb = '{}'".format(self.data["idventaweb"]))

        if cursor.first():
            cursor.setModeAccess(cursor.Edit)
            cursor.refreshBuffer()

            self.is_insert = False
        else:
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBuffer()

            self.is_insert = True
        return cursor

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))
