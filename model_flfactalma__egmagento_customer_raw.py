from YBLEGACY import qsatype

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgMagentoCustomer(AQModel):

    def __init__(self, data, params=None):
        super().__init__("mg_customers", data, params)

    def get_cursor(self):
        cursor = qsatype.FLSqlCursor(self.table)
        cursor.select("email = '{}'".format(self.data["email"]))

        if cursor.first():
            cursor.setModeAccess(cursor.Edit)
            cursor.refreshBuffer()

            self.is_insert = False
        else:
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBuffer()

            self.is_insert = True
        return cursor

    def dump_to_cursor(self):
        if not self.cursor:
            self.cursor = self.get_cursor()

        for key, value in self.data.items():
            if key == "children":
                continue
            if not self.is_insert and key in ["idusuarioalta", "fechaalta", "horaalta"]:
                continue

            self.cursor.setValueBuffer(key, value)
