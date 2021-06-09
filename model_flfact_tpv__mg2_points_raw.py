from models.flsyncppal.objects.aqmodel_raw import AQModel


class Mg2Points(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_tarjetaspuntos", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()
        cursor.setActivatedCommitActions(False)
        return cursor
