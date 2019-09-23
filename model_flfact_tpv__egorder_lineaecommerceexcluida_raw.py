from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal.objects.aqmodel_raw import AQModel


class EgOrderLineaEcommerceExcluida(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("eg_lineasecommerceexcluidas", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_linea", parent_cursor.valueBuffer("idtpv_linea"))
