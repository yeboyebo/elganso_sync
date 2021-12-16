from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal import flsyncppal_def as syncppal
from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.mirakl.returns.serializers.movistock_serializer import EgMovistockSerializer


class ReturnLineSerializer(DefaultSerializer):

    def get_data(self):
        qL = qsatype.FLSqlQuery()
        qL.setSelect("codimpuesto, pvpunitario, iva")
        qL.setFrom("tpv_lineascomanda")
        qL.setWhere("idtpv_comanda = {} AND barcode = '{}'".format(self.init_data["idcomandaO"], self.get_barcode()))
        # Para pruebas
        # qL.setWhere("idtpv_comanda = {}".format(self.init_data["idcomandaO"]))

        if not qL.exec_():
            syncppal.iface.log("Error. Fallo la query al obtener los datos de las líneas de la venta original", "egmiraklreturns")
            return False

        if not qL.first():
            syncppal.iface.log("Error. No se encontraron datos de las líneas de la venta original", "egmiraklreturns")
            return False

        iva = int(qL.value("iva"))

        self.set_string_value("codtienda", self.get_codtienda())
        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", qL.value("codimpuesto"), max_characters=10)
        self.set_string_relation("codcomanda", "codcomanda", max_characters=12)

        pvpUnitario = qL.value("pvpunitario")
        cantidad = self.get_cantidad()
        pvptotal = pvpUnitario * cantidad

        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", cantidad)
        self.set_data_value("ivaincluido", True)
        self.set_data_value("pvpunitario", pvpUnitario)
        self.set_data_value("pvpsindto", pvptotal)
        self.set_data_value("pvptotal", pvptotal)
        self.set_data_value("iva", iva)
        self.set_data_value("pvpunitarioiva", pvpUnitario + ((pvpUnitario * iva) / 100))
        self.set_data_value("pvpsindtoiva", pvptotal + ((pvptotal * iva) / 100))
        self.set_data_value("pvptotaliva", pvptotal + ((pvptotal * iva) / 100))
       
        new_data = self.data.copy()
        new_data.update({
            "codalmacen": self.init_data["codalmacen"]
        })
        movistock_data = EgMovistockSerializer().serialize(new_data)
        self.data["children"]["movistock"] = movistock_data
        return True

    def get_pvpunitario(self):
        return qL.value("pvpunitario")

    def get_codtienda(self):
        return "AEVV"

    def get_referencia(self):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "referencia", "barcode = '{}'".format(self.get_barcode()))

    def get_descripcion(self):
        return qsatype.FLUtil.sqlSelect("articulos", "descripcion", "referencia = '{}'".format(self.get_referencia())) or "TU"

    def get_barcode(self):
        return self.get_init_value("EAN")[2:]

    def get_talla(self):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "talla", "barcode = '{}'".format(self.get_barcode())) or "TU"

    def get_color(self):
        return qsatype.FLUtil.sqlSelect("atributosarticulos", "color", "barcode = '{}'".format(self.get_barcode())) or "U"

    def get_codimpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def get_cantidad(self):
        return int(self.get_init_value("unidades")) * -1 or 0
