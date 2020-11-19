from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel


class AzMovistock(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("movistock", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idlineaco", parent_cursor.valueBuffer("idtpv_linea"))
