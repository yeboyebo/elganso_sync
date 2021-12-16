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


class Mg2RefoundsSerializer(DefaultSerializer):

    def get_data(self):
        qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 1")
        if not self.control_tallas_devolucion():
            return False
        qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 2")

        codigo = "WDV2" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(self.init_data["rma_id"]), 8)
        qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 3")

        now = str(qsatype.Date())
        self.start_date = now[:10]
        self.start_time = now[-(8):]

        if self.init_data["status"] != "Complete" or "items_requested" in self.init_data:
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 1")

            idComanda = qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
            if idComanda:
                return False
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 5")

            self.crear_cabecera_comanda_devolucionweb(codigo)
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 6")

            if "lines" not in self.data["children"]:
                self.data["children"]["lines"] = []
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 7")

            if "payments" not in self.data["children"]:
                self.data["children"]["payments"] = []
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 8")

            if "items_refunded" not in self.init_data:
                raise NameError("Error. No viene el nodo items_refunded en el JSON")
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 9")

            iva = 0
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 10")

            for line in self.init_data["items_refunded"]:
                line.update({
                    "codcomanda": codigo,
                    "tipo_linea": "refounded"
                })

                line_data = Mg2RefoundLineSerializer().serialize(line)
                self.data["children"]["lines"].append(line_data)
                iva = line["tax_percent"]

            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 11")
            if "items_requested" in self.init_data:
                for linea in self.init_data["items_requested"]:
                    linea.update({
                        "codcomanda": codigo,
                        "tipo_linea": "requested"
                    })
                    line_data = Mg2RefoundLineSerializer().serialize(linea)
                    self.data["children"]["lines"].append(line_data)
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 12")

            self.crear_registros_descuentos(iva)
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 13")
            self.crear_registros_puntos(iva)
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 14")
            self.crear_registros_vales(iva)
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 15")
            self.crear_registros_gastosenvio(iva)
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 16")

            self.data["children"]["cashcount"] = False
            qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ 17")
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
        qsatype.debug(u"+++++++++++++++++++++++++++++++++++++++ OK")

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
        region = self.init_data["pickup_address"]["region"]
        codDivisa = str(self.init_data["currency"])

        totalIva = parseFloat(self.init_data["tax_refunded"])
        # totalVenta = parseFloat(self.init_data["subtotal_refunded"]) - parseFloat(self.init_data["discount_refunded"]) - parseFloat(self.init_data["vale_total"]) + parseFloat(self.init_data["shipping_price"])
        totalVenta = parseFloat(self.init_data["total_refunded"])
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

    def crear_registros_vales(self, iva):

        new_init_data = self.init_data.copy()
        new_init_data.update({
            "codcomanda": self.data["codigo"],
            "iva": iva,
            "tipo_linea": "ValesPositivos"
        })
        linea_vale = Mg2RefoundVoucherLineSerializer().serialize(new_init_data)
        self.data["children"]["lines"].append(linea_vale)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update({
                "codcomanda": self.data["codigo"],
                "iva": iva,
                "tipo_linea": "ValesNegativos"
            })
            linea_vale = Mg2RefoundVoucherLineSerializer().serialize(new_init_data)
            self.data["children"]["lines"].append(linea_vale)

    def cerrar_devolucionweb(self, codigo):

        idComandaPago = qsatype.FLUtil.sqlSelect("tpv_comandas c INNER JOIN tpv_pagoscomanda p ON c.idtpv_comanda = p.idtpv_comanda", "p.idtpv_comanda", "c.codigo = '" + str(codigo) + "'")
        if idComandaPago:
            raise NameError("La devolucion ya tiene un pago creado.")
            return False

        self.data.update({
            "fecha": qsatype.Date()
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

        pago_web = Mg2RefoundPaymentSerializer().serialize(new_init_data)
        self.data["children"]["payments"].append(pago_web)

        if "items_requested" in self.init_data:
            new_init_data = self.init_data.copy()
            new_init_data.update(
                {"idarqueo": arqueo_web["idtpv_arqueo"],
                "tipo_pago": "Positivo",
                "codcomanda": codigo
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
        curMotivos.setValueBuffer("pvpunitarioiva", parseFloat(linea["original_price"]))
        curMotivos.setValueBuffer("idsincro", str(codigo) + "_" + str(curMotivos.valueBuffer("id")))
        curMotivos.setValueBuffer("motivos", str(linea["reason"]))
        curMotivos.setValueBuffer("sincronizada", True)
        if not curMotivos.commitBuffer():
            return False

        return True

    def crear_registros_ecommerce(self):
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

    def crear_viaje_recogidatienda(self, codcomanda):

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

        nombre_destino = str(qsatype.FLUtil.quickSqlSelect("almacenes", "nombre", "codalmacen = '" + str(self.init_data["warehouse"]) + "'"))
        curViaje = qsatype.FLSqlCursor("tpv_viajesmultitransstock")
        curViaje.setModeAccess(curViaje.Insert)
        curViaje.refreshBuffer()
        curViaje.setValueBuffer("idviajemultitrans", id_viaje)
        curViaje.setValueBuffer("fecha", qsatype.Date())
        curViaje.setValueBuffer("codalmaorigen", "AWEB")
        curViaje.setValueBuffer("nombreorigen", "WEB")
        curViaje.setValueBuffer("codalmadestino", str(self.init_data["warehouse"]))
        curViaje.setValueBuffer("nombredestino", nombre_destino)
        curViaje.setValueBuffer("cantidad", cantidad_viaje)
        curViaje.setValueBuffer("estado", "EN TRANSITO")
        curViaje.setValueBuffer("enviocompletado", True)
        curViaje.setValueBuffer("ptesincroenvio", True)
        curViaje.setValueBuffer("recepcioncompletada", False)
        curViaje.setValueBuffer("azkarok", False)
        curViaje.setValueBuffer("egnumseguimiento", codcomanda)

        if not curViaje.commitBuffer():
            raise NameError("Error al guardar la cabecera del viaje.")
            return False

        num_linea = 1
        for linea in self.init_data["items_refunded"]:
            if not self.crear_lineas_viaje_recogidatienda(id_viaje, linea, num_linea):
                raise NameError("Error al crear las líneas del viaje.")
                return False
            num_linea += 1


        if not qsatype.FLUtil.execSql("INSERT INTO eg_viajestiendaemail (idviajemultitrans, email, correoenviado) VALUES ('" + str(id_viaje) + "', '" + str(self.init_data["warehouse_email"]) + "', false)"):
            raise NameError("Error al insertar el registro en eg_viajestiendaemail.")
            return False

        return True

    def crear_lineas_viaje_recogidatienda(self, id_viaje, linea, num_linea):

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
        curLV.setValueBuffer("codalmadestino", str(self.init_data["warehouse"]))
        curLV.setValueBuffer("estado", "EN TRANSITO")
        curLV.setValueBuffer("cantidad", parseFloat(linea["qty"]))
        curLV.setValueBuffer("numlinea", num_linea)
        curLV.setValueBuffer("cantpteenvio", 0)
        curLV.setValueBuffer("cantenviada", parseFloat(linea["qty"]))
        curLV.setValueBuffer("cantpterecibir", parseFloat(linea["qty"]))
        curLV.setValueBuffer("cantrecibida", 0)
        curLV.setValueBuffer("excentral", "OK")
        curLV.setValueBuffer("extienda", "OK")
        curLV.setValueBuffer("rxcentral", "PTE")
        curLV.setValueBuffer("rxtienda", "PTE")
        curLV.setValueBuffer("ptestockcentral", False)
        curLV.setValueBuffer("cerradorx", False)
        curLV.setValueBuffer("cerradoex", False)
        curLV.setValueBuffer("revisada", False)
        curLV.setValueBuffer("ptestockrx", True)
        curLV.setValueBuffer("fechaex", str(qsatype.Date())[:10])
        curLV.setValueBuffer("horaex", self.get_hora(str(qsatype.Date())))
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
