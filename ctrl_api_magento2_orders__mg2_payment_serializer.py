from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2PaymentSerializer(DefaultSerializer):

    def get_data(self):

        idarqueo = self.init_data["idarqueo"]
        if not idarqueo:
            return False

        # tasaconv = self.init_data["tasaconv"]

        self.set_data_value("anulado", False)
        self.set_data_value("editable", True)
        self.set_data_value("nogenerarasiento", True)
        

        self.set_data_relation("importe", "total", default=0)
        self.set_string_relation("codpago", "codpago", max_characters=10)

        self.set_string_value("estado", "Pagado")
        self.set_string_value("codtienda", self.init_data["codtienda"])
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)

        # total = round(parseFloat(self.init_data["total"] * tasaconv), 2)
        # self.set_data_value("importe", total)
        
        self.set_string_relation("fecha", "fecha")
        self.set_string_relation("codtpv_puntoventa", "codtpv_puntoventa", max_characters=6)
        
        self.set_string_relation("codcomanda", "codigo", max_characters=15)

        return True
