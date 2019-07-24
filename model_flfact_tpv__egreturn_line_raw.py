from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flfact_tpv.objects.egorder_line_raw import EgOrderLine
from models.flfact_tpv.objects.egmovistock_raw import EgMovistock


class EgReturnLine(EgOrderLine):

    def get_cursor(self):
        cursor = super().get_cursor()
        cursor.setActivatedCommitActions(False)
        return cursor

    def get_children_data(self):
        self.children.append(EgMovistock(self.data["children"]["movistock"]))
