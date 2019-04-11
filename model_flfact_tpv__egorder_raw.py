from models.flsyncppal.objects.aqmodel_raw import AQModel

from models.flfact_tpv.objects.egorder_line_raw import EgOrderLine
from models.flfact_tpv.objects.egorder_shippingline_raw import EgOrderShippingLine
from models.flfact_tpv.objects.egorder_payment_raw import EgOrderPayment
from models.flfact_tpv.objects.egcashcount_raw import EgCashCount


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
            self.children.append(EgOrderPayment(item.update({"idarqueo": arqueo.data["idtpv_arqueo"]})))
