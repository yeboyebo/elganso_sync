from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgStoreOrder(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("so_comandassincro", init_data, params)
