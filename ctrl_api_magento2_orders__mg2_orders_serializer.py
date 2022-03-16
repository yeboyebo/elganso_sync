from YBLEGACY import qsatype
from YBLEGACY.constantes import *
import json

from controllers.base.default.serializers.default_serializer import DefaultSerializer

from controllers.api.magento2.orders.serializers.mg2_orderline_serializer import Mg2OrderLineSerializer
from controllers.api.magento2.orders.serializers.mg2_shippingline_serializer import Mg2ShippingLineSerializer
from controllers.api.magento2.orders.serializers.mg2_expensesline_serializer import Mg2ExpensesLineSerializer
from controllers.api.magento2.orders.serializers.mg2_discountline_serializer import Mg2DiscountLineSerializer
from controllers.api.magento2.orders.serializers.mg2_voucherline_serializer import Mg2VoucherLineSerializer
from controllers.api.magento2.orders.serializers.mg2_payment_serializer import Mg2PaymentSerializer
from controllers.api.magento2.orders.serializers.mg2_cashcount_serializer import Mg2CashCountSerializer
from controllers.api.magento2.orders.serializers.mg2_idlecommerce_serializer import Mg2IdlEcommerce
from controllers.api.magento2.orders.serializers.mg2_pointsline_serializer import Mg2PointsLineSerializer
from controllers.api.magento2.orders.serializers.mg2_discountunknownline_serializer import Mg2DiscountUnknownLineSerializer


class Mg2OrdersSerializer(DefaultSerializer):
    cod_almacenes = ""
    barcodes_lineas = ""
    barcodes_con_stock = 0
    def get_data(self):
        increment = str(self.init_data["increment_id"])
        self.cod_almacenes = ""
        self.barcodes_lineas = ""
        self.barcodes_con_stock = 0
        # self.dame_almacenes(self.init_data)

        if not self.actualizar_items_lineas():
            raise NameError("Error al actualizar el items de las lineas.")
            return False

        codigo = "WEB{}".format(qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(increment, 9))

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
        elif str(self.init_data["status"]) == "canceled" or str(self.init_data["status"]) == "paypal_reversed" or str(self.init_data["status"]) == "paypal_canceled_reversal":
            if not self.eliminar_pedido_reserva_stock(codigo):
                raise NameError("Error al eliminar el pedido de reserva de stock.")
                return False
            return False
        elif str(self.init_data["status"]) == "complete" or str(self.init_data["status"]) == "processing":
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
            now = str(qsatype.Date())[:10]
            # self.set_string_relation("fecha", "created_at", max_characters=10)
            self.set_string_value("fecha", now, max_characters=10)

            tasaconv = 1
            divisa = str(self.init_data["currency"])

            if divisa:
                if divisa != "None" and divisa != "EUR" and divisa != "CLP":
                    tasaconv = qsatype.FLUtil.quickSqlSelect("divisas", "tasaconv", "coddivisa = '{}'".format(divisa))
                    if not tasaconv:
                        tasaconv = 1

            iva = 0
            ivaLinea = 0

            if "lines" not in self.data["children"]:
                self.data["children"]["lines"] = []

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []

            if not self.distribucion_almacenes():
                raise NameError("El numero de unidades indicadas y la cantidad de lineas no coincide.")
                return False

            ivaInformado = False

            for item in self.init_data["items"]:
                item.update({
                    "codcomanda": self.data["codigo"],
                    "tasaconv": tasaconv
                })

                line_data = Mg2OrderLineSerializer().serialize(item)
                self.data["children"]["lines"].append(line_data)

                ivaLinea = item["iva"]
                if not ivaInformado and item["pvpunitarioiva"] != 0:
                    iva = ivaLinea
                    ivaInformado = True

            if not ivaInformado:
                iva = ivaLinea

            new_init_data = self.init_data.copy()
            new_init_data.update({
                "iva": iva,
                "codcomanda": self.data["codigo"],
                "fecha": self.data["fecha"],
                "tasaconv": tasaconv
            })

            self.set_string_value("codtpv_puntoventa", self.get_puntoventa())
            self.set_string_value("codtpv_agente", "0350")
            self.set_string_value("codalmacen", "AWEB")
            self.set_string_value("codtienda", self.get_codtienda())
            self.set_string_value("coddivisa", "EUR"),
            self.set_string_value("estado", "Cerrada")

            self.set_data_value("editable", True)
            self.set_data_value("tasaconv", 1)
            self.set_data_value("ptesincrofactura", True)

            # iva = self.init_data["items"][-1]["iva"]
            total = round(parseFloat(self.init_data["grand_total"] * tasaconv), 2)
            neto = round(parseFloat(total / ((100 + iva) / 100)), 2)
            total_iva = total - neto

            # self.set_data_relation("total", "grand_total")
            # self.set_data_relation("pagado", "grand_total")

            self.set_data_value("total", total)
            self.set_data_value("pagado", total)
            self.set_data_value("totaliva", total_iva)
            self.set_data_value("neto", neto)

            self.set_string_relation("email", "email", max_characters=100)
            self.set_string_value("codtarjetapuntos", self.get_codtarjetapuntos(), max_characters=15)
            self.set_string_relation("cifnif", "cif", max_characters=20, default="-")

            self.set_string_relation("codpostal", "billing_address//postcode", max_characters=10)
            self.set_string_relation("ciudad", "billing_address//city", max_characters=100)
            self.set_string_relation("provincia", "billing_address//region", max_characters=100)
            self.set_string_relation("codpais", "billing_address//country_id", max_characters=20)
            self.set_string_relation("telefono1", "billing_address//telephone", max_characters=30)

            recogidatienda = self.get_recogidatienda()

            if recogidatienda:
                self.set_data_value("recogidatienda", True)
                self.set_string_relation("codtiendarecogida", "shipping_address//lastname", max_characters=10)
            else:
                self.set_data_value("recogidatienda", False)

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

            linea_envio = Mg2ShippingLineSerializer().serialize(new_init_data)
            linea_gastos = Mg2ExpensesLineSerializer().serialize(new_init_data)
            linea_descuento = Mg2DiscountLineSerializer().serialize(new_init_data)
            linea_puntos = Mg2PointsLineSerializer().serialize(new_init_data)
            linea_vale = Mg2VoucherLineSerializer().serialize(new_init_data)
            linea_dtodesconocido = Mg2DiscountUnknownLineSerializer().serialize(new_init_data)
            new_data = self.data.copy()
            if str(self.init_data["store_id"]) == "13":
                new_data.update({
                    "codtienda": self.get_codtienda()
                })
            arqueo_web = Mg2CashCountSerializer().serialize(new_data)
            new_data = self.data.copy()
            new_data.update({
                "idarqueo": arqueo_web["idtpv_arqueo"],
                "tasaconv": tasaconv,
                "codtienda": self.get_codtienda()
            })

            pago_web = Mg2PaymentSerializer().serialize(new_data)
            idl_ecommerce = Mg2IdlEcommerce().serialize(new_init_data)

            self.data["children"]["lines"].append(linea_gastos)
            self.data["children"]["lines"].append(linea_descuento)
            self.data["children"]["lines"].append(linea_vale)
            self.data["children"]["lines"].append(linea_puntos)
            self.data["children"]["lines"].append(linea_dtodesconocido)
            self.data["children"]["payments"].append(pago_web)
            self.data["children"]["shippingline"] = linea_envio

            if "skip" in arqueo_web and arqueo_web["skip"]:
                arqueo_web = False
            self.data["children"]["cashcount"] = arqueo_web
            self.data["children"]["idl_ecommerce"] = idl_ecommerce
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
        # hour = self.init_data["created_at"][-(8):]
        # hour = "23:59:59" if hour == "00:00:00" else hour

        now = str(qsatype.Date())
        hour = now[-(8):]

        return hour

    def get_codpago(self):
        payment_method = self.init_data["payment_method"]
        codpago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '{}'".format(payment_method))

        if not codpago:
            codpago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")

        return codpago

    def get_codtarjetapuntos(self):
        email = self.init_data["email"]
        codtarjetapuntos = qsatype.FLUtil.quickSqlSelect("tpv_tarjetaspuntos", "codtarjetapuntos", "email = '{}'".format(email).lower())

        if not codtarjetapuntos:
            codtarjetapuntos = ""

        return codtarjetapuntos

    def get_recogidatienda(self):
        metodoEnvio = str(self.init_data["shipping_method"])

        recogidatienda = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "recogidaentienda", "LOWER(metodoenviomg) = '" + metodoEnvio + "' OR UPPER(metodoenviomg) = '" + metodoEnvio + "' OR metodoenviomg = '" + metodoEnvio + "'")
        return recogidatienda

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
        qsatype.FactoriaModulos.get('flfactalma').iface.movimientoStockWeb_ = True
        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

        curPedido = qsatype.FLSqlCursor("pedidoscli")
        curPedido.setModeAccess(curPedido.Insert)
        curPedido.refreshBuffer()
        curPedido.setValueBuffer("observaciones", codigo)
        curPedido.setValueBuffer("codejercicio", self.get_codejercicio())
        curPedido.setValueBuffer("codserie", "SW")
        curPedido.setValueBuffer("codalmacen", "AWEB")

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

        cont = 0
        for linea in self.init_data["items"]:
            cont = cont + 1
            if not self.crear_linea_pedido_reserva_stock(cont, linea, curPedido.valueBuffer("idpedido")):
                raise NameError("Error al crear la linea del pedido de reserva de stock.")
                return False

        qsatype.FactoriaModulos.get('flfactalma').iface.movimientoStockWeb_ = False
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
            raise NameError("Error al guardar la linea del pedido.")
            return False

        return True

    def eliminar_pedido_reserva_stock(self, codigo):
        qsatype.FactoriaModulos.get('flfactalma').iface.movimientoStockWeb_ = True
        curPedido = qsatype.FLSqlCursor("pedidoscli")
        curPedido.select("observaciones = '" + str(codigo) + "'")
        if curPedido.first():
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
        else:
            for linea in self.init_data["items"]:
                id_stock = qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "codalmacen = 'AWEB' AND barcode = '{}'".format(self.get_barcode(linea["sku"])))
                if id_stock:
                    existe_sincroweb = qsatype.FLUtil.quickSqlSelect("eg_sincrostockweb", "idstock", "idstock = '{}'".format(id_stock))
                    if existe_sincroweb:
                        qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = FALSE, fecha = CURRENT_DATE, hora = CURRENT_TIME WHERE idstock = {}".format(id_stock))
                    else:
                        qsatype.FLSqlQuery().execSql("INSERT INTO eg_sincrostockweb (fecha,hora,sincronizado,idstock,sincronizadoeci) VALUES (CURRENT_DATE,CURRENT_TIME,false,{},true)".format(id_stock))

        qsatype.FactoriaModulos.get('flfactalma').iface.movimientoStockWeb_ = False
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

    def distribucion_almacenes(self):
        jsonDatos = self.init_data

        codpago = self.get_codpago()
        if str(codpago) == "CREE":
            return True

        almacenes = self.dame_almacenes(jsonDatos)

        def puntua_combinacion(combinacion):
            puntos = 100000 * self.puntos_productos_disponibles(combinacion)
            puntos += 10000 * self.puntos_cantidad_almacenes(combinacion, almacenes)
            puntos += 1000 * self.puntos_almacen_local(jsonDatos, combinacion)
            puntos += 100 * self.puntos_prioridad(combinacion, almacenes)
            puntos += 10 * self.puntos_bajo_limite(combinacion, almacenes)
            return puntos

        combinaciones = self.combinaciones_almacenes(almacenes)
        if len(combinaciones) == 0:
            return True

        combinaciones_ordenadas = sorted(combinaciones, key=puntua_combinacion, reverse=False)
        mejor_combinacion = combinaciones_ordenadas[0]
        print("MEJOR COMBINACION: ", mejor_combinacion)
        lineas_data = jsonDatos["items"]
        disponibles = self.disponibles_x_almacen(mejor_combinacion)

        for linea in lineas_data:
            barcode = self.get_barcode(linea["sku"])
            for almacen in mejor_combinacion:
                clave_disp = self.clave_disponible(almacen, barcode)
                can_disponible = disponibles.get(clave_disp, 0)
                if can_disponible > 0:
                    disponibles[clave_disp] -= 1
                    linea["almacen"] = almacen["cod_almacen"]
                    linea["emailtienda"] = almacen["emailtienda"]
                    break

        return True

    def dame_almacenes(self, jsonDatos):
        codpago = self.get_codpago()
        if str(codpago) == "CREE":
            return True

        q = qsatype.FLSqlQuery()
        q.setSelect(u"p.nombre, p.valor, a.codpais")
        q.setFrom(u"param_parametros p INNER JOIN almacenes a ON p.nombre = 'RSTOCK_' || a.codalmacen ")
        q.setWhere(u"p.nombre like 'RSTOCK_%'")

        q.exec_()

        if not q.size():
            return True

        margen_almacenes = {}
        pais_almacenes = {}

        while q.next():
            margen_almacenes[str(q.value(u"p.nombre"))] = int(q.value(u"p.valor"))
            pais_almacenes[str(q.value(u"p.nombre"))] = str(q.value(u"a.codpais"))

        lineas_data = self.init_data["items"]
        almacenes = []

        # combinaciones_almacen = {}
        indice_limite = 0
        limite_sobrepasado = False
        for indice, almacen in enumerate(jsonDatos["almacenes"]):
            limite_sobrepasado = False
            limite_pedido_minimo = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'LPEDIDO_" + almacen["source_code"] + "'")
            if not limite_pedido_minimo:
                limite_pedido_minimo = 1000

            # pedidos_almacen = qsatype.FLUtil.quickSqlSelect("eg_lineasecommerceexcluidas e INNER JOIN tpv_comandas c ON e.codcomanda = c.codigo", "COUNT(*)", "e.codalmacen = '" + almacen["source_code"] + "' AND c.fecha = CURRENT_DATE")
            pedidos_almacen = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "COUNT(*)", "fecha = CURRENT_DATE AND codigo like 'WEB%' and codtienda in ('AWEB','AWCL') and idtpv_comanda in (select c.idtpv_comanda from eg_lineasecommerceexcluidas le inner join tpv_lineascomanda l on le.idtpv_linea = l.idtpv_linea inner join tpv_comandas c on (l.idtpv_comanda = c.idtpv_comanda and le.codcomanda = c.codigo) WHERE le.codalmacen = '" + almacen["source_code"] + "' and c.fecha = CURRENT_DATE AND c.codigo like 'WEB%' and c.codtienda in ('AWEB','AWCL') group by c.idtpv_comanda)")
            # limite_sobrepasado = int(pedidos_almacen) >= int(limite_pedido_minimo)
            if int(pedidos_almacen) >= int(limite_pedido_minimo):
                limite_sobrepasado = True
                indice_limite += len(jsonDatos["almacenes"])

            barcodes = []
            lineas = {}
            ref_regalo = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'ART_REGALOWEB'")            
            aRegalo = ref_regalo.split(",")
            paramRegalo = False
            if len(aRegalo) > 0:
                paramRegalo = True
                
            esRegalo = False

            for linea_data in lineas_data:
                referencia = self.get_referencia(linea_data["sku"])
                
                if paramRegalo:
                    for i in range(len(aRegalo)):
                        if str(aRegalo[i][1:-1]) == str(referencia):
                            esRegalo = True

                if not esRegalo:
                    barcode = self.get_barcode(linea_data["sku"])
                    barcodes.append(barcode)
                    lineas[barcode] = linea_data["cantidad"]

            q = qsatype.FLSqlQuery()
            q.setSelect(u"barcode, disponible")
            q.setFrom(u"stocks")
            q.setWhere(u"codalmacen = '" + almacen["source_code"] + "' AND barcode IN ('" + "', '".join(barcodes) + "') ORDER BY barcode")

            q.exec_()

            if not q.size():
                continue

            jBarcodes = {}
            cant_disponible = 0
            hay_disponible = False
            # mi_combinacion = str(limite_sobrepasado)
            while q.next():
                
                #margen = margen_almacenes.get("RSTOCK_" + almacen["source_code"], 0)
                margen = 0
                cant_disponible = q.value("disponible") - margen
                if cant_disponible <= 0:
                    continue
                hay_disponible = True
                jBarcodes[q.value("barcode")] = cant_disponible
                # mi_combinacion += q.value("barcode") + "-" + str(cant_disponible) + ";"


            #if hay_disponible and mi_combinacion not in combinaciones_almacen:
            if hay_disponible:
                # combinaciones_almacen[mi_combinacion] = True
                if self.cod_almacenes == "":
                    self.cod_almacenes = "'" + almacen["source_code"] + "'"
                else:
                    self.cod_almacenes += ",'" + almacen["source_code"] + "'"

                if limite_sobrepasado:
                    almacenes.append({
                        "cod_almacen": almacen["source_code"],
                        "emailtienda": almacen["email"],
                        "total": 0,
                        "lineas": {},
                        "prioridad": 0.99 - indice_limite * 0.01,
                        "codpais": almacen["country_id"],
                        "bajo_limite": limite_pedido_minimo,
                        "disponibles": jBarcodes
                    })
                else:
                    almacenes.append({
                        "cod_almacen": almacen["source_code"],
                        "emailtienda": almacen["email"],
                        "total": 0,
                        "lineas": {},
                        "prioridad": 0.99 - indice * 0.01,
                        "codpais": almacen["country_id"],
                        "bajo_limite": limite_pedido_minimo,
                        "disponibles": jBarcodes
                    })

        self.barcodes_con_stock = qsatype.FLUtil.quickSqlSelect("atributosarticulos", "COUNT(*)", "barcode IN (SELECT barcode FROM stocks WHERE disponible > 0 AND codalmacen IN ({}) AND barcode IN ({}) GROUP BY barcode)".format(self.cod_almacenes, self.barcodes_lineas))

        return almacenes

    def clave_disponible(self, almacen, barcode):
        return almacen["cod_almacen"] + "_X_" + barcode

    def disponibles_x_almacen(self, combinacion):
        disponibles = {}
        for almacen in combinacion:
            for barcode in almacen["disponibles"]:
                disponibles[self.clave_disponible(almacen, barcode)] = almacen["disponibles"][barcode]

        return disponibles

    def puntos_productos_disponibles(self, combinacion):
        lineas = self.init_data["items"]
        max_puntos = len(lineas)
        if len(lineas) > self.barcodes_con_stock:
            max_puntos = len(lineas) - (len(lineas) - self.barcodes_con_stock)
        total_disponible = 0
        disponibles = self.disponibles_x_almacen(combinacion)
        for linea in lineas:
            barcode = linea["barcode"]
            for almacen in combinacion:
                clave_disp = self.clave_disponible(almacen, barcode)
                can_disponible = disponibles.get(self.clave_disponible(almacen, barcode), 0)
                if can_disponible > 0:
                    disponibles[clave_disp] -= 1
                    total_disponible += 1
                    break

        result = total_disponible * 10 / max_puntos
        return result

    def puntos_cantidad_almacenes(self, combinacion, almacenes):
        max_puntos = len(almacenes)
        puntos = len(almacenes) - len(combinacion) + 1
        result = puntos * 10 / max_puntos
        return result

    def puntos_almacen_local(self, jsonDatos, combinacion):
        def es_local(pais):
            return pais == jsonDatos["shipping_address"]["country_id"]

        max_puntos = len(combinacion)
        puntos = 0
        for i in range(len(combinacion)):
            puntos += 1 if es_local(combinacion[i]["codpais"]) else 0

        result = puntos * 10 / max_puntos
        return result

    def puntos_prioridad(self, combinacion, almacenes):
        max_puntos = 0
        for almacen in almacenes:
            max_puntos += almacen["prioridad"]

        prioridad = 0
        total_almacenes = len(almacenes)
        for almacen in combinacion:
            prioridad += total_almacenes - almacen["prioridad"]

        result = prioridad * 10 / max_puntos
        return result

    def puntos_bajo_limite(self, combinacion, almacenes):
        max_puntos = len(almacenes)
        puntos = 0

        for almacen in combinacion:
            puntos += 1 if parseFloat(almacen["bajo_limite"]) > 0 else 0

        result = puntos * 10 / max_puntos

        return result

    def combinacion_viable(self, combinacion):
        puntos = self.puntos_productos_disponibles(combinacion)
        return puntos == 10

    def combinaciones_almacenes(self, almacenes):
        from itertools import combinations
        result = []
        for can_almacenes in range(1, len(almacenes) + 1):
        # for can_almacenes in range(1, 4):
            combinaciones = combinations(almacenes, can_almacenes)
            hay_viables = False
            for c in combinaciones:
                if self.combinacion_viable(c):
                    hay_viables = True
                    result.append(c)

            if hay_viables:
                break

        return result

    def actualizar_items_lineas(self):
        aItems = []
        for item in self.init_data["items"]:
            if item["cantidad"] > 1:
                for i in range(item["cantidad"]):
                    sku = item["sku"]
                    cantidad = 1
                    barcode = self.get_barcode(item["sku"])
                    iva = item["iva"]
                    pvptotaliva = item["pvptotaliva"] / item["cantidad"]
                    ivaincluido = item["ivaincluido"]
                    pvpunitarioiva = item["pvpunitarioiva"]
                    pvpsindtoiva = item["pvpsindtoiva"] / item["cantidad"]
                    aItems.append({"sku": sku, "cantidad": cantidad, "iva": iva, "pvptotaliva": pvptotaliva, "ivaincluido": ivaincluido, "pvpunitarioiva": pvpunitarioiva, "pvpsindtoiva": pvpsindtoiva, "barcode": barcode})
            else:
                item["barcode"] = self.get_barcode(item["sku"])
                aItems.append(item)

        self.init_data["items"] = aItems

        self.barcodes_lineas = ""
        for linea in aItems:
            if self.barcodes_lineas == "":
                self.barcodes_lineas = "'" + linea["barcode"] + "'"
            else:
                self.barcodes_lineas += ",'" + linea["barcode"] + "'"
        return True

    def get_codtienda(self):
        if str(self.init_data["store_id"]) == "13":
            return qsatype.FLUtil.quickSqlSelect("mg_storeviews", "egcodtiendarebajas", "idmagento = '{}'".format(str(self.init_data["store_id"])))
        return "AWEB"

    def get_puntoventa(self):
        if str(self.init_data["store_id"]) == "13":
            return qsatype.FLUtil.quickSqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = '{}'".format(str(self.get_codtienda())))
        return "AWEB"
