from models.flsyncppal.objects.aqmodel_raw import AQModel


class Mg2CashCount(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_arqueos", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)
        cursor.setActivatedCheckIntegrity(False)

        return cursor
