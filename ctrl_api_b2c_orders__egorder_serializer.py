from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer

from controllers.api.b2c.orders.serializers.egorder_line_serializer import EgOrderLineSerializer
from controllers.api.b2c.orders.serializers.egorder_shippingline_serializer import EgOrderShippingLineSerializer
from controllers.api.b2c.orders.serializers.egorder_expensesline_serializer import EgOrderExpensesLineSerializer
from controllers.api.b2c.orders.serializers.egorder_discountline_serializer import EgOrderDiscountLineSerializer
from controllers.api.b2c.orders.serializers.egorder_voucherline_serializer import EgOrderVoucherLineSerializer
from controllers.api.b2c.orders.serializers.egorder_payment_serializer import EgOrderPaymentSerializer
from controllers.api.b2c.orders.serializers.egcashcount_serializer import EgCashCountSerializer
from controllers.api.b2c.orders.serializers.egidlecommerce_serializer import EgIdlEcommerce


class EgOrderSerializer(DefaultSerializer):

    def get_data(self):
        increment = str(self.init_data["increment_id"])
        codigo = "WEB{}".format(qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(increment, 9))

        if qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codigo)):
            return False

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

        qsatype.FLSqlQuery().execSql("DELETE FROM eg_logpedidosweb WHERE fechaalta < CURRENT_DATE-30")
        qsatype.FLSqlQuery().execSql("INSERT INTO eg_logpedidosweb (fechaalta, horaalta, cuerpolog, codcomanda) VALUES ('{}', '{}', '{}', '{}')".format(now[:10], now[-(8):], str(self.init_data).replace("'", "\""), codigo))

        self.set_string_value("codigo", codigo, max_characters=15)

        self.set_string_value("codtpv_puntoventa", "AWEB")
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("codalmacen", "AWEB")
        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("coddivisa", "EUR")
        self.set_string_value("estado", "Cerrada")

        self.set_data_value("editable", True)
        self.set_data_value("tasaconv", 1)
        self.set_data_value("ptesincrofactura", True)

        iva = self.init_data["items"][-1]["iva"]
        neto = round(parseFloat(self.init_data["grand_total"] / ((100 + iva) / 100)), 2)
        total_iva = self.init_data["grand_total"] - neto

        self.set_data_relation("total", "grand_total")
        self.set_data_relation("pagado", "grand_total")
        self.set_data_value("totaliva", total_iva)
        self.set_data_value("neto", neto)

        self.set_string_relation("email", "email", max_characters=100)
        self.set_string_relation("codtarjetapuntos", "card_points", max_characters=15)
        self.set_string_relation("cifnif", "cif", max_characters=20, default="-")
        self.set_string_relation("fecha", "created_at", max_characters=10)

        self.set_string_relation("codpostal", "billing_address//postcode", max_characters=10)
        self.set_string_relation("ciudad", "billing_address//city", max_characters=100)
        self.set_string_relation("provincia", "billing_address//region", max_characters=100)
        self.set_string_relation("codpais", "billing_address//country_id", max_characters=20)
        self.set_string_relation("telefono1", "billing_address//telephone", max_characters=30)

        if self.init_data["shipping_method"].startswith("pl_store_pickup"):
            self.set_data_value("recogidatienda", True)
            self.set_string_relation("codtiendarecogida", "shipping_address//lastname", max_characters=10)

        nombrecliente = "{} {}".format(self.init_data["billing_address"]["firstname"], self.init_data["billing_address"]["lastname"])
        self.set_string_value("nombrecliente", nombrecliente, max_characters=100)

        street = self.init_data["billing_address"]["street"].split("\n")
        dirtipovia = street[0] if len(street) >= 1 else ""
        direccion = street[1] if len(street) >= 2 else ""
        dirnum = street[2] if len(street) >= 3 else ""
        dirotros = street[3] if len(street) >= 4 else ""

        self.set_string_value("dirtipovia", dirtipovia, max_characters=100)
        self.set_string_value("direccion", direccion, max_characters=100)
        self.set_string_value("dirnum", dirnum, max_characters=100)
        self.set_string_value("dirotros", dirotros, max_characters=100)

        self.set_string_value("codserie", self.get_codserie())
        self.set_string_value("codejercicio", self.get_codejercicio())
        self.set_string_value("hora", self.get_hora())
        self.set_string_value("codpago", self.get_codpago(), max_characters=10)
        self.set_string_value("egcodfactura", self.get_codfactura(), max_characters=12)

        iva = 0

        if "lines" not in self.data["children"]:
            self.data["children"]["lines"] = []

        if "payments" not in self.data["children"]:
            self.data["children"]["payments"] = []

        for item in self.init_data["items"]:
            item.update({
                "codcomanda": self.data["codigo"]
            })

            line_data = EgOrderLineSerializer().serialize(item)
            self.data["children"]["lines"].append(line_data)
            iva = item["iva"]

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "iva": iva,
            "codcomanda": self.data["codigo"],
            "fecha": self.data["fecha"]
        })

        linea_envio = EgOrderShippingLineSerializer().serialize(new_init_data)
        linea_gastos = EgOrderExpensesLineSerializer().serialize(new_init_data)
        linea_descuento = EgOrderDiscountLineSerializer().serialize(new_init_data)
        linea_vale = EgOrderVoucherLineSerializer().serialize(new_init_data)
        arqueo_web = EgCashCountSerializer().serialize(self.data)
        new_data = self.data.copy()
        new_data.update({"idarqueo": arqueo_web["idtpv_arqueo"]})
        pago_web = EgOrderPaymentSerializer().serialize(new_data)
        idl_ecommerce = EgIdlEcommerce().serialize(new_init_data)

        self.data["children"]["lines"].append(linea_gastos)
        self.data["children"]["lines"].append(linea_descuento)
        self.data["children"]["lines"].append(linea_vale)
        self.data["children"]["payments"].append(pago_web)
        self.data["children"]["shippingline"] = linea_envio

        if "skip" in arqueo_web and arqueo_web["skip"]:
            arqueo_web = False
        self.data["children"]["cashcount"] = arqueo_web
        self.data["children"]["idl_ecommerce"] = idl_ecommerce

        return True

    def get_codserie(self):
        pais = self.init_data["billing_address"]["country_id"]
        codpostal = self.init_data["billing_address"]["postcode"]

        codpais = None
        codserie = "A"
        codpostal2 = None

        if not pais or pais == "":
            return codserie

        codpais = qsatype.FLUtil.quickSqlSelect("paises", "codpais", "UPPER(codpais) = '{}'".format(pais.upper()))
        if not codpais or codpais == "":
            return codserie

        if codpais != "ES":
            codserie = "X"
        elif codpostal and codpostal != "":
            codpostal2 = codpostal[:2]
            if codpostal2 == "35" or codpostal2 == "38" or codpostal2 == "51" or codpostal2 == "52":
                codserie = "X"

        return codserie

    def get_codejercicio(self):
        date = self.init_data["created_at"][:10]
        splitted_date = date.split("-")

        return splitted_date[0]

    def get_hora(self):
        hour = self.init_data["created_at"][-(8):]
        hour = "23:59:59" if hour == "00:00:00" else hour

        return hour

    def get_codpago(self):
        payment_method = self.init_data["payment_method"]
        codpago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '{}'".format(payment_method))

        if not codpago:
            codpago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")

        return codpago

    def get_codfactura(self):
        prefix = "AWEBX"
        ultima_factura = None

        id_ultima = qsatype.FLUtil.sqlSelect("tpv_comandas", "egcodfactura", "egcodfactura LIKE '{}%' ORDER BY egcodfactura DESC".format(prefix))

        if id_ultima:
            ultima_factura = parseInt(str(id_ultima)[-(12 - len(prefix)):])
        else:
            ultima_factura = 0

        ultima_factura = ultima_factura + 1

        return "{}{}".format(prefix, qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(ultima_factura), 12 - len(prefix)))
