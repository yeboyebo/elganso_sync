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
from controllers.api.b2c.orders.serializers.egidlecommercedevoluciones_serializer import EgIdlEcommerceDevoluciones
from controllers.api.b2c.orders.serializers.egorder_soles4soul_serializer import EgOrderSoles4soulLineSerializer
from controllers.api.b2c.orders.serializers.egshippinglabel_serializer import EgShippingLabel


class EgOrderSerializer(DefaultSerializer):

    def get_data(self):
        increment = str(self.init_data["increment_id"])
        print("increment: ", increment)
        codigo = "WEB{}".format(qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(increment, 9))

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

        qsatype.FLSqlQuery().execSql("DELETE FROM eg_logpedidosweb WHERE fechaalta < CURRENT_DATE-30")
        qsatype.FLSqlQuery().execSql("INSERT INTO eg_logpedidosweb (fechaalta, horaalta, cuerpolog, codcomanda) VALUES ('{}', '{}', '{}', '{}')".format(now[:10], now[-(8):], str(self.init_data).replace("'", "\""), codigo))

        if qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codigo)):
            return False

        if str(self.init_data["status"]) == "holded" or str(self.init_data["status"]) == "closed":
            return False
        elif str(self.init_data["status"]) == "seurpro_pending_cashondelivery" or str(self.init_data["status"]) == "fraud" or str(self.init_data["status"]) == "payment_review" or str(self.init_data["status"]) == "redsyspro_pending" or str(self.init_data["status"]) == "pending":
            if qsatype.FLUtil.sqlSelect("pedidoscli", "idpedido", "observaciones = '{}'".format(codigo)):
                raise NameError("Pedido ya creado.")
                return False

            if not self.crear_pedido_reserva_stock(codigo):
                raise NameError("Error al crear el pedido de reserva de stock.")
                return False

            return False
        elif str(self.init_data["status"]) == "canceled" or str(self.init_data["status"]) == "paypal_reversed" or  str(self.init_data["status"]) == "paypal_canceled_reversal":
            if not self.eliminar_pedido_reserva_stock(codigo):
                raise NameError("Error al eliminar el pedido de reserva de stock.")
                return False
            return False
        elif str(self.init_data["status"]) == "complete" or str(self.init_data["status"]) == "processing" or str(self.init_data["status"]) == "en_camino":
            if qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format(codigo)):
                return False

            if qsatype.FLUtil.sqlSelect("pedidoscli", "idpedido", "observaciones = '{}'".format(codigo)):
                if not self.eliminar_pedido_reserva_stock(codigo):
                    raise NameError("Error al eliminar el pedido de reserva de stock.")
                    return False

            num_lineas = 0
            for item in self.init_data["items"]:
                num_lineas = num_lineas + float(item["cantidad"])

            if float(num_lineas) != float(self.init_data["units"]):
                raise NameError("El número de unidades indicadas y la cantidad de líneas no coincide.")
                return False

            self.set_string_value("codigo", codigo, max_characters=15)
            self.set_string_value("fecha", now[:10])
            #self.set_string_relation("fecha", "created_at", max_characters=10)

            iva = 0
            ivaLinea = 0

            if "lines" not in self.data["children"]:
                self.data["children"]["lines"] = []

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []

            ivaInformado = False
            for item in self.init_data["items"]:
                item.update({
                    "codcomanda": self.data["codigo"]
                })

                line_data = EgOrderLineSerializer().serialize(item)
                self.data["children"]["lines"].append(line_data)

                ivaLinea = item["iva"] 
                if ivaInformado == False and item["pvpunitarioiva"] != 0:
                    iva = ivaLinea
                    ivaInformado = True

            if not ivaInformado:
                iva = ivaLinea

            new_init_data = self.init_data.copy()
            new_init_data.update({
                "iva": iva,
                "codcomanda": self.data["codigo"],
                "fecha": self.data["fecha"]
            })

            self.set_string_value("codtpv_puntoventa", "AWEB")
            self.set_string_value("codtpv_agente", "0350")
            self.set_string_value("codalmacen", "AWEB")
            self.set_string_value("codtienda", "AWEB")
            self.set_string_value("coddivisa", "EUR")
            self.set_string_value("estado", "Cerrada")

            self.set_data_value("editable", True)
            self.set_data_value("tasaconv", 1)
            self.set_data_value("ptesincrofactura", True)

            #iva = self.init_data["items"][-1]["iva"]
            neto = round(parseFloat(self.init_data["grand_total"] / ((100 + iva) / 100)), 2)
            total_iva = self.init_data["grand_total"] - neto

            self.set_data_relation("total", "grand_total")
            self.set_data_relation("pagado", "grand_total")
            self.set_data_value("totaliva", total_iva)
            self.set_data_value("neto", neto)

            self.set_string_relation("email", "email", max_characters=100)
            self.set_string_relation("codtarjetapuntos", "card_points", max_characters=15)
            self.set_string_relation("cifnif", "cif", max_characters=20, default="-")
            
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

            linea_envio = EgOrderShippingLineSerializer().serialize(new_init_data)
            linea_gastos = EgOrderExpensesLineSerializer().serialize(new_init_data)
            linea_descuento = EgOrderDiscountLineSerializer().serialize(new_init_data)
            linea_vale = EgOrderVoucherLineSerializer().serialize(new_init_data)
            linea_soles4soul = EgOrderSoles4soulLineSerializer().serialize(new_init_data)
            arqueo_web = EgCashCountSerializer().serialize(self.data)
            new_data = self.data.copy()
            new_data.update({"idarqueo": arqueo_web["idtpv_arqueo"]})
            pago_web = EgOrderPaymentSerializer().serialize(new_data)
            idl_ecommerce = EgIdlEcommerce().serialize(new_init_data)

            if "imagen_recoger" in self.init_data:
                if str(self.init_data["imagen_recoger"]) != "None" and self.init_data["imagen_recoger"] != None and self.init_data["imagen_recoger"] != False:
                    idl_ecommerce_devolucion = EgIdlEcommerceDevoluciones().serialize(new_init_data)
                    self.data["children"]["idl_ecommerce_devolucion"] = idl_ecommerce_devolucion

            self.data["children"]["lines"].append(linea_gastos)
            self.data["children"]["lines"].append(linea_descuento)
            self.data["children"]["lines"].append(linea_vale)
            if linea_soles4soul:
                self.data["children"]["lines"].append(linea_soles4soul)
            self.data["children"]["payments"].append(pago_web)
            self.data["children"]["shippingline"] = linea_envio

            if "skip" in arqueo_web and arqueo_web["skip"]:
                arqueo_web = False
            self.data["children"]["cashcount"] = arqueo_web
            self.data["children"]["idl_ecommerce"] = idl_ecommerce

            if "shipping_label" in self.init_data:
                if str(self.init_data["shipping_label"]) != "None" and self.init_data["shipping_label"] != None and self.init_data["shipping_label"] != False:
                    self.data["children"]["shipping_label"] = EgShippingLabel().serialize(new_init_data)

        else:
            raise NameError("Estado no controlado del pedido. Mirar registro de log en BBDD")
            return False
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

    def crear_pedido_reserva_stock(self, codigo):

        for linea in self.init_data["items"]:
            now = str(qsatype.Date())
            self.start_date = now[:10]
            self.start_time = now[-(8):]
            curPedido = qsatype.FLSqlCursor("pedidoscli")
            curPedido.setModeAccess(curPedido.Insert)
            curPedido.refreshBuffer()
            curPedido.setValueBuffer("observaciones", codigo)
            curPedido.setValueBuffer("codejercicio", self.get_codejercicio())
            curPedido.setValueBuffer("codserie", "SW")
            curPedido.setValueBuffer("codalmacen", linea["almacen"])

            numero = qsatype.FactoriaModulos.get("flfacturac").iface.siguienteNumero("SW", self.get_codejercicio(), "npedidocli")
            curPedido.setValueBuffer("numero", numero)
            codpedido = qsatype.FactoriaModulos.get("flfacturac").iface.pub_construirCodigo("SW", self.get_codejercicio(), numero)
            curPedido.setValueBuffer("codigo", codpedido)
            curPedido.setValueBuffer("totaleuros", 0)
            curPedido.setValueBuffer("direccion", "-")
            curPedido.setValueBuffer("codpago", "CONT")
            curPedido.setValueBuffer("tasaconv", 1)
            curPedido.setValueBuffer("total", 0)
            curPedido.setValueBuffer("irpf", 0)
            curPedido.setValueBuffer("servido", "No")
            curPedido.setValueBuffer("editable", True)
            curPedido.setValueBuffer("cifnif", "-")
            curPedido.setValueBuffer("recfinanciero", 0)
            curPedido.setValueBuffer("fecha", now)
            curPedido.setValueBuffer("neto", 0)
            curPedido.setValueBuffer("totalirpf", 0)
            curPedido.setValueBuffer("totaliva", 0)
            curPedido.setValueBuffer("fechasalida", now)
            curPedido.setValueBuffer("egenviado", False)
            curPedido.setValueBuffer("coddivisa", "EUR")

            if not curPedido.commitBuffer():
                raise NameError("Error al guardar la cabecera del pedido.")
                return False

            if not curPedido.valueBuffer("idpedido") or str(curPedido.valueBuffer("idpedido")) == "None":
                return False

            cont = 1
            if not self.crear_linea_pedido_reserva_stock(cont, linea, curPedido.valueBuffer("idpedido")):
                raise NameError("Error al crear la línea del pedido de reserva de stock.")
                return False

        return True

    def crear_linea_pedido_reserva_stock(self, cont, linea, idpedido):

        curLineaPedido = qsatype.FLSqlCursor("lineaspedidoscli")
        curLineaPedido.setModeAccess(curLineaPedido.Insert)
        curLineaPedido.refreshBuffer()
        curLineaPedido.setValueBuffer("idpedido", idpedido)
        curLineaPedido.setValueBuffer("numlinea", cont)
        curLineaPedido.setValueBuffer("referencia", self.get_referencia(linea["sku"]))
        curLineaPedido.setValueBuffer("descripcion", self.get_descripcion(linea["sku"]))
        curLineaPedido.setValueBuffer("barcode", self.get_barcode(linea["sku"]))
        curLineaPedido.setValueBuffer("talla", self.get_talla(linea["sku"]))
        curLineaPedido.setValueBuffer("cantidad", linea["cantidad"])
        curLineaPedido.setValueBuffer("totalenalbaran", 0)

        curLineaPedido.setValueBuffer("pvpunitario", 0)
        curLineaPedido.setValueBuffer("pvpunitarioiva", 0)
        curLineaPedido.setValueBuffer("pvpsindtoiva", 0)
        curLineaPedido.setValueBuffer("pvpsindto", 0)
        curLineaPedido.setValueBuffer("pvptotal", 0)
        curLineaPedido.setValueBuffer("pvptotaliva", 0)
        curLineaPedido.setValueBuffer("dtolineal", 0)
        curLineaPedido.setValueBuffer("dtopor", 0)
        curLineaPedido.setValueBuffer("iva", 21)
        curLineaPedido.setValueBuffer("codimpuesto", "GEN")
        curLineaPedido.setValueBuffer("egordenlinea", "")
        if not curLineaPedido.commitBuffer():
            raise NameError("Error al guardar la línea del pedido.")
            return False

        return True

    def eliminar_pedido_reserva_stock(self, codigo):
        curPedido = qsatype.FLSqlCursor("pedidoscli")
        curPedido.select("observaciones = '" + str(codigo) + "'")
        while curPedido.next():
            curLineaPedido = qsatype.FLSqlCursor("lineaspedidoscli")
            curLineaPedido.select("idpedido = " + str(curPedido.valueBuffer("idpedido")))
            while curLineaPedido.next():
                curLineaPedido.setModeAccess(curLineaPedido.Del)
                curLineaPedido.refreshBuffer()
                if not curLineaPedido.commitBuffer():
                    return False

            curPedido.setModeAccess(curPedido.Del)
            curPedido.refreshBuffer()
            if not curPedido.commitBuffer():
                return False

        valorFiltro = ""
        valorUsarPreOrder = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'USAR_ART_PREORDER'")

        if valorUsarPreOrder and valorUsarPreOrder == "True":
            artPreOrder = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'ART_PREORDER'")
            if artPreOrder and artPreOrder != "":
                valorFiltro = " AND referencia NOT IN (" + artPreOrder + ")"

        for linea in self.init_data["items"]:
            if valorFiltro == "":
                id_stock = qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "codalmacen = 'AWEB' AND barcode = '{}'".format(self.get_barcode(linea["sku"])))
            else:
                id_stock = qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "codalmacen = 'AWEB' AND barcode = '{}' {}".format(self.get_barcode(linea["sku"], valorFiltro)))
            if id_stock:
                existe_sincroweb = qsatype.FLUtil.quickSqlSelect("eg_sincrostockweb", "idstock", "idstock = '{}'".format(id_stock))
                if existe_sincroweb:
                    qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = FALSE, fecha = CURRENT_DATE, hora = CURRENT_TIME WHERE idstock = {}".format(id_stock))
                else:
                    qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincrostockweb (fecha,hora,sincronizado,idstock,sincronizadoeci) VALUES (CURRENT_DATE,CURRENT_TIME,false,{},true)".format(id_stock))
        return True

    def get_splitted_sku(self, refArticulo):
        return refArticulo.split("-")

    def get_referencia(self, refArticulo):
        return self.get_splitted_sku(refArticulo)[0]

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

    def get_descripcion(self, sku):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '{}'".format(self.get_referencia(sku)))

    def get_talla(self, sku):
        splitted_sku = self.get_splitted_sku(sku)

        if len(splitted_sku) == 1:
            referencia = splitted_sku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "talla", "referencia = '{}'".format(referencia))
        elif len(splitted_sku) == 2:
            return splitted_sku[1]
        else:
            return "TU"
