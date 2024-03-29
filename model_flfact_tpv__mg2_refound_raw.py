from YBLEGACY import qsatype
from models.flsyncppal.objects.aqmodel_raw import AQModel

from models.flfact_tpv.objects.mg2_refound_line_raw import Mg2RefoundLine
from models.flfact_tpv.objects.mg2_refound_payment_raw import Mg2RefoundPayment
from models.flfact_tpv.objects.mg2_cashcount_raw import Mg2CashCount
from models.flfact_tpv.objects.egidlecommerce_raw import EgIdlEcommerce
from models.flfact_tpv.objects.egidlecommercedevoluciones_raw import EgIdlEcommerceDevoluciones


class MgRefound(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_comandas", init_data, params)

    def get_cursor(self):
        cursor = qsatype.FLSqlCursor(self.table)
        idComanda = False

        if "children" in self.data:
            if "payments" in self.data["children"]:
                if len(self.data["children"]["payments"]) > 0:
                    if "codcomanda" in self.data["children"]["payments"][0]:
                        idComanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(self.data["children"]["payments"][0]["codcomanda"]) + "'")

        cursor.select("idtpv_comanda = " + str(idComanda))

        if cursor.first():
            cursor.setModeAccess(cursor.Edit)
            cursor.refreshBuffer()
            self.is_insert = False
        else:
            cursor.setModeAccess(cursor.Insert)
            cursor.refreshBuffer()
            self.is_insert = True

        cursor.setActivatedCommitActions(False)

        return cursor

    def get_children_data(self):
        for item in self.data["children"]["lines"]:
            if item:
                item["creditmemo"] = self.data["children"]["creditmemo"]
                if "idl_ecommerce_devolucion" in self.data["children"]:
                    if self.data["children"]["idl_ecommerce_devolucion"]:
                        if "codtiendaentrega" in self.data["children"]["idl_ecommerce_devolucion"]:
                            item["codtiendaentrega"] = self.data["children"]["idl_ecommerce_devolucion"]["codtiendaentrega"]
                self.children.append(Mg2RefoundLine(item))

        if "cashcount" in self.data["children"]:
            if self.data["children"]["cashcount"]:
                arqueo = Mg2CashCount(self.data["children"]["cashcount"])
                self.children.append(arqueo)

        if "payments" in self.data["children"]:
            for item in self.data["children"]["payments"]:
                self.children.append(Mg2RefoundPayment(item))

        if "idl_ecommerce" in self.data["children"]:
            if self.data["children"]["idl_ecommerce"]:
                idlEcommerce = EgIdlEcommerce(self.data["children"]["idl_ecommerce"])
                self.children.append(idlEcommerce)

        if "idl_ecommerce_devolucion" in self.data["children"]:
            if self.data["children"]["idl_ecommerce_devolucion"]:
                idlEcommerceDevoluciones = EgIdlEcommerceDevoluciones(self.data["children"]["idl_ecommerce_devolucion"])
                self.children.append(idlEcommerceDevoluciones)
