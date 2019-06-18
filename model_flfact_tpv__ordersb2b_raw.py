from models.flsyncppal.objects.aqmodel_raw import AQModel

from models.flfact_tpv.objects.ordersb2b_line_raw import OrderLine
from models.flfact_tpv.objects.ordersb2b_line_shipping_raw import OrderLineShipping


class OrdersB2B(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("pedidoscli", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        return cursor

    def get_children_data(self):
        for item in self.data["children"]["lines"]:
            self.children.append(OrderLine(item))

        if self.data["children"]["shippingline"]:
            self.children.append(OrderLineShipping(self.data["children"]["shippingline"]))
