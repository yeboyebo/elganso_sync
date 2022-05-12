from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from datetime import datetime
import time

from controllers.base.default.serializers.default_serializer import DefaultSerializer

from controllers.api.mirakl.shippingorders.serializers.egorder_line_serializer import EgOrderLineSerializer
from controllers.base.mirakl.orders.serializers.order_shippingline_serializer import OrderShippingLineSerializer
from controllers.base.mirakl.orders.serializers.order_expensesline_serializer import OrderExpensesLineSerializer
from controllers.base.mirakl.orders.serializers.cashcount_serializer import CashCountSerializer
from controllers.base.mirakl.orders.serializers.order_payment_serializer import OrderPaymentSerializer
from controllers.base.mirakl.orders.serializers.idl_ecommerce_serializer import IdlEcommerceSerializer


class EgOrderSerializer(DefaultSerializer):

    cod_almacenes = ""
    barcodes_lineas = ""
    barcodes_con_stock = 0
    def get_data(self):
        self.cod_almacenes = ""
        self.barcodes_lineas = ""
        self.barcodes_con_stock = 0
        codtienda = self.get_codtienda()
        punto_venta = self.get_puntoventa()

        self.actualizar_items_lineas()

        self.set_string_value("codalmacen", "AWEB")
        self.set_string_value("codtpv_puntoventa", punto_venta)
        self.set_string_value("codtienda", codtienda)

        codigo = self.get_codigo()
        self.set_string_value("codigo", codigo, max_characters=15)

        self.set_string_value("codtpv_agente", "0350")

        self.set_string_relation("coddivisa", "currency_iso_code")
        self.set_string_value("estado", "Cerrada")

        self.set_data_value("editable", True)
        self.set_data_value("tasaconv", 1)
        self.set_data_value("ptesincrofactura", False)

        # iva = self.init_data["order_lines"][-1]["iva"]
        # neto = round(parseFloat(self.init_data["grand_total"] / ((100 + iva) / 100)), 2)
        # total_iva = self.init_data["grand_total"] - neto

        self.set_data_relation("total", "total_price")
        self.set_data_relation("pagado", "total_price")
        self.set_data_relation("neto", "price")
        self.set_data_relation("totaliva", "total_commission")

        # self.set_string_relation("email", "email", max_characters=100)
        # self.set_string_relation("codtarjetapuntos", "card_points", max_characters=15)
        # self.set_string_relation("cifnif", "cif", max_characters=20, default="-")
        utcCreatedDtate = datetime.strptime(self.get_init_value("created_date"), '%Y-%m-%dT%H:%M:%SZ')
        localCreatedDate = self.utcToLocal(utcCreatedDtate)
        fecha = str(localCreatedDate)[:10]
        hora = str(localCreatedDate)[-8:]
        self.set_string_value("fecha", fecha)
        self.set_string_value("hora", hora)

        self.set_string_relation("codpostal", "customer//billing_address//zip_code", max_characters=10)
        self.set_string_relation("ciudad", "customer//billing_address//city", max_characters=100)
        # self.set_string_relation("provincia", "customer//billing_address//region", max_characters=100)
        self.set_string_relation("codpais", "customer//billing_address//country_iso_code", max_characters=100)
        self.set_string_relation("telefono1", "customer//billing_address//phone", max_characters=30)
        nombrecliente = "{} {}".format(self.get_init_value("customer//billing_address//firstname"), self.get_init_value("customer//billing_address//lastname"))
        self.set_string_value("nombrecliente", nombrecliente, max_characters=100)
        # street = self.get_init_value("customer//billing_address//street_1").split("\n")
        # dirtipovia = street[0] if len(street) >= 1 else ""
        # direccion = street[1] if len(street) >= 2 else ""
        # dirnum = street[2] if len(street) >= 3 else ""
        # dirotros = street[3] if len(street) >= 4 else ""

        self.set_string_relation("direccion", "customer//billing_address//street_1", max_characters=100)
        # self.set_string_value("dirtipovia", dirtipovia, max_characters=100)
        # self.set_string_value("dirnum", dirnum, max_characters=100)
        # self.set_string_value("dirotros", dirotros, max_characters=100)

        self.set_string_value("codserie", self.get_codserie())
        codejercicio = fecha[:4]
        self.set_string_value("codejercicio", codejercicio)
        self.set_string_value("codpago", self.get_codpago(), max_characters=10)
        self.set_string_value("egcodfactura", "")
        iva = self.init_data["order_lines"][-1]["commission_rate_vat"]
        if "lines" not in self.data["children"]:
            self.data["children"]["lines"] = []

        if "payments" not in self.data["children"]:
            self.data["children"]["payments"] = []

        if not self.distribucion_almacenes():
            raise NameError("Error en la distribucion de almacenes.")
            return False

        for item in self.init_data["order_lines"]:
            item.update({
                "codcomanda": self.data["codigo"]
            })

            line_data = EgOrderLineSerializer().serialize(item)
            self.data["children"]["lines"].append(line_data)

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "fecha": self.data["fecha"],
            "iva": iva
        })

        linea_envio = OrderShippingLineSerializer().serialize(new_init_data)
        # linea_descuento = EgOrderDiscountLineSerializer().serialize(new_init_data)
        # linea_vale = EgOrderVoucherLineSerializer().serialize(new_init_data)
        linea_gastos = OrderExpensesLineSerializer().serialize(new_init_data)
        arqueo_web = CashCountSerializer().serialize(self.data)
        new_data = self.data.copy()
        new_data.update({"idarqueo": arqueo_web["idtpv_arqueo"]})
        pago_web = OrderPaymentSerializer().serialize(new_data)
        idl_ecommerce = IdlEcommerceSerializer().serialize(new_init_data)

        self.data["children"]["lines"].append(linea_gastos)
        self.data["children"]["payments"].append(pago_web)
        self.data["children"]["shippingline"] = linea_envio
        self.data["children"]["idl_ecommerce"] = idl_ecommerce
        # self.data["children"]["lines"].append(linea_descuento)
        # self.data["children"]["lines"].append(linea_vale)

        if "skip" in arqueo_web and arqueo_web["skip"]:
            arqueo_web = False
        self.data["children"]["cashcount"] = arqueo_web

        return True

    def get_codtienda(self):
        return "AEVV"

    def get_puntoventa(self):
        return qsatype.FLUtil.sqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = '{}'".format(self.get_codtienda()))

    def get_codserie(self):
        pais = self.data["codpais"]
        codpostal = self.data["codpostal"]

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
        date = self.data["fecha"][:10]
        splitted_date = date.split("-")

        return splitted_date[0]

    def get_hora(self):
        utcCreatedDtate = self.get_init_value("created_date")
        localCreatedDate = utcToLocal(utcCreatedDtate)

        hour = "23:59:59" if hour == "00:00:00" else hour

        return hour

    def get_codpago(self):
        return "TARJ"

    def get_codigo(self):
        prefix = self.data["codtpv_puntoventa"]
        ultima_vta = None

        id_ultima = qsatype.FLUtil.sqlSelect("tpv_comandas", "codigo", "codigo LIKE '{}%' ORDER BY codigo DESC LIMIT 1".format(prefix))

        if id_ultima:
            ultima_vta = parseInt(str(id_ultima)[-(12 - len(prefix)):])
        else:
            ultima_vta = 0

        ultima_vta = ultima_vta + 1

        return "{}{}".format(prefix, qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(ultima_vta), 12 - len(prefix)))

    def utcToLocal(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset

    def distribucion_almacenes(self):
        jsonDatos = self.init_data

        codpago = self.get_codpago()
        if str(codpago) == "CREE":
            return True

        almacenes = self.dame_almacenes(jsonDatos)

        def puntua_combinacion(combinacion):
            print(str(combinacion))
            puntos = 100000 * self.puntos_productos_disponibles(combinacion)
            #print("disponibles:", str(puntos))
            puntos += 10000 * self.puntos_cantidad_almacenes(combinacion, almacenes)
            #print("cantidad almacenes:", str(puntos))
            puntos += 1000 * self.puntos_almacen_local(jsonDatos, combinacion)
            #print("almacen local:", str(puntos))
            puntos += 100 * self.puntos_prioridad(combinacion, almacenes)
            #print("prioridad:", str(puntos))
            puntos += 10 * self.puntos_bajo_limite(combinacion, almacenes)
            print("Puntos", str(puntos))
            return puntos

        combinaciones = self.combinaciones_almacenes(almacenes)
        if len(combinaciones) == 0:
            return True

        combinaciones_ordenadas = sorted(combinaciones, key=puntua_combinacion, reverse=True)
        mejor_combinacion = combinaciones_ordenadas[0]
        #print(str(combinaciones_ordenadas))
        print("MEJOR COMBINACION: ", str(mejor_combinacion))
        lineas_data = jsonDatos["order_lines"]
        disponibles = self.disponibles_x_almacen(mejor_combinacion)

        for linea in lineas_data:
            barcode = linea["product_sku"]
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

        codcanalweb = "WBNC"
        almacenes_sincro_mk = str(qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO_MK'")).replace(",", "','")
        print("almacenes: ", almacenes_sincro_mk)
        q = qsatype.FLSqlQuery()
        q.setSelect(u"a.codpais, a.email, a.codalmacen, ac.porcentajeteorico, ac.importeventas")
        q.setFrom(u"almacenes a INNER JOIN almacenescanalweb ac ON a.codalmacen = ac.codalmacen")
        q.setWhere(u"a.codalmacen IN ('" + almacenes_sincro_mk + "') ORDER BY ac.porcentajeteorico DESC")

        q.exec_()
        print(q.sql())

        if not q.size():
            return True
        
        lineas_data = self.init_data["order_lines"]
        
        barcodes = []
        lineas = {}
        for linea_data in lineas_data:
            barcode = linea_data["offer_sku"]
            barcodes.append(barcode)
            lineas[barcode] = linea_data["quantity"]

        if not "almacenes" in jsonDatos:
            jsonDatos["almacenes"] = []

        while q.next():
            jsonDatos["almacenes"].append({
                "source_code": str(q.value(u"a.codalmacen")),
                "email": str(q.value(u"a.email")),
                "country_id": str(q.value(u"a.codpais")),
                "porcentaje_teorico": parseFloat(q.value(u"ac.porcentajeteorico"))
            })

        almacenes = []

        # combinaciones_almacen = {}
        indice_limite = 0

        importe_total_ventas = parseFloat(qsatype.FLUtil.quickSqlSelect("almacenescanalweb", "SUM(importeventas)", "codcanalweb = '" + codcanalweb + "'"))

        for indice, almacen in enumerate(jsonDatos["almacenes"]):
            limite_pedido_minimo = qsatype.FLUtil.quickSqlSelect("param_parametros", "valor", "nombre = 'LPEDIDO_" + almacen["source_code"] + "'")
            if not limite_pedido_minimo:
                limite_pedido_minimo = 1000

            importe_total_ventas_almacen = parseFloat(qsatype.FLUtil.quickSqlSelect("almacenescanalweb", "importeventas", "codalmacen = '" + almacen["source_code"] + "' AND codcanalweb = '" + codcanalweb + "'"))

            porcentaje_tienda_real = 0
            if parseFloat(importe_total_ventas) != 0:
                porcentaje_tienda_real = (parseFloat(importe_total_ventas_almacen) * 100) / parseFloat(importe_total_ventas)


            prioridad_almacen = parseFloat(almacen["porcentaje_teorico"]) - parseFloat(porcentaje_tienda_real)

            # pedidos_almacen = qsatype.FLUtil.quickSqlSelect("eg_lineasecommerceexcluidas e INNER JOIN tpv_comandas c ON e.codcomanda = c.codigo", "COUNT(*)", "e.codalmacen = '" + almacen["source_code"] + "' AND c.fecha = CURRENT_DATE")
            pedidos_almacen = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "COUNT(*)", "fecha = CURRENT_DATE AND codigo like 'WEB%' and codtienda in ('AWEB','AWCL') and idtpv_comanda in (select c.idtpv_comanda from eg_lineasecommerceexcluidas le inner join tpv_lineascomanda l on le.idtpv_linea = l.idtpv_linea inner join tpv_comandas c on (l.idtpv_comanda = c.idtpv_comanda and le.codcomanda = c.codigo) WHERE le.codalmacen = '" + almacen["source_code"] + "' and c.fecha = CURRENT_DATE AND c.codigo like 'WEB%' and c.codtienda in ('AWEB','AWCL') group by c.idtpv_comanda)")

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
            while q.next():
                cant_disponible = q.value("disponible")
                if cant_disponible <= 0:
                    continue
                hay_disponible = True
                jBarcodes[q.value("barcode")] = cant_disponible

            if hay_disponible:
                if self.cod_almacenes == "":
                    self.cod_almacenes = "'" + almacen["source_code"] + "'"
                else:
                    self.cod_almacenes += ",'" + almacen["source_code"] + "'"

                almacenes.append({
                    "cod_almacen": almacen["source_code"],
                    "emailtienda": almacen["email"],
                    "total": 0,
                    "lineas": {},
                    "prioridad": prioridad_almacen,
                    "codpais": almacen["country_id"],
                    "bajo_limite": (int(limite_pedido_minimo)-int(pedidos_almacen)) / int(limite_pedido_minimo),
                    "disponibles": jBarcodes
                })

        if self.cod_almacenes != "":
            print("////////BARCODES CON STOCK: ", self.barcodes_lineas)
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
        lineas = self.init_data["order_lines"]
        max_puntos = len(lineas)
        if len(lineas) > self.barcodes_con_stock:
            max_puntos = len(lineas) - (len(lineas) - self.barcodes_con_stock)
        total_disponible = 0
        disponibles = self.disponibles_x_almacen(combinacion)
        for linea in lineas:
            barcode = linea["product_sku"]
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
            return pais == jsonDatos["customer"]["shipping_address"]["country"]

        max_puntos = len(combinacion)
        puntos = 0
        for i in range(len(combinacion)):
            puntos += 1 if es_local(combinacion[i]["codpais"]) else 0

        result = puntos * 10 / max_puntos
        return result

    def puntos_prioridad(self, combinacion, almacenes):
        prioridad = 0

        for almacen in combinacion:
            prioridad += almacen["prioridad"]

        result = prioridad * 10

        return result

    def puntos_bajo_limite(self, combinacion, almacenes):
        puntos = 0

        for almacen in combinacion:
            puntos += parseFloat(almacen["bajo_limite"])

        result = puntos * 10

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
        for linea in self.init_data["order_lines"]:
            if self.barcodes_lineas == "":
                self.barcodes_lineas = "'" + linea["product_sku"] + "'"
            else:
                self.barcodes_lineas += ",'" + linea["product_sku"] + "'"
        return True