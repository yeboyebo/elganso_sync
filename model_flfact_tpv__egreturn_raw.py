from models.flsyncppal.objects.aqmodel_raw import AQModel
from models.flsyncppal import flsyncppal_def as syncppal
from models.flfact_tpv.objects.egreturn_line_raw import EgReturnLine
from models.flfact_tpv.objects.egidlecommercedevoluciones_raw import EgIdlEcommerceDevoluciones


class EgReturn(AQModel):

    def __init__(self, init_data, params=None):
        super().__init__("tpv_comandas", init_data, params)

    def get_cursor(self):
        cursor = super().get_cursor()

        cursor.setActivatedCommitActions(False)

        return cursor

    def get_children_data(self):
        if "lines" in self.data["children"]:
            if str(type(self.data["children"]["lines"])) == "<class 'list'>":
                for item in self.data["children"]["lines"]:
                    self.children.append(EgReturnLine(item))
            else:
                self.children.append(EgReturnLine(self.data["children"]["lines"]))
        else:
            syncppal.iface.log("Error. No se encontraron los datos de líneas", "egmiraklreturns")

        if "idl_ecommercedevoluciones" in self.data["children"]:
            idlEcommerceDev = EgIdlEcommerceDevoluciones(self.data["children"]["idl_ecommercedevoluciones"])
            self.children.append(idlEcommerceDev)
        else:
            syncppal.iface.log("Error. No se encontraron los datos de idl_ecommercedevoluciones", "egmiraklreturns")
