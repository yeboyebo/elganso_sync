from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgIdlEcommerceDevoluciones(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("idl_ecommercedevoluciones", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))
