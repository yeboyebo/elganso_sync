from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer
from controllers.api.magento2.refounds.serializers.mg2_refound_line_serializer import Mg2RefoundLineSerializer
from controllers.api.magento2.refounds.serializers.mg2_refound_discountline_serializer import Mg2RefoundDiscountLineSerializer
from controllers.api.magento2.refounds.serializers.mg2_refound_pointline_serializer import Mg2RefoundPointLineSerializer
from controllers.api.magento2.refounds.serializers.mg2_refound_voucherline_serializer import Mg2RefoundVoucherLineSerializer
from controllers.api.magento2.orders.serializers.mg2_cashcount_serializer import Mg2CashCountSerializer
from controllers.api.magento2.refounds.serializers.mg2_refound_payment_serializer import Mg2RefoundPaymentSerializer
from controllers.api.magento2.refounds.serializers.mg2_idlecommerce_serializer import Mg2IdlEcommerce
from controllers.api.magento2.refounds.serializers.mg2_idlecommercedevoluciones_serializer import Mg2IdlEcommerceDevoluciones
from controllers.api.magento2.refounds.serializers.mg2_refound_expensesline_serializer import Mg2RefoundExpensesLineSerializer
from controllers.api.magento2.refounds.serializers.mg2_refound_tarjetaregaloline_serializer import Mg2RefoundTarjetaMonederoSerializer


class Mg2RefoundsSerializer(DefaultSerializer):

    def get_data(self):
        if not self.control_tallas_devolucion():
            return False

        if str(self.init_data["status"]) == "creditmemo":
            if not self.control_creditmemo():
                return False

        codigo = "WDV2" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 8)

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

        if self.init_data["status"] != "Complete" or "items_requested" in self.init_data:

            idComanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
            if idComanda:
                return False

            tasaconv = 1
            divisa = str(self.init_data["currency"])

            if divisa:
                if divisa != "None" and divisa != "EUR" and divisa != "CLP":
                    tasaconv = qsatype.FLUtil.quickSqlSelect("divisas", "tasaconv", "coddivisa = '{}'".format(divisa))
                    if not tasaconv:
                        tasaconv = 1

            self.init_data["tasaconv"] = tasaconv

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
                    "tipo_linea": "refounded",
                    "tasaconv": tasaconv
                })

                if "codtiendaentrega" in self.init_data:
                    if str(self.init_data["codtiendaentrega"]) != "AWEB":
                        line.update({
                         "codtiendaentrega": self.init_data["codtiendaentrega"]
                        })

                line_data = Mg2RefoundLineSerializer().serialize(line)
                self.data["children"]["lines"].append(line_data)
                iva = line["tax_percent"]

            if "items_requested" in self.init_data:
                for linea in self.init_data["items_requested"]:
                    linea.update({
                        "codcomanda": codigo,
                        "tipo_linea": "requested",
                        "tasaconv": tasaconv
                    })
                    line_data = Mg2RefoundLineSerializer().serialize(linea)
                    self.data["children"]["lines"].append(line_data)

            if "codtiendaentrega" in self.init_data:
                if str(self.init_data["codtiendaentrega"]) != "AWEB":
                    if "numero_seguimiento" in self.init_data:
                        if str(self.init_data["numero_seguimiento"]) != "None" and str(self.init_data["numero_seguimiento"]) != "":
                            self.crearSeguimientoEnvio(codigo)

            self.crear_registros_descuentos(iva)
            self.crear_registros_puntos(iva)
            self.crear_registros_vales(iva, False)
            self.crear_registros_gastosenvio(iva)
            self.crear_registros_tarjetamonedero(iva)

            if "gastos_envio" in self.init_data:
                if "importe_gastosenvio" in self.init_data["gastos_envio"]:
                    if str(self.init_data["gastos_envio"]["importe_gastosenvio"]) != "None":
                        if float(self.init_data["gastos_envio"]["importe_gastosenvio"]) > 0:
                            self.crear_comanda_gastosenvio()

            self.data["children"]["cashcount"] = False
            self.data["children"]["creditmemo"] = False
            if str(self.init_data["status"]) == "creditmemo":
                self.data["children"]["creditmemo"] = True
        else:

            tasaconv = 1
            divisa = str(self.init_data["currency"])
            if divisa:
                if divisa != "None" and divisa != "EUR" and divisa != "CLP":
                    tasaconv = qsatype.FLUtil.quickSqlSelect("divisas", "tasaconv", "coddivisa = '{}'".format(divisa))
                    if not tasaconv:
                        tasaconv = 1

            self.init_data["tasaconv"] = tasaconv

            if "lines" not in self.data["children"]:
                self.data["children"]["lines"] = []

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []

            idComanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
            if not idComanda:
                return False

        if self.init_data["status"] == "Complete" or "items_requested" in self.init_data or self.init_data["status"] == "creditmemo":
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

        # nombreCliente = str(self.init_data["pickup_address"]["firstname"]) + " " + str(self.init_data["pickup_address"]["lastname"])
        nombreCliente = str(self.init_data["pickup_address"]["firstname"])

        direccion = self.init_data["pickup_address"]["street"]
        dirNum = self.init_data["pickup_address"]["number"]
        if str(dirNum) == "None":
            dirNum = ""

        codpostal = str(self.init_data["pickup_address"]["postcode"])
        codComandaDevol = "WEB" + str(self.init_data["increment_id"])
        city = self.init_data["pickup_address"]["city"]
        codpais = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codpais", "codigo = '" + str(codComandaDevol) + "'")
        telefonofac = self.init_data["phone"]
        if "phone" in self.init_data["pickup_address"]:
            telefonofac = self.init_data["pickup_address"]["phone"]
        codpago = self.get_codpago(str(self.init_data["payment_method"]))
        email = self.init_data["email"]
        region = self.init_data["pickup_address"]["region"]
        codDivisa = str(self.init_data["currency"])

        iva = 0
        for line in self.init_data["items_refunded"]:
            iva = parseFloat(line["tax_percent"])

        #totalIva = parseFloat(self.init_data["tax_refunded"]) * self.init_data["tasaconv"]
        totalVenta = parseFloat(self.init_data["total_refunded"]) * parseFloat(self.init_data["tasaconv"])
        totalNeto = round(parseFloat(totalVenta / ((100 + iva) / 100)), 2)
        totalIva = parseFloat(totalVenta - totalNeto)

        if "items_requested" in self.init_data:
            totalNeto = 0
            totalIva = 0
            totalVenta = 0

        self.set_string_value("codserie", self.get_codserie(codpais, self.init_data["pickup_address"]["postcode"]))
        self.set_string_value("codejercicio", self.get_codejercicio(str(qsatype.Date())))
        self.set_string_value("codcomandadevol", str(codComandaDevol))
        self.set_string_value("codtpv_puntoventa", self.get_puntoventa())
        self.set_string_value("codtpv_agente", "0350")
        self.set_string_value("codalmacen", "AWEB")
        self.set_string_value("codtienda", self.get_codtienda())
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
        self.set_string_value("codtarjetapuntos", self.get_codtarjetapuntos(), max_characters=15)
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
        return True
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
        linea_descuento = Mg2RefoundDiscountLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_descuento)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "BonoNegativo"
            })
            linea_descuento = Mg2RefoundDiscountLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_descuento)

    def crear_registros_puntos(self, iva):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "PuntosPositivos"
        })

        linea_puntos = Mg2RefoundPointLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_puntos)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "PuntosNegativos"
            })
            linea_puntos = Mg2RefoundPointLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_puntos)

    def crear_registros_vales(self, iva, crear_movimiento_vale):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "ValesNegativos",
            "crear_movimiento_vale": crear_movimiento_vale
        })
        linea_vale = Mg2RefoundVoucherLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_vale)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "ValesPositivos",
                "crear_movimiento_vale": crear_movimiento_vale
            })
            linea_vale = Mg2RefoundVoucherLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_vale)

    def cerrar_devolucionweb(self, codigo):
        if "codtiendaentrega" in self.init_data:
            if str(self.init_data["codtiendaentrega"]) != "AWEB":
                idComandaPago = qsatype.FLUtil.sqlSelect("tpv_comandas c INNER JOIN tpv_pagoscomanda p ON c.idtpv_comanda = p.idtpv_comanda", "p.idtpv_comanda", "c.codigo = '" + str(codigo) + "'")
                if idComandaPago:
                    self.crear_registro_puntos(codigo)
                    raise NameError("La devolucion ya ha sido procesada en una tienda.")
                    return False

        idComandaPago = qsatype.FLUtil.sqlSelect("tpv_comandas c INNER JOIN tpv_pagoscomanda p ON c.idtpv_comanda = p.idtpv_comanda", "p.idtpv_comanda", "c.codigo = '" + str(codigo) + "'")
        if idComandaPago:
            raise NameError("La devolucion ya tiene un pago creado.")
            return False

        tasaconv = 1
        divisa = str(self.init_data["currency"])
        if divisa:
            if divisa != "None" and divisa != "EUR" and divisa != "CLP":
                tasaconv = qsatype.FLUtil.quickSqlSelect("divisas", "tasaconv", "coddivisa = '{}'".format(divisa))
                if not tasaconv:
                    tasaconv = 1

        self.init_data["tasaconv"] = tasaconv

        if str(self.init_data["store_id"]) == "13" or str(self.init_data["store_id"]) == "14":
            codtienda = self.get_codtienda()
        else:
            codtienda = "AWEB"

        self.data.update({
            "fecha": qsatype.Date(),
            "codtienda": codtienda,
            "codigo": codigo
        })
        arqueo_web = Mg2CashCountSerializer().serialize(self.data)

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
            self.set_string_value("pagado", float(self.init_data["total_pay"] * self.init_data["tasaconv"]) * (-1))

        if self.init_data["status"] == "creditmemo":
            if str(self.init_data["store_id"]) == "13":
                codtiendaentrega = "ACHI"
                if "codtiendaentrega" in self.init_data:
                    if str(self.init_data["codtiendaentrega"]) != "AWEB":
                        codtiendaentrega = self.init_data["codtiendaentrega"]
                        if not self.crear_viaje_recogidatienda(self.data["codigo"], codtiendaentrega):
                            raise NameError("Error al crear el viaje de recogida en tienda.")

        self.crear_registro_puntos(codigo)
        self.crear_registros_vales(False, True)

        return True

    def crear_pagos_devolucionweb(self, arqueo_web, codigo):
        tasaconv = 1
        divisa = str(self.init_data["currency"])
        if divisa:
            if divisa != "None" and divisa != "EUR" and divisa != "CLP":
                tasaconv = qsatype.FLUtil.quickSqlSelect("divisas", "tasaconv", "coddivisa = '{}'".format(divisa))
                if not tasaconv:
                    tasaconv = 1

        self.init_data["tasaconv"] = tasaconv

        new_init_data = self.init_data.copy()
        new_init_data.update(
            {"idarqueo": arqueo_web["idtpv_arqueo"],
            "tipo_pago": "Negativo",
            "codcomanda": codigo,
            "codtienda": self.get_codtienda(),
            "puntoventa": self.get_puntoventa()
            }
        )

        if "payments" not in self.data["children"]:
            self.data["children"]["payments"] = []
        
        pago_web = Mg2RefoundPaymentSerializer().serialize(new_init_data)
        self.data["children"]["payments"].append(pago_web)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update(
                {"idarqueo": arqueo_web["idtpv_arqueo"],
                "tipo_pago": "Positivo",
                "codcomanda": codigo,
                "codtienda": self.get_codtienda(),
                "puntoventa": self.get_puntoventa()
                }
            )
            pago_web = Mg2RefoundPaymentSerializer().serialize(new_init_data)
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
        curMotivos.setValueBuffer("pvpunitarioiva", parseFloat(linea["original_price"] * self.init_data["tasaconv"]))
        curMotivos.setValueBuffer("idsincro", str(codigo) + "_" + str(curMotivos.valueBuffer("id")))
        curMotivos.setValueBuffer("motivos", str(linea["reason"]))
        curMotivos.setValueBuffer("sincronizada", True)
        if not curMotivos.commitBuffer():
            return False

        return True

    def crear_registros_ecommerce(self):
        if self.init_data["status"] == "creditmemo":
            return True
        new_init_data = self.init_data.copy()
        excluir_idl = False
        """if str(self.init_data["warehouse"]) != "AWEB":
            excluir_idl = True"""

        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "excluir_idl": excluir_idl
        })

        if excluir_idl == True:
            if not self.crear_viaje_recogidatienda(self.data["codigo"]):
                raise NameError("Error al crear el viaje de recogida en tienda.")

        idl_ecommerce_devolucion = Mg2IdlEcommerceDevoluciones().serialize(new_init_data)
        self.data["children"]["idl_ecommerce_devolucion"] = idl_ecommerce_devolucion

        excluir_idl = False
        if "items_requested" in self.init_data:
            idl_ecommerce = Mg2IdlEcommerce().serialize(new_init_data)
            self.data["children"]["idl_ecommerce"] = idl_ecommerce

        return True

    def crear_viaje_recogidatienda(self, codcomanda, codtiendaentrega):

        id_viaje =  qsatype.FactoriaModulos.get("formRecordtpv_comandas").iface.obtenerIdViaje()

        if not id_viaje or str(id_viaje) == "None" or id_viaje == None:
            raise NameError("No se ha podido calcular el idviaje.")
            return False

        cantidad_viaje = 0
        for linea in self.init_data["items_refunded"]:
            cantidad_viaje += parseFloat(linea["qty"])

        if cantidad_viaje <= 0:
            raise NameError("La cantidad para crear el viaje es menor o igual que cero.")
            return False

        nombre_destino = str(qsatype.FLUtil.quickSqlSelect("almacenes", "nombre", "codalmacen = '" + str(codtiendaentrega) + "'"))
        curViaje = qsatype.FLSqlCursor("tpv_viajesmultitransstock")
        curViaje.setModeAccess(curViaje.Insert)
        curViaje.refreshBuffer()
        curViaje.setValueBuffer("idviajemultitrans", id_viaje)
        curViaje.setValueBuffer("fecha", qsatype.Date())
        curViaje.setValueBuffer("codalmaorigen", "AWEB")
        curViaje.setValueBuffer("nombreorigen", "WEB")
        curViaje.setValueBuffer("codalmadestino", str(codtiendaentrega))
        curViaje.setValueBuffer("nombredestino", nombre_destino)
        curViaje.setValueBuffer("cantidad", cantidad_viaje)
        curViaje.setValueBuffer("estado", "RECIBIDO")
        curViaje.setValueBuffer("enviocompletado", True)
        curViaje.setValueBuffer("ptesincroenvio", True)
        curViaje.setValueBuffer("recepcioncompletada", True)
        curViaje.setValueBuffer("azkarok", False)
        curViaje.setValueBuffer("egnumseguimiento", codcomanda)

        if not curViaje.commitBuffer():
            raise NameError("Error al guardar la cabecera del viaje.")
            return False

        num_linea = 1
        for linea in self.init_data["items_refunded"]:
            if not self.crear_lineas_viaje_recogidatienda(id_viaje, linea, num_linea, str(codtiendaentrega)):
                raise NameError("Error al crear las líneas del viaje.")
                return False
            num_linea += 1


        if not qsatype.FLUtil.execSql("INSERT INTO eg_viajeswebtiendaptes (idviajemultitrans) VALUES ('" + str(id_viaje) + "')"):
            raise NameError("Error al insertar el registro en eg_viajeswebtiendaptes.")
            return False

        return True

    def crear_lineas_viaje_recogidatienda(self, id_viaje, linea, num_linea, codtiendaentrega):

        if parseFloat(linea["qty"]) <= 0:
            raise NameError("La cantidad de la línea es menor o igual que cero.")
            return False

        curLV = qsatype.FLSqlCursor("tpv_lineasmultitransstock")
        curLV.setModeAccess(curLV.Insert)
        curLV.setActivatedCommitActions(False)
        curLV.setActivatedCheckIntegrity(False)
        curLV.refreshBuffer()
        curLV.setValueBuffer("idviajemultitrans", id_viaje)
        curLV.setValueBuffer("referencia", self.get_referencia(linea["sku"]))
        curLV.setValueBuffer("descripcion", self.get_descripcion(linea["sku"]))
        curLV.setValueBuffer("barcode", self.get_barcode(linea["sku"]))
        curLV.setValueBuffer("talla", self.get_talla(linea["sku"]))
        curLV.setValueBuffer("codalmaorigen", "AWEB")
        curLV.setValueBuffer("codalmadestino", str(codtiendaentrega))
        curLV.setValueBuffer("estado", "RECIBIDO")
        curLV.setValueBuffer("cantidad", parseFloat(linea["qty"]))
        curLV.setValueBuffer("numlinea", num_linea)
        curLV.setValueBuffer("cantpteenvio", 0)
        curLV.setValueBuffer("cantenviada", parseFloat(linea["qty"]))
        curLV.setValueBuffer("cantpterecibir", parseFloat(linea["qty"]))
        curLV.setValueBuffer("cantrecibida", parseFloat(linea["qty"]))
        curLV.setValueBuffer("excentral", "OK")
        curLV.setValueBuffer("extienda", "OK")
        curLV.setValueBuffer("rxcentral", "OK")
        curLV.setValueBuffer("rxtienda", "OK")
        curLV.setValueBuffer("ptestockcentral", False)
        curLV.setValueBuffer("cerradorx", False)
        curLV.setValueBuffer("cerradoex", False)
        curLV.setValueBuffer("revisada", False)
        curLV.setValueBuffer("ptestockrx", False)
        curLV.setValueBuffer("fechaex", str(qsatype.Date())[:10])
        curLV.setValueBuffer("horaex", self.get_hora(str(qsatype.Date())))
        curLV.setValueBuffer("fecharx", str(qsatype.Date())[:10])
        curLV.setValueBuffer("horarx", self.get_hora(str(qsatype.Date())))
        curLV.setValueBuffer("idsincro", "CENTRAL_" + str(curLV.valueBuffer("idlinea")))

        if not curLV.commitBuffer():
            raise NameError("Error al guardar la línea del viaje.")
            return False

        if not qsatype.FactoriaModulos.get("flfactalma").iface.generarEstructuraMTOrigen(curLV):
            raise NameError("No se ha podido crear los movimientos de stock de origen.")
            return False

        if not qsatype.FactoriaModulos.get("flfactalma").iface.generarEstructuraMTDestino(curLV):
            raise NameError("No se ha podido crear los movimientos de stock de destino.")
            return False

        return True

    def crear_registros_gastosenvio(self, iva):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "GastosNegativos"
        })
        linea_gastosenvio = Mg2RefoundExpensesLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_gastosenvio)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "GastosPositivos"
            })
            linea_gastosenvio = Mg2RefoundExpensesLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_gastosenvio)

    def get_codtarjetapuntos(self):
        codtarjetapuntos = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codtarjetapuntos", "codigo = '{}'".format("WEB" + str(self.init_data["increment_id"])))

        if not codtarjetapuntos:
            codtarjetapuntos = ""

        return codtarjetapuntos

    def control_creditmemo(self):
        if not qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codigo", "codcomandadevol = '{}'".format("WEB" + str(self.init_data["increment_id"]))):
            return True

        idtpv_comanda_original = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '{}'".format("WEB" + str(self.init_data["increment_id"])))
        cod_comanda_original = "WEB" + str(self.init_data["increment_id"])

        for line in self.init_data["items_refunded"]:
            barcode_linea = self.get_barcode(line["sku"])
            if qsatype.FLUtil.quickSqlSelect("eg_devolucionesweb dw INNER JOIN tpv_comandas c ON dw.codventa = c.codigo INNER JOIN tpv_lineascomanda lc ON c.idtpv_comanda = lc.idtpv_comanda", "lc.barcode", "dw.codventa = '{}' AND lc.barcode = '{}'".format(cod_comanda_original, barcode_linea), "eg_devolucionesweb,tpv_comandas,tpv_lineascomanda"):
                raise NameError("Error CreditMemo. Devolucion ya realizada en una tienda.")
                return False

            cant_inicial = parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "SUM(cantidad)", "barcode = '{}' AND idtpv_comanda = '{}'".format(barcode_linea, idtpv_comanda_original)))

            cant_devuelta = parseFloat(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "SUM(cantdevuelta)", "barcode = '{}' AND idtpv_comanda = '{}'".format(barcode_linea, idtpv_comanda_original)))

            if (parseFloat(line["qty"]) + cant_devuelta) > cant_inicial:
                raise NameError("Error CreditMemo. La cantidad de la devolucion mas lo devuelto supera la cantidad original de la venta.")
                return False
        return True

    def get_codtienda(self):
        if str(self.init_data["store_id"]) == "13" or str(self.init_data["store_id"]) == "14":
            return qsatype.FLUtil.quickSqlSelect("mg_storeviews", "egcodtiendarebajas", "idmagento = '{}'".format(str(self.init_data["store_id"])))
        return "AWEB"

    def get_puntoventa(self):
        if str(self.init_data["store_id"]) == "13" or str(self.init_data["store_id"]) == "14":
            return qsatype.FLUtil.quickSqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = '{}'".format(str(self.get_codtienda())))
        return "AWEB"

    def crearSeguimientoEnvio(self, codigo):

        items = []
        for line in self.init_data["items_refunded"]:
            items.append({"sku" : line["sku"], "qty": line["qty"], "almacen": str(self.init_data["codtiendaentrega"])})

        curSegEnvio = qsatype.FLSqlCursor("eg_seguimientoenvios")
        curSegEnvio.setModeAccess(curSegEnvio.Insert)
        curSegEnvio.refreshBuffer()
        curSegEnvio.setValueBuffer("informadocompleto", False)
        curSegEnvio.setValueBuffer("fechamagento", str(qsatype.Date())[:10])
        curSegEnvio.setValueBuffer("horamagento", str(qsatype.Date())[-(8):])
        if str(self.init_data["numero_seguimiento"]) != "False":
            num_seguimiento = self.init_data["numero_seguimiento"].replace(" ", "")
            num_seguimiento = num_seguimiento.split(":")
            curSegEnvio.setValueBuffer("transportista", num_seguimiento[0])
            curSegEnvio.setValueBuffer("numseguimiento", num_seguimiento[1])
        else:
            curSegEnvio.setValueBuffer("numseguimiento", codigo)

        curSegEnvio.setValueBuffer("codalmacen", str(self.init_data["codtiendaentrega"]))
        curSegEnvio.setValueBuffer("tipo", "ECOMMERCE")
        curSegEnvio.setValueBuffer("items", items)
        curSegEnvio.setValueBuffer("numseguimientoinformado", True)
        curSegEnvio.setValueBuffer("coddocumento", codigo)

        if not curSegEnvio.commitBuffer():
            return True

        return True

    def crear_movimiento_tarjeta_monedero(self):

        codigo = "WDV2" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 8)
        id_tarjeta = qsatype.FLUtil.quickSqlSelect("eg_tarjetamonedero", "idtarjeta", "coduso = '{}'".format(str(self.init_data["tarjeta_monedero"]["cod_uso"])))

        curTarjeta = qsatype.FLSqlCursor("eg_movitarjetamonedero")
        curTarjeta.setModeAccess(curTarjeta.Insert)
        curTarjeta.refreshBuffer()
        curTarjeta.setValueBuffer("fecha", str(qsatype.Date())[:10])
        curTarjeta.setValueBuffer("hora", self.get_hora(str(qsatype.Date())))
        curTarjeta.setValueBuffer("idtarjeta", id_tarjeta)
        curTarjeta.setValueBuffer("importe", parseFloat(self.init_data["tarjeta_monedero"]["importe_gastado"]))
        curTarjeta.setValueBuffer("codcomanda", codigo)
        curTarjeta.setValueBuffer("coduso", str(self.init_data["tarjeta_monedero"]["cod_uso"]))
        if not curTarjeta.commitBuffer():
            return False

        if not qsatype.FLUtil.execSql(ustr(u"UPDATE eg_tarjetamonedero SET saldoconsumido = CASE WHEN (SELECT SUM(importe) FROM eg_movitarjetamonedero WHERE idtarjeta = eg_tarjetamonedero.idtarjeta) IS NULL THEN 0 ELSE (SELECT SUM(importe) FROM eg_movitarjetamonedero WHERE idtarjeta = eg_tarjetamonedero.idtarjeta) * (-1) END WHERE idtarjeta =  {}".format(str(id_tarjeta)))):
            return False

        if not qsatype.FLUtil.execSql(ustr(u"UPDATE eg_tarjetamonedero SET saldopendiente = CASE WHEN (saldoinicial - saldoconsumido) IS NULL THEN 0 ELSE (saldoinicial - saldoconsumido) END, fechamod = CURRENT_DATE, horamod = CURRENT_TIME WHERE idtarjeta = {}".format(str(id_tarjeta)))):
            return False

        return True

    def crear_registros_tarjetamonedero(self, iva):


        if "tarjeta_monedero" in self.init_data:
            if "importe_gastado" in self.init_data["tarjeta_monedero"]:
                if float(self.init_data["tarjeta_monedero"]["importe_gastado"]) > 0:
                    new_init_data = self.init_data.copy()
                    new_init_data.update({
                        "cod_uso": str(self.init_data["tarjeta_monedero"]["cod_uso"]),
                        "importe_gastado": parseFloat(self.init_data["tarjeta_monedero"]["importe_gastado"]) * -1,
                        "codcomanda": self.data["codigo"],
                        "iva": iva,
                        "tipo_linea": "tarjetaMonederoNegativos"

                    })
                    pago_tarjeta_monedero = Mg2RefoundTarjetaMonederoSerializer().serialize(new_init_data)
                    self.data["children"]["lines"].append(pago_tarjeta_monedero)
                    
                    if "items_requested" in self.init_data:
                        new_init_data = self.init_data.copy()
                        new_init_data.update({
                            "cod_uso": str(self.init_data["tarjeta_monedero"]["cod_uso"]),
                        "importe_gastado": parseFloat(self.init_data["tarjeta_monedero"]["importe_gastado"]),
                        "codcomanda": self.data["codigo"],
                        "iva": iva,
                        "tipo_linea": "tarjetaMonederoPositivo"
                        })
                        pago_tarjeta_monedero = Mg2RefoundTarjetaMonederoSerializer().serialize(new_init_data)
                        self.data["children"]["lines"].append(pago_tarjeta_monedero)
                    else:
                        if not self.crear_movimiento_tarjeta_monedero():
                            return False

        return True

    def crear_comanda_gastosenvio(self):
        idtpv_comanda = self.crear_cabecera_comanda_gastosenvio()
        if not idtpv_comanda:
            return False
        self.crear_lineas_comanda_gastosenvio(idtpv_comanda)
        self.crear_pagos_comanda_gastosenvio(idtpv_comanda)

        return True

    def crear_cabecera_comanda_gastosenvio(self):
        cif = self.init_data["cif"][:20] if self.init_data["cif"] and self.init_data["cif"] != "" else ""
        if not cif or cif == "":
            cif = "-"

        nombreCliente = str(self.init_data["pickup_address"]["firstname"])

        direccion = self.init_data["pickup_address"]["street"]
        dirNum = self.init_data["pickup_address"]["number"]
        if str(dirNum) == "None":
            dirNum = ""

        codpostal = str(self.init_data["pickup_address"]["postcode"])
        codComandaDevol = "WEB" + str(self.init_data["increment_id"])
        city = self.init_data["pickup_address"]["city"]
        codpais = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codpais", "codigo = '" + str(codComandaDevol) + "'")
        telefonofac = self.init_data["phone"]
        if "phone" in self.init_data["pickup_address"]:
            telefonofac = self.init_data["pickup_address"]["phone"]
        codpago = self.get_codpago(str(self.init_data["payment_method"]))
        email = self.init_data["email"]
        region = self.init_data["pickup_address"]["region"]
        codDivisa = str(self.init_data["currency"])

        iva = parseFloat(self.init_data["gastos_envio"]["iva"])
        totalVenta = parseFloat(self.init_data["gastos_envio"]["importe_gastosenvio"])
        totalNeto = round(parseFloat(totalVenta / ((100 + iva) / 100)), 2)
        totalIva = parseFloat(totalVenta - totalNeto)

        curComanda = qsatype.FLSqlCursor("tpv_comandas")
        curComanda.setModeAccess(curComanda.Insert)
        curComanda.setActivatedCommitActions(False)
        curComanda.refreshBuffer()
        curComanda.setValueBuffer("codigo", "WGE" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 9))
        curComanda.setValueBuffer("email", "")
        curComanda.setValueBuffer("codserie", self.get_codserie(codpais, self.init_data["pickup_address"]["postcode"]))
        curComanda.setValueBuffer("codejercicio", self.get_codejercicio(str(qsatype.Date())))
        curComanda.setValueBuffer("codcomandadevol", "")
        curComanda.setValueBuffer("codtpv_puntoventa", self.get_puntoventa())
        curComanda.setValueBuffer("codtpv_agente", "0350")
        curComanda.setValueBuffer("codalmacen", "AWEB")
        curComanda.setValueBuffer("codtienda", self.get_codtienda())
        curComanda.setValueBuffer("fecha", str(qsatype.Date())[:10])
        curComanda.setValueBuffer("hora", self.get_hora(str(qsatype.Date())))
        curComanda.setValueBuffer("nombrecliente", nombreCliente[:100] if nombreCliente else nombreCliente)
        curComanda.setValueBuffer("cifnif", cif)
        curComanda.setValueBuffer("dirtipovia", "")
        curComanda.setValueBuffer("direccion", direccion[:100] if direccion else direccion)
        curComanda.setValueBuffer("dirnum", dirNum[:100] if dirNum else dirNum)
        curComanda.setValueBuffer("dirotros", "")
        curComanda.setValueBuffer("codpostal", codpostal[:10] if codpostal else codpostal)
        curComanda.setValueBuffer("ciudad", city[:100] if city else city)
        curComanda.setValueBuffer("provincia", region[:100] if region else region)
        curComanda.setValueBuffer("telefono1", telefonofac[:30] if telefonofac else telefonofac)
        curComanda.setValueBuffer("codpais", codpais)
        curComanda.setValueBuffer("codpago", codpago[:10] if codpago else codpago)
        curComanda.setValueBuffer("coddivisa", codDivisa)
        curComanda.setValueBuffer("tasaconv", 1)
        curComanda.setValueBuffer("email", email[:100] if email else email)
        curComanda.setValueBuffer("neto", totalNeto)
        curComanda.setValueBuffer("totaliva", totalIva)
        curComanda.setValueBuffer("total", totalVenta)
        curComanda.setValueBuffer("codtarjetapuntos", self.get_codtarjetapuntos())
        curComanda.setValueBuffer("ptesincrofactura", False)
        curComanda.setValueBuffer("egcodfactura", "")
        curComanda.setValueBuffer("tipodoc", "VENTA")
        curComanda.setValueBuffer("estado", "Cerrada")
        curComanda.setValueBuffer("pagado", totalVenta)
        curComanda.setValueBuffer("egcodfactura", self.get_codfactura())
        curComanda.setValueBuffer("ptesincrofactura", True)
        if not curComanda.commitBuffer():
            return False

        return curComanda.valueBuffer("idtpv_comanda")

    def crear_lineas_comanda_gastosenvio(self, idtpv_comanda):
        iva = parseFloat(self.init_data["gastos_envio"]["iva"])

        codigo = "WGE" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 9)
        curLineasComanda = qsatype.FLSqlCursor("tpv_lineascomanda")
        curLineasComanda.setModeAccess(curLineasComanda.Insert)
        curLineasComanda.setActivatedCommitActions(False)
        curLineasComanda.refreshBuffer()
        curLineasComanda.setValueBuffer("codtienda", "AWEB")
        curLineasComanda.setValueBuffer("referencia", "0000ATEMP00001")
        curLineasComanda.setValueBuffer("descripcion", "MANIPULACIÓN Y ENVIO" + " WDV2" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 8))
        curLineasComanda.setValueBuffer("barcode", "8433613403654")
        curLineasComanda.setValueBuffer("codimpuesto", "GEN")
        curLineasComanda.setValueBuffer("codcomanda", codigo)

        iva = parseFloat(self.init_data["gastos_envio"]["iva"])
        totalVenta = parseFloat(self.init_data["gastos_envio"]["importe_gastosenvio"])
        totalNeto = round(parseFloat(totalVenta / ((100 + iva) / 100)), 2)

        curLineasComanda.setValueBuffer("cantidad", 1)
        curLineasComanda.setValueBuffer("cantdevuelta", 0)
        curLineasComanda.setValueBuffer("pvpunitario", totalNeto)
        curLineasComanda.setValueBuffer("pvpsindto", totalNeto)
        curLineasComanda.setValueBuffer("pvptotal", totalNeto)
        curLineasComanda.setValueBuffer("pvpunitarioiva", totalVenta)
        curLineasComanda.setValueBuffer("pvpsindtoiva", totalVenta)
        curLineasComanda.setValueBuffer("pvptotaliva", totalVenta)
        curLineasComanda.setValueBuffer("iva", iva)
        curLineasComanda.setValueBuffer("ivaincluido", True)
        curLineasComanda.setValueBuffer("idsincro", codigo + "_" + str(curLineasComanda.valueBuffer("idtpv_linea")))
        curLineasComanda.setValueBuffer("idtpv_comanda", idtpv_comanda)
        if not curLineasComanda.commitBuffer():
            return False

        return True


    def crear_pagos_comanda_gastosenvio(self, idtpv_comanda):
        
        iva = parseFloat(self.init_data["gastos_envio"]["iva"])
        idarqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = '{}' AND diadesde >= '{}' AND idasiento IS NULL ORDER BY diadesde ASC".format(self.get_codtienda(),str(qsatype.Date())[:10]))

        codigo = "WGE" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 9)
        curPagosComanda = qsatype.FLSqlCursor("tpv_pagoscomanda")
        curPagosComanda.setModeAccess(curPagosComanda.Insert)
        curPagosComanda.setActivatedCommitActions(False)
        curPagosComanda.refreshBuffer()
        curPagosComanda.setValueBuffer("anulado", False)
        curPagosComanda.setValueBuffer("ptepuntos", False)
        curPagosComanda.setValueBuffer("editable", True)
        curPagosComanda.setValueBuffer("nogenerarasiento", True)
        curPagosComanda.setValueBuffer("estado", "Pagado")
        curPagosComanda.setValueBuffer("codtienda", self.get_codtienda())
        curPagosComanda.setValueBuffer("codtpv_agente", "0350")
        curPagosComanda.setValueBuffer("codtpv_puntoventa", self.get_puntoventa())
        curPagosComanda.setValueBuffer("fecha", str(qsatype.Date())[:10])
        curPagosComanda.setValueBuffer("idtpv_arqueo", idarqueo)
        curPagosComanda.setValueBuffer("idtpv_comanda", idtpv_comanda)
        curPagosComanda.setValueBuffer("codcomanda", codigo)
        curPagosComanda.setValueBuffer("importe", parseFloat(self.init_data["gastos_envio"]["importe_gastosenvio"]))
        curPagosComanda.setValueBuffer("codpago", self.get_codpago(str(self.init_data["gastos_envio"]["metodo_pago"])))
        curPagosComanda.setValueBuffer("idsincro", codigo + "_" + str(curPagosComanda.valueBuffer("idpago")))
        if not curPagosComanda.commitBuffer():
            return False


        return True

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

    def crear_registro_puntos(self, codigo):

        if qsatype.FLUtil.quickSqlSelect("tpv_movpuntos", "operacion", "operacion = '{}'".format(codigo)):
            return True

        tasaconv = 1
        divisa = str(self.init_data["currency"])

        if divisa:
            if divisa != "None" and divisa == "CLP":
                tasaconv = qsatype.FLUtil.quickSqlSelect("divisas", "tasaconv", "coddivisa = '{}'".format(divisa))
                if not tasaconv:
                    tasaconv = 1

        if "points_used" in self.init_data:
            if parseFloat(self.init_data["points_used"]) != 0:
                curMP = qsatype.FLSqlCursor("tpv_movpuntos")
                curMP.setModeAccess(curMP.Insert)
                # curMP.setActivatedCommitActions(False)
                curMP.refreshBuffer()
                curMP.setValueBuffer("codtarjetapuntos", str(self.get_codtarjetapuntos()))
                curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
                curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                curMP.setValueBuffer("horamod", self.get_hora(str(qsatype.Date())))
                curMP.setValueBuffer("canpuntos", parseFloat(self.init_data["points_used"]) * tasaconv)
                curMP.setValueBuffer("operacion", codigo)
                curMP.setValueBuffer("sincronizado", False)
                curMP.setValueBuffer("codtienda", "AWEB")

                if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                    return False

                if not curMP.commitBuffer():
                    return False

        if "points_earn" in self.init_data:
            if parseFloat(self.init_data["points_earn"]) != 0:
                curMP = qsatype.FLSqlCursor("tpv_movpuntos")
                curMP.setModeAccess(curMP.Insert)
                # curMP.setActivatedCommitActions(False)
                curMP.refreshBuffer()
                curMP.setValueBuffer("codtarjetapuntos", str(self.get_codtarjetapuntos()))
                curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
                curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                curMP.setValueBuffer("horamod", self.get_hora(str(qsatype.Date())))
                curMP.setValueBuffer("canpuntos", parseFloat(self.init_data["points_earn"]) * (-1))
                curMP.setValueBuffer("operacion", codigo)
                curMP.setValueBuffer("sincronizado", False)
                curMP.setValueBuffer("codtienda", "AWEB")

                if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                    return False

                if not curMP.commitBuffer():
                    return False

        if "items_requested" in self.init_data:
            if "points_used" in self.init_data:
                if parseFloat(self.init_data["points_used"]) != 0:
                    curMP = qsatype.FLSqlCursor("tpv_movpuntos")
                    curMP.setModeAccess(curMP.Insert)
                    # curMP.setActivatedCommitActions(False)
                    curMP.refreshBuffer()
                    curMP.setValueBuffer("codtarjetapuntos", str(self.get_codtarjetapuntos()))
                    curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
                    curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                    curMP.setValueBuffer("horamod", self.get_hora(str(qsatype.Date())))
                    curMP.setValueBuffer("canpuntos", parseFloat(self.init_data["points_used"]) * (-1))
                    curMP.setValueBuffer("operacion", codigo)
                    curMP.setValueBuffer("sincronizado", False)
                    curMP.setValueBuffer("codtienda", "AWEB")

                    if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                        return False

                    if not curMP.commitBuffer():
                        return False

            if "points_earn" in self.init_data:
                if parseFloat(self.init_data["points_earn"]) != 0:
                    curMP = qsatype.FLSqlCursor("tpv_movpuntos")
                    curMP.setModeAccess(curMP.Insert)
                    # curMP.setActivatedCommitActions(False)
                    curMP.refreshBuffer()
                    curMP.setValueBuffer("codtarjetapuntos", str(self.get_codtarjetapuntos()))
                    curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
                    curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
                    curMP.setValueBuffer("horamod", self.get_hora(str(qsatype.Date())))
                    curMP.setValueBuffer("canpuntos", parseFloat(self.init_data["points_earn"])  * tasaconv)
                    curMP.setValueBuffer("operacion", codigo)
                    curMP.setValueBuffer("sincronizado", False)
                    curMP.setValueBuffer("codtienda", "AWEB")

                    if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                        return False

                    if not curMP.commitBuffer():
                        return False
