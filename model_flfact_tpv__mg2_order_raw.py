from models.flsyncppal.objects.aqmodel_raw import AQModel

from models.flfact_tpv.objects.mg2_orderline_raw import Mg2OrderLine
from models.flfact_tpv.objects.mg2_shippingline_raw import Mg2ShippingLine
from models.flfact_tpv.objects.mg2_payment_raw import Mg2Payment
from models.flfact_tpv.objects.mg2_cashcount_raw import Mg2CashCount
from models.flfact_tpv.objects.egidlecommerce_raw import EgIdlEcommerce
from models.flfact_tpv.objects.egidlecommercedevoluciones_raw import EgIdlEcommerceDevoluciones

class Mg2Order(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_comandas", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)

        return cursor

    def get_children_data(self):
        for item in self.data["children"]["lines"]:
            self.children.append(Mg2OrderLine(item))

        self.children.append(Mg2ShippingLine(self.data["children"]["shippingline"]))

        arqueo = Mg2CashCount(self.data["children"]["cashcount"])
        self.children.append(arqueo)

        for item in self.data["children"]["payments"]:
            self.children.append(Mg2Payment(item))

        idlEcommerce = EgIdlEcommerce(self.data["children"]["idl_ecommerce"])
        self.children.append(idlEcommerce)

        if "idl_ecommerce_devolucion" in self.data["children"]:
            if self.data["children"]["idl_ecommerce_devolucion"]:
                idlEcommerceDevoluciones = EgIdlEcommerceDevoluciones(self.data["children"]["idl_ecommerce_devolucion"])
                self.children.append(idlEcommerceDevoluciones)
