from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.magento2.refounds.serializers.mg2_lineasdevolucioneswebtienda_serializer import Mg2LineasDevolucionesWebTienda

class Mg2RefoundLineSerializer(DefaultSerializer):

    def get_data(self):

        iva = self.init_data["tax_percent"]
        if not iva or iva == "":
            iva = 0

        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)
        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        cant = parseFloat(self.init_data["qty"])
        pvpunitario = self.get_damepreciopedido("pvpunitario")
        pvpsindto = self.get_damepreciopedido("pvpsindto")
        pvptotal = self.get_damepreciopedido("pvptotal")
        pvpunitarioiva = self.get_damepreciopedido("pvpunitarioiva")
        pvpsindtoiva = self.get_damepreciopedido("pvpsindtoiva")
        pvptotaliva = self.get_damepreciopedido("pvptotaliva")

        if self.init_data["tipo_linea"] == "refounded":
            pvpsindto = pvpsindto * (-1)
            pvptotal = pvptotal * (-1)
            pvpsindtoiva = pvpsindtoiva * (-1)
            pvptotaliva = pvptotaliva * (-1)
            cant = cant * (-1)

        if iva == 0:
            pvpunitarioiva = parseFloat(pvpunitario)
            pvpsindtoiva = parseFloat(pvpsindto)
            pvptotaliva = parseFloat(pvptotal)

        self.set_string_value("cantidad", cant)
        self.set_string_value("cantdevuelta", 0)
        self.set_string_value("pvpunitario", pvpunitario)
        self.set_string_value("pvpsindto", pvpsindto)
        self.set_string_value("pvptotal", pvptotal)
        self.set_string_value("pvpunitarioiva", pvpunitarioiva)
        self.set_string_value("pvpsindtoiva", pvpsindtoiva)
        self.set_string_value("pvptotaliva", pvptotaliva)
        self.set_string_value("iva", iva)
        self.set_data_value("ivaincluido", True)

        if "codtiendaentrega" in self.init_data:
            if str(self.init_data["codtiendaentrega"]) != "AWEB":
                linea_devolucion_web_tienda = Mg2LineasDevolucionesWebTienda().serialize(self.init_data)
                self.data["children"]["lineadevolucionwebtienda"] = linea_devolucion_web_tienda
        return True

    def get_splitted_sku(self):
        return self.init_data["sku"].split("-")

    def get_referencia(self):
        return self.get_splitted_sku()[0]

    def get_descripcion(self):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '{}'".format(self.get_referencia()))

    def get_barcode(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0].upper()
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            referencia = splitted_sku[0].upper()
            talla = splitted_sku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '{}' AND talla = '{}'".format(referencia, talla))
        else:
            return "ERRORNOTALLA"

    def get_talla(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "talla", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            return splitted_sku[1]
        else:
            return "TU"

    def get_color(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            referencia = splitted_sku[0]
            talla = splitted_sku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '{}' AND talla = '{}'".format(referencia, talla))
        else:
            return "U"

    def get_codimpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def get_cantidad(self):
        return self.init_data["cantidad"]

    def get_damepreciopedido(self, tipoPrecio):

        cant = parseFloat(self.init_data["qty"])
        if self.init_data["es_cambio"] == False:
            if tipoPrecio == "pvpunitario":
                return parseFloat(self.init_data["price"]) * self.init_data["tasaconv"]   
            elif tipoPrecio == "pvpsindto" or tipoPrecio == "pvptotal":
                return parseFloat(self.init_data["price"]) * self.init_data["tasaconv"] * cant
            elif tipoPrecio == "pvpunitarioiva":
                return parseFloat(self.init_data["original_price"]) * self.init_data["tasaconv"]
            elif tipoPrecio == "pvpsindtoiva":
                return parseFloat(self.init_data["original_price"]) * self.init_data["tasaconv"] * cant
            elif tipoPrecio == "pvptotaliva":
                return parseFloat(self.init_data["row_total_incl_tax"]) * self.init_data["tasaconv"]
        else:
            codComandaDevol = "WEB" + str(self.init_data["increment_id"])
            idtpv_comanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
            if tipoPrecio == "pvpunitario":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitario", "idtpv_comanda = {} AND barcode = '{}'".format(idtpv_comanda, self.get_barcode())))
            elif tipoPrecio == "pvpsindto" or tipoPrecio == "pvptotal":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitario", "idtpv_comanda = {} AND barcode = '{}'".format(idtpv_comanda, self.get_barcode()))) * cant
            elif tipoPrecio == "pvpunitarioiva":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitarioiva", "idtpv_comanda = {} AND barcode = '{}'".format(idtpv_comanda, self.get_barcode())))
            elif tipoPrecio == "pvpsindtoiva" or tipoPrecio == "pvptotaliva":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitarioiva", "idtpv_comanda = {} AND barcode = '{}'".format(idtpv_comanda, self.get_barcode()))) * cant
       