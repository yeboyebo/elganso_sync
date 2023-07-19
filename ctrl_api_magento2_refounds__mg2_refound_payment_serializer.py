from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class Mg2RefoundPaymentSerializer(DefaultSerializer):

    def get_data(self):

        idarqueo = self.init_data["idarqueo"]
        if not idarqueo:
            return False

        importe = float(self.init_data["total_pay"])  * self.init_data["tasaconv"]
        if self.init_data["es_cambio"]:
            importe = self.get_dameimportepedido()

        self.set_data_value("anulado", False)
        self.set_data_value("editable", True)
        self.set_data_value("nogenerarasiento", True)
        self.set_string_value("estado", "Pagado")
        self.set_string_value("codtienda", self.init_data["codtienda"])
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("codtpv_puntoventa", self.init_data["puntoventa"])
        self.set_string_value("fecha", str(qsatype.Date())[:10])
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)
        self.set_string_value("codcomanda", str(self.init_data["codcomanda"]))
        codPago = self.get_codpago()

        if str(self.init_data["tipo_pago"]) == "Negativo":
            importe = importe * (-1)

        self.set_string_value("importe", importe)
        self.set_string_value("codpago", codPago)

        return True

    def get_codpago(self):
        codPago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '" + str(self.init_data["payment_method"]) + "'")

        if not codPago:
            codPago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")
            if not codPago:
                codPago = "CONT"

        if self.init_data["es_cambio"]:
            codComandaDevol = "WEB" + str(self.init_data["increment_id"])
            idtpv_comanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
            codPago = qsatype.FLUtil.quickSqlSelect("tpv_pagoscomanda", "codpago", "idtpv_comanda = {}".format(idtpv_comanda))

        return codPago

    def get_splitted_sku(self, sku):
        return sku.split("-")

    def get_referencia(self):
        return self.get_splitted_sku()[0]

    def get_descripcion(self):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '{}'".format(self.get_referencia()))

    def get_barcode(self, sku):
        splitted_sku = self.get_splitted_sku(sku)

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

    def get_dameimportepedido(self):
        importe = 0
        codComandaDevol = "WEB" + str(self.init_data["increment_id"])
        idtpv_comanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
        for linea in self.init_data["items_refunded"]:
            importe += parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitarioiva", "idtpv_comanda = {} AND barcode = '{}'".format(idtpv_comanda, self.get_barcode(linea["sku"])))) * parseFloat(linea["qty"])

        return importe