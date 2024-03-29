from models.flsyncppal.objects.aqmodel_raw import AQModel
from YBLEGACY import qsatype

class EgShippingLabel(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("eg_shippinglabel", init_data, params)

    def get_parent_data(self, parent_cursor):
        self.set_data_value("idtpv_comanda", parent_cursor.valueBuffer("idtpv_comanda"))

        idEcommerce = qsatype.FLUtil.sqlSelect("idl_ecommerce", "id", "idtpv_comanda = {}".format(parent_cursor.valueBuffer("idtpv_comanda")))
        if idEcommerce:
            self.set_data_value("idecommerce", idEcommerce)
