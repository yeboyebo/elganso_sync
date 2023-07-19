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
        

        if self.init_data["es_cambio"]:
            importe = self.get_dameimportepedido()
            self.set_string_value("importe", importe)
            codPago = self.get_codpago()
            self.set_string_value("codpago", codPago)
        else:
            self.set_data_relation("importe", "total", default=0)
            self.set_string_relation("codpago", "codpago", max_characters=10)

        self.set_string_value("estado", "Pagado")
        self.set_string_value("codtienda", self.init_data["codtienda"])
        self.set_string_value("refvale", self.init_data["refvale"])
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("idtpv_arqueo", idarqueo, max_characters=8)

        # total = round(parseFloat(self.init_data["total"] * tasaconv), 2)
        # self.set_data_value("importe", total)
        
        self.set_string_relation("fecha", "fecha")
        self.set_string_relation("codtpv_puntoventa", "codtpv_puntoventa", max_characters=6)
        
        self.set_string_relation("codcomanda", "codigo", max_characters=15)

        return True

    def get_splitted_sku(self, sku):
        return sku.split("-")

    def get_referencia(self, sku):
        return self.get_splitted_sku(sku)[0]

    def get_dameimportepedido(self):
        importe = 0
        codComandaDevol = str(self.init_data["rma_replace_id"])
        idtpv_comanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
        for linea in self.init_data["items"]:
            importe += parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "pvpunitarioiva", "idtpv_comanda = {} AND (referencia IN (SELECT referencia from articulos where referenciaconfigurable IN (select referenciaconfigurable FROM articulos where referencia = '{}')) OR referencia = '{}')".format(idtpv_comanda, self.get_referencia(linea["sku"]), self.get_referencia(linea["sku"])))) * parseFloat(linea["cantidad"])

        return importe

    def get_codpago(self):
        codComandaDevol = str(self.init_data["rma_replace_id"])
        idtpv_comanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codComandaDevol))
        codPago = qsatype.FLUtil.quickSqlSelect("tpv_pagoscomanda", "codpago", "idtpv_comanda = {}".format(idtpv_comanda))

        return codPago