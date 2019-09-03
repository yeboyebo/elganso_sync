from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.b2c.refounds.serializers.egrefound_line_serializer import EgRefoundLineSerializer
from controllers.api.b2c.refounds.serializers.egrefound_discountline_serializer import EgRefoundDiscountLineSerializer
from controllers.api.b2c.refounds.serializers.egrefound_pointline_serializer import EgRefoundPointLineSerializer
from controllers.api.b2c.refounds.serializers.egrefound_voucherline_serializer import EgRefoundVoucherLineSerializer
from controllers.api.b2c.orders.serializers.egcashcount_serializer import EgCashCountSerializer
from controllers.api.b2c.refounds.serializers.egrefound_payment_serializer import EgRefoundPaymentSerializer
from controllers.api.b2c.refounds.serializers.egidlecommerce_serializer import EgIdlEcommerce
from controllers.api.b2c.refounds.serializers.egidlecommercedevoluciones_serializer import EgIdlEcommerceDevoluciones


class EgRefoundsSerializer(DefaultSerializer):

    def get_data(self):
        if not self.control_tallas_devolucion():
            return False

        codigo = "WDV" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["refound_id"]), 9)

        if self.init_data["status"] != "Complete" or "items_requested" in self.init_data:

            idComanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
            if idComanda:
                return False

            self.crear_cabecera_comanda_devolucionweb(codigo)

            if "lines" not in self.data["children"]:
                self.data["children"]["lines"] = []

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []

            if "items_refunded" not in self.init_data:
                raise NameError("Error. No viene el nodo items_refunded en el JSON")

            iva = 0

            for line in self.init_data["items_refunded"]:
                line.update({
                    "codcomanda": codigo,
                    "tipo_linea": "refounded"
                })

                line_data = EgRefoundLineSerializer().serialize(line)
                self.data["children"]["lines"].append(line_data)
                iva = line["tax_percent"]

            if "items_requested" in self.init_data:
                for linea in self.init_data["items_requested"]:
                    linea.update({
                        "codcomanda": codigo,
                        "tipo_linea": "requested"
                    })
                    line_data = EgRefoundLineSerializer().serialize(linea)
                    self.data["children"]["lines"].append(line_data)


            self.crear_registros_descuentos(iva)
            self.crear_registros_puntos(iva)
            self.crear_registros_vales(iva)
            self.data["children"]["cashcount"] = False
        else:

            if "lines" not in self.data["children"]:
                self.data["children"]["lines"] = []

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []

            idComanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
            if not idComanda:
                return False

        if self.init_data["status"] == "Complete" or "items_requested" in self.init_data:
            self.cerrar_devolucionweb(codigo)

        if self.init_data["status"] != "Complete" or "items_requested" in self.init_data:
            for linea in self.init_data["items_refunded"]:
                linea.update({
                    "codcomanda": codigo
                })
                if not self.crear_motivos_devolucion(linea):
                    return False
                if not self.crear_registros_ecommerce():
                    return False

        return True

    def crear_cabecera_comanda_devolucionweb(self, codigo):
        self.set_string_value("codigo", codigo[:15])
        self.set_string_relation("email", "email", max_characters=100)
        self.set_string_value("codigo", codigo[:15])

        cif = self.init_data["cif"][:20] if self.init_data["cif"] and self.init_data["cif"] != "" else ""
        if not cif or cif == "":
            cif = "-"

        self.set_string_value("cif", cif)

        nombreCliente = str(self.init_data["pickup_address"]["firstname"]) + " " + str(self.init_data["pickup_address"]["lastname"])

        direccion = self.init_data["pickup_address"]["street"]
        dirNum = self.init_data["pickup_address"]["number"]
        if str(dirNum) == "None":
            dirNum = ""

        codpostal = str(self.init_data["pickup_address"]["postcode"])
        codComandaDevol = "WEB" + str(self.init_data["increment_id"])
        city = self.init_data["pickup_address"]["city"]
        codpais = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codpais", "codigo = '" + str(codComandaDevol) + "'")
        telefonofac = self.init_data["phone"]
        codpago = self.get_codpago(str(self.init_data["payment_method"]))
        email = self.init_data["email"]
        codtarjetapuntos = self.init_data["card_points"]
        region = self.init_data["pickup_address"]["region"]
        codDivisa = str(self.init_data["currency"])

        totalIva = parseFloat(self.init_data["tax_refunded"])
        totalVenta = parseFloat(self.init_data["subtotal_refunded"]) - parseFloat(self.init_data["discount_refunded"]) - parseFloat(self.init_data["vale_total"])
        totalNeto = totalVenta - totalIva

        if "items_requested" in self.init_data:
            totalNeto = 0
            totalIva = 0
            totalVenta = 0

        self.set_string_value("codserie", self.get_codserie(codpais, self.init_data["pickup_address"]["postcode"]))
        self.set_string_value("codejercicio", self.get_codejercicio(str(qsatype.Date())))
        self.set_string_value("codcomandadevol", str(codComandaDevol))
        self.set_string_value("codtpv_puntoventa", "AWEB")
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("codalmacen", "AWEB")
        self.set_string_value("codtienda", "AWEB")
        self.set_string_value("fecha", str(qsatype.Date())[:10])
        self.set_string_value("hora", self.get_hora(str(qsatype.Date())))
        self.set_string_value("nombrecliente", nombreCliente[:100] if nombreCliente else nombreCliente)
        self.set_string_value("cifnif", cif)
        self.set_string_value("dirtipovia", "")
        self.set_string_value("direccion", direccion[:100] if direccion else direccion)
        self.set_string_value("dirnum", dirNum[:100] if dirNum else dirNum)
        self.set_string_value("dirotros", "")
        self.set_string_value("codpostal", codpostal[:10] if codpostal else codpostal)
        self.set_string_value("ciudad", city[:100] if city else city)
        self.set_string_value("provincia", region[:100] if region else region)
        self.set_string_value("telefono1", telefonofac[:30] if telefonofac else telefonofac)
        self.set_string_value("codpais", codpais)
        self.set_string_value("codpago", codpago[:10] if codpago else codpago)
        self.set_string_value("coddivisa", codDivisa)
        self.set_string_value("tasaconv", 1)
        self.set_string_value("email", email[:100] if email else email)
        self.set_string_value("neto", totalNeto * (-1))
        self.set_string_value("totaliva", totalIva * (-1))
        self.set_string_value("total", totalVenta * (-1))
        self.set_string_value("codtarjetapuntos", codtarjetapuntos[:15] if codtarjetapuntos else codtarjetapuntos)
        self.set_string_value("ptesincrofactura", False)
        self.set_string_value("egcodfactura", "")
        total = totalVenta * (-1)
        tipoDoc = "VENTA"
        if total < 0:
            tipoDoc = "DEVOLUCION"
        self.set_string_value("tipodoc", tipoDoc)

        return True

    def get_codserie(self, nomPais, codPostal):
        codPais = None
        codSerie = "A"
        codPostal2 = None

        if not nomPais or nomPais == "":
            return codSerie

        codPais = qsatype.FLUtil.quickSqlSelect("paises", "codpais", "UPPER(codpais) = '" + nomPais.upper() + "'")
        if not codPais or codPais == "":
            return codSerie

        if codPais != "ES":
            codSerie = "X"
        elif codPostal and codPostal != "":
            codPostal2 = codPostal[:2]
            if codPostal2 == "35" or codPostal2 == "38" or codPostal2 == "51" or codPostal2 == "52":
                codSerie = "X"

        return codSerie

    def get_codejercicio(self, fecha):
        fecha = fecha[:10]
        datosFecha = fecha.split("-")

        return datosFecha[0]

    def get_hora(self, fecha):
        h = fecha[-(8):]
        h = "23:59:59" if h == "00:00:00" else h
        return h

    def get_codpago(self, metPago):
        codPago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '" + metPago + "'")
        if not codPago:
            codPago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")

        return codPago

    def control_tallas_devolucion(self):

        refDevol = ""
        refCambio = False

        for linea in self.init_data["items_refunded"]:
            refDevol = self.get_referencia(linea["sku"])

        if "items_requested" in self.init_data:
            for linea in self.init_data["items_requested"]:
                refCambio = self.get_referencia(linea["sku"])

        if not refCambio:
            return True

        if refDevol != refCambio:
            return False

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

    def crear_registros_descuentos(self, iva):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "BonoPositivo"
        })
        linea_descuento = EgRefoundDiscountLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_descuento)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "BonoNegativo"
            })
            linea_descuento = EgRefoundDiscountLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_descuento)

    def crear_registros_puntos(self, iva):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "PuntosPositivos"
        })

        linea_puntos = EgRefoundPointLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_puntos)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "PuntosNegativos"
            })
            linea_puntos = EgRefoundPointLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_puntos)

    def crear_registros_vales(self, iva):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "ValesPositivos"
        })
        linea_vale = EgRefoundVoucherLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_vale)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "ValesNegativos"
            })
            linea_vale = EgRefoundVoucherLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_vale)

    def cerrar_devolucionweb(self, codigo):

        self.data.update({
            "fecha": qsatype.Date()
        })
        arqueo_web = EgCashCountSerializer().serialize(self.data)

        if "skip" in arqueo_web and arqueo_web["skip"]:
            self.data["children"]["cashcount"] = False
        else:
            self.data["children"]["cashcount"] = arqueo_web

        self.crear_pagos_devolucionweb(arqueo_web, codigo)

        idFactura = qsatype.FLUtil.sqlSelect("tpv_comandas", "idfactura", "codigo = '" + str(codigo) + "'")

        if (not idFactura or str(idFactura) == "None" or idFactura == 0) and (not "items_requested" in self.init_data):
            self.set_string_value("ptesincrofactura", True)
            self.set_string_value("fecha", str(qsatype.Date())[:10])

        self.set_string_value("estado", 'Cerrada')
        self.set_string_value("editable", True)

        if "items_requested" in self.init_data:
            self.set_string_value("pagado", "0")
        else:
            self.set_string_value("pagado", float(self.init_data["total_pay"]) * (-1))

        return True


    def crear_pagos_devolucionweb(self, arqueo_web, codigo):
        new_init_data = self.init_data.copy()
        new_init_data.update(
            {"idarqueo": arqueo_web["idtpv_arqueo"],
            "tipo_pago": "Negativo",
            "codcomanda": codigo
            }
        )

        pago_web = EgRefoundPaymentSerializer().serialize(new_init_data)
        self.data["children"]["payments"].append(pago_web)

        if "items_requested" in self.init_data:
            print("entra")
            new_init_data = self.init_data.copy()
            new_init_data.update(
                {"idarqueo": arqueo_web["idtpv_arqueo"],
                "tipo_pago": "Positivo",
                "codcomanda": codigo
                }
            )
            pago_web = EgRefoundPaymentSerializer().serialize(new_init_data)
            self.data["children"]["payments"].append(pago_web)

        return True

    def crear_motivos_devolucion(self, linea):
        if not self.crear_registro_devolucion_tienda(linea):
            return False

        if not self.crear_registro_devolucion(linea):
            return False

        return True

    def crear_registro_devolucion_tienda(self, linea):

        codigo = linea["codcomanda"]
        curDevolT = qsatype.FLSqlCursor("eg_devolucionestienda")
        curDevolT.select("codcomandaoriginal = '" + "WEB" + str(self.init_data["increment_id"]) + "' AND coddevolucion = '" + str(codigo) + "'")
        if curDevolT.first():
            return True

        curDevolT = qsatype.FLSqlCursor("eg_devolucionestienda")
        curDevolT.setModeAccess(curDevolT.Insert)
        curDevolT.refreshBuffer()
        curDevolT.setValueBuffer("codcomandaoriginal", "WEB" + str(self.init_data["increment_id"]))
        curDevolT.setValueBuffer("coddevolucion", str(codigo))
        curDevolT.setValueBuffer("sincronizada", True)
        curDevolT.setValueBuffer("fecha", str(qsatype.Date())[:10])
        curDevolT.setValueBuffer("hora", self.get_hora(str(qsatype.Date())))
        curDevolT.setValueBuffer("idsincro", str(codigo) + "_" + str(curDevolT.valueBuffer("id")))
        curDevolT.setValueBuffer("codtienda", "AWEB")

        if "items_requested" in self.init_data:
            curDevolT.setValueBuffer("codcomandacambio", str(codigo))
            curDevolT.setValueBuffer("cambio", True)
        else:
            curDevolT.setNull("codcomandacambio")
            curDevolT.setValueBuffer("cambio", False)

        if not curDevolT.commitBuffer():
            return False

        return True

    def crear_registro_devolucion(self, linea):

        codigo = linea["codcomanda"]
        curMotivos = qsatype.FLSqlCursor("eg_motivosdevolucion")
        curMotivos.setModeAccess(curMotivos.Insert)
        curMotivos.refreshBuffer()
        curMotivos.setValueBuffer("codcomandadevol", str(codigo))
        curMotivos.setValueBuffer("referencia", self.get_referencia(linea["sku"]))
        curMotivos.setValueBuffer("barcode", self.get_barcode(linea["sku"]))
        curMotivos.setValueBuffer("descripcion", self.get_descripcion(linea["sku"]))
        curMotivos.setValueBuffer("talla", self.get_talla(linea["sku"]))
        curMotivos.setValueBuffer("cantidad", parseFloat(linea["qty"]))
        curMotivos.setValueBuffer("pvpunitarioiva", parseFloat(linea["original_price"]))
        curMotivos.setValueBuffer("idsincro", str(codigo) + "_" + str(curMotivos.valueBuffer("id")))
        curMotivos.setValueBuffer("motivos", str(linea["reason"]))
        curMotivos.setValueBuffer("sincronizada", True)
        if not curMotivos.commitBuffer():
            return False

        return True

    def crear_registros_ecommerce(self):
        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
        })
        idl_ecommerce_devolucion = EgIdlEcommerceDevoluciones().serialize(new_init_data)
        self.data["children"]["idl_ecommerce_devolucion"] = idl_ecommerce_devolucion

        if "items_requested" in self.init_data:
            idl_ecommerce = EgIdlEcommerce().serialize(new_init_data)
            self.data["children"]["idl_ecommerce"] = idl_ecommerce

        return True