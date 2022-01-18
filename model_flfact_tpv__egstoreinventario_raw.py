from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgStoreInventario(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("so_inventariossincro", init_data, params)
