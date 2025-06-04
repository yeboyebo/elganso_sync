from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.magento2.orders.serializers.mg2_lineaecommerceexcluida_serializer import Mg2LineaEcommerceExcluidaSerializer

class Mg2OrderLineSerializer(DefaultSerializer):

    def get_data(self):
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        if not self.comprobar_talla():
            return False

        self.set_string_value("codtienda", "AWEB")

        self.set_string_value("referencia", self.get_referencia(), max_characters=18)
        self.set_string_value("descripcion", self.get_descripcion(), max_characters=100)
        self.set_string_value("barcode", self.get_barcode(), max_characters=20)
        self.set_string_value("talla", self.get_talla(), max_characters=50)
        self.set_string_value("color", self.get_color(), max_characters=50)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_string_relation("codcomanda", "codcomanda", max_characters=15)

        tasaconv = self.init_data["tasaconv"]

        """pvpunitarioiva = round(parseFloat(self.init_data["pvpunitarioiva"] * tasaconv), 2)
        pvpsindtoiva = round(parseFloat(self.init_data["pvpsindtoiva"] * tasaconv), 2)
        pvptotaliva = round(parseFloat(self.init_data["pvptotaliva"] * tasaconv), 2)

        pvpunitario = parseFloat(pvpunitarioiva / ((100 + iva) / 100))
        pvpsindto = parseFloat(pvpsindtoiva / ((100 + iva) / 100))
        pvptotal = parseFloat(pvptotaliva / ((100 + iva) / 100))"""

        pvpunitarioiva = self.get_damepreciopedido("pvpunitarioiva")
        pvpsindtoiva = self.get_damepreciopedido("pvpsindtoiva")
        pvptotaliva = self.get_damepreciopedido("pvptotaliva")

        pvpunitario = self.get_damepreciopedido("pvpunitario")
        pvpsindto = self.get_damepreciopedido("pvpsindto")
        pvptotal = self.get_damepreciopedido("pvptotal")

        self.set_data_value("cantdevuelta", 0)
        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("ivaincluido", True)
        self.set_data_value("pvpunitario", pvpunitario)
        self.set_data_value("pvpsindto", pvpsindto)
        self.set_data_value("pvptotal", pvptotal)

        self.set_data_relation("iva", "iva")
        self.set_data_value("pvpunitarioiva", pvpunitarioiva)
        self.set_data_value("pvpsindtoiva", pvpsindtoiva)
        self.set_data_value("pvptotaliva", pvptotaliva)
        # self.set_data_relation("pvpunitarioiva", "pvpunitarioiva")
        # self.set_data_relation("pvpsindtoiva", "pvpsindtoiva")
        # self.set_data_relation("pvptotaliva", "pvptotaliva")

        if self.get_barcode() != "8445005503262":
            if "almacen" in self.init_data:
                if str(self.init_data["almacen"]) != "AWEB":
                    linea_ecommerce_excluida = Mg2LineaEcommerceExcluidaSerializer().serialize(self.init_data)
                    self.data["children"]["lineaecommerceexcluida"] = linea_ecommerce_excluida
        
            if str(self.init_data["store_id"]) == "14" or str(self.init_data["store_id"]) == "13":
                if "almacen" not in self.init_data:
                    if str(self.init_data["store_id"]) == "14":
                        self.init_data["almacen"] = "AANT"
                        self.init_data["emailtienda"] = qsatype.FLUtil.quickSqlSelect("almacenes", "email", "codalmacen = '{}'".format("AANT"))
                    else:
                        raise NameError("VIENE SIN ALMACEN.")
                        return False
                        self.init_data["almacen"] = "ACHI"
                        self.init_data["emailtienda"] = qsatype.FLUtil.quickSqlSelect("almacenes", "email", "codalmacen = '{}'".format("ACHI"))
                    linea_ecommerce_excluida = Mg2LineaEcommerceExcluidaSerializer().serialize(self.init_data)
                    self.data["children"]["lineaecommerceexcluida"] = linea_ecommerce_excluida

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

    def comprobar_talla(self):
        splitted_sku = self.get_splitted_sku()

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            cant_tallas = qsatype.FLUtil.quickSqlSelect("atributosarticulos", "COUNT(*)", "referencia = '{}'".format(referencia))

            if float(cant_tallas) > 1:
                raise NameError("Error. Se ha indicado una referencia con varias tallas asociadas, revisar JSON")

        return True

    def get_damepreciopedido(self, tipoPrecio):

        cant = self.get_cantidad()
        tasaconv = self.init_data["tasaconv"]
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0
        pvpunitarioiva = round(parseFloat(self.init_data["pvpunitarioiva"] * tasaconv), 2)
        pvpsindtoiva = round(parseFloat(self.init_data["pvpsindtoiva"] * tasaconv), 2)
        pvptotaliva = round(parseFloat(self.init_data["pvptotaliva"] * tasaconv), 2)

        pvpunitario = parseFloat(pvpunitarioiva / ((100 + iva) / 100))
        pvpsindto = parseFloat(pvpsindtoiva / ((100 + iva) / 100))
        pvptotal = parseFloat(pvptotaliva / ((100 + iva) / 100))

        if self.init_data["es_cambio"] == False:
            if tipoPrecio == "pvpunitario":
                pvpunitarioiva = round(parseFloat(self.init_data["pvpunitarioiva"] * tasaconv), 2)
                return parseFloat(pvpunitarioiva / ((100 + iva) / 100))  
            elif tipoPrecio == "pvpsindto":
                pvpsindtoiva = round(parseFloat(self.init_data["pvpsindtoiva"] * tasaconv), 2)
                return parseFloat(pvpsindtoiva / ((100 + iva) / 100))
            elif tipoPrecio == "pvptotal":
                pvptotaliva = round(parseFloat(self.init_data["pvptotaliva"] * tasaconv), 2)
                return parseFloat(pvptotaliva / ((100 + iva) / 100))
            elif tipoPrecio == "pvpunitarioiva":
                return round(parseFloat(self.init_data["pvpunitarioiva"] * tasaconv), 2)
            elif tipoPrecio == "pvpsindtoiva":
                return round(parseFloat(self.init_data["pvpsindtoiva"] * tasaconv), 2)
            elif tipoPrecio == "pvptotaliva":
                return round(parseFloat(self.init_data["pvptotaliva"] * tasaconv), 2)
        else:
            codComandaDevol = str(self.init_data["rma_replace_id"])
            idtpv_comanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
            if tipoPrecio == "pvpunitario":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitario", "idtpv_comanda = {} AND (referencia IN (SELECT referencia from articulos where referenciaconfigurable IN (select referenciaconfigurable FROM articulos where referencia = '{}')) OR referencia = '{}')".format(idtpv_comanda, self.get_referencia(), self.get_referencia())))
            elif tipoPrecio == "pvpsindto" or tipoPrecio == "pvptotal":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitario", "idtpv_comanda = {} AND (referencia IN (SELECT referencia from articulos where referenciaconfigurable IN (select referenciaconfigurable FROM articulos where referencia = '{}')) OR referencia = '{}')".format(idtpv_comanda, self.get_referencia(), self.get_referencia()))) * cant
            elif tipoPrecio == "pvpunitarioiva":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitarioiva", "idtpv_comanda = {} AND (referencia IN (SELECT referencia from articulos where referenciaconfigurable IN (select referenciaconfigurable FROM articulos where referencia = '{}')) OR referencia = '{}')".format(idtpv_comanda, self.get_referencia(), self.get_referencia())))
            elif tipoPrecio == "pvpsindtoiva" or tipoPrecio == "pvptotaliva":
                return parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitarioiva", "idtpv_comanda = {} AND (referencia IN (SELECT referencia from articulos where referenciaconfigurable IN (select referenciaconfigurable FROM articulos where referencia = '{}')) OR referencia = '{}')".format(idtpv_comanda, self.get_referencia(), self.get_referencia()))) * cant
