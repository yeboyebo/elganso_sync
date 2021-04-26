from models.flsyncppal.objects.aqmodel_raw import AQModel

from models.flfact_tpv.objects.egorder_line_raw import EgOrderLine
from models.flfact_tpv.objects.egorder_shippingline_raw import EgOrderShippingLine
from models.flfact_tpv.objects.egorder_payment_raw import EgOrderPayment
from models.flfact_tpv.objects.egcashcount_raw import EgCashCount
from models.flfact_tpv.objects.egidlecommerce_raw import EgIdlEcommerce
from models.flfact_tpv.objects.egidlecommercedevoluciones_raw import EgIdlEcommerceDevoluciones
from models.flfact_tpv.objects.egshippinglabel_raw import EgShippingLabel

class EgOrder(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_comandas", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)

        return cursor

    def get_children_data(self):
        for item in self.data["children"]["lines"]:
            self.children.append(EgOrderLine(item))

        self.children.append(EgOrderShippingLine(self.data["children"]["shippingline"]))

        arqueo = EgCashCount(self.data["children"]["cashcount"])
        self.children.append(arqueo)

        for item in self.data["children"]["payments"]:
            self.children.append(EgOrderPayment(item))

        idlEcommerce = EgIdlEcommerce(self.data["children"]["idl_ecommerce"])
        self.children.append(idlEcommerce)

        if "idl_ecommerce_devolucion" in self.data["children"]:
            if self.data["children"]["idl_ecommerce_devolucion"]:
                idlEcommerceDevoluciones = EgIdlEcommerceDevoluciones(self.data["children"]["idl_ecommerce_devolucion"])
                self.children.append(idlEcommerceDevoluciones)

        if "shipping_label" in self.data["children"]:
            if self.data["children"]["shipping_label"]:
                shippingLabel = EgShippingLabel(self.data["children"]["shipping_label"])
                self.children.append(shippingLabel)
