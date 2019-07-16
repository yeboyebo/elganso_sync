from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EwVentaseciweb(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("ew_ventaseciweb", init_data, params)

    def get_cursor(self):
        cursor = qsatype.FLSqlCursor(self.table)
        cursor.select("idweb = '{}'".format(self.data["idweb"]))

        if cursor.first():
            cursor.setModeAccess(cursor.Edit)
            cursor.refreshBuffer()

            self.is_insert = False
        else:
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBuffer()

            self.is_insert = True
        return cursor

