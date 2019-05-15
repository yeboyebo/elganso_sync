# @class_declaration interna #
import requests
import json
from django.db import transaction
from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from models.flsyncppal import flsyncppal_def as syncppal


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
class elganso_sync(interna):

    @transaction.atomic
    def elganso_sync_getUnsynchronizedDevWeb(self):
        _i = self.iface

        cdSmall = 10
        cdLarge = 180

        headers = None
        if qsatype.FLUtil.isInProd():
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic c2luY3JvOmJVcWZxQk1ub0g="
            }
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic dGVzdDp0ZXN0"
            }

        try:
            url = None
            if qsatype.FLUtil.isInProd():
                url = 'https://www.elganso.com/syncapi/index.php/refounds/ready'
            else:
                url = 'http://local2.elganso.com/syncapi/index.php/refounds/ready'

            print("Llamando a", url)
            response = requests.get(url, headers=headers)
            stCode = response.status_code
            json = None
            if response and stCode == 200:
                json = response.json()
            else:
                raise Exception("Mala respuesta")

        except Exception as e:
            print(e)
            syncppal.iface.log("Error. No se pudo establecer la conexión con el servidor.", "mgsyncdevweb")
            return cdLarge

        if json and len(json):
            try:
                aOrders = _i.processOrdersDevWeb(json)

                if not aOrders and not isinstance(aOrders, (list, tuple, dict)):
                    syncppal.iface.log("Error. Ocurrió un error al sincronizar las devoluciones web.", "mgsyncdevweb")
                    raise Exception
            except Exception as e:
                print(e)
                return cdSmall

            if aOrders and len(aOrders.keys()):
                strCods = ""
                for k in aOrders.keys():
                    strCods += k if strCods == "" else ", " + k
                syncppal.iface.log(ustr("Éxito. Las siguientes devoluciones web se han sincronizado correctamente: ", str(strCods)), "mgsyncdevweb")
                for order in aOrders.keys():
                    try:
                        url = None
                        if qsatype.FLUtil.isInProd():
                            url = 'https://www.elganso.com/syncapi/index.php/refounds/' + str(aOrders[order]) + '/synchronized'
                        else:
                            url = 'http://local2.elganso.com/syncapi/index.php/refounds/' + str(aOrders[order]) + '/synchronized'

                        print("Llamando a", url)
                        response = requests.put(url, headers=headers)
                        print("Correcto")
                    except Exception:
                        syncppal.iface.log(ustr("Error. La devolución web ", str(order), " no ha podido marcarse como sincronizada."), "mgsyncdevweb")
            elif aOrders == {}:
                syncppal.iface.log("Éxito. No hay devoluciones web que sincronizar.", "mgsyncdevweb")
                return cdLarge
        else:
            syncppal.iface.log("Éxito. No hay devoluciones web que sincronizar.", "mgsyncdevweb")
            return cdLarge

        return cdSmall

    def elganso_sync_processOrdersDevWeb(self, orders):
        _i = self.iface

        aOrders = {}
        saltar = {}

        for order in orders:
            if order["refound_id"] in saltar:
                continue

            if not _i.controlTallasDevolucion(order):
                continue

            codigo = "WDV" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(order["refound_id"]), 9)

            if qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + codigo + "'"):
                saltar[order["refound_id"]] = order["refound_id"]
                aOrders[codigo] = order["refound_id"]
                continue

            curComanda = _i.creaCabeceraComandaDevWeb(order, codigo)
            if not curComanda:
                return False

            for linea in order["items_refunded"]:
                if not _i.creaLineaComandaDevWeb(linea, curComanda, order["refound_id"], "refounded"):
                    return False

            if "items_requested" in order:
                for linea in order["items_requested"]:
                    if not _i.creaLineaComandaDevWeb(linea, curComanda, order["refound_id"], "requested"):
                        return False

            if str(order["cupon_bono"]) != "None":
                for linea in order["items_refunded"]:
                    if not _i.controlMovBono(linea, order, curComanda):
                        return False
            elif str(order["points_used"]) != "None":
                for linea in order["items_refunded"]:
                    if not _i.controlMovPuntos(linea, order, curComanda):
                        return False

            if str(order["vale_description"]) != "None":
                for linea in order["items_refunded"]:
                    if not _i.controlMovVale(linea, order, curComanda):
                        return False

            idComanda = curComanda.valueBuffer("idtpv_comanda")
            curComanda.select("idtpv_comanda = " + str(idComanda))
            if not curComanda.first():
                syncppal.iface.log(ustr("Error. No se pudo recuperar la venta guardada para ", str(idCOmanda)), "mgsyncdevweb")
                return False

            curComanda.setModeAccess(curComanda.Edit)
            curComanda.refreshBuffer()
            qsatype.FactoriaModulos.get('formRecordtpv_comandas').iface.calcularTotalesCursor(curComanda)
            if not curComanda.commitBuffer():
                return False

            if not _i.cerrarVentaWeb(curComanda, order):
                syncppal.iface.log(ustr("Error. No se pudo cerrar la devolución web ", str(codigo)), "mgsyncdevweb")
                return False

            for linea in order["items_refunded"]:
                if not _i.actualizarCantDevueltaOrder(linea, curComanda, order):
                    return False

            for linea in order["items_refunded"]:
                if not _i.creaMotivosDevolucion(linea, curComanda, order):
                    return False

            for linea in order["items_refunded"]:
                if not _i.creaRegistroEcommerce(linea, curComanda, order):
                    return False

            codigo = "WDV" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(order["refound_id"]), 9)
            aOrders[codigo] = order["refound_id"]

        return aOrders

    def elganso_sync_creaCabeceraComandaDevWeb(self, order, codigo):
        _i = self.iface

        try:
            curComanda = qsatype.FLSqlCursor("tpv_comandas")
            curComanda.setActivatedCommitActions(False)
            curComanda.setModeAccess(curComanda.Insert)
            curComanda.refreshBuffer()

            curComanda.setValueBuffer("codigo", codigo[:15])

            cif = order["cif"][:20] if order["cif"] and order["cif"] != "" else ""
            if not cif or cif == "":
                cif = "-"
            nombreCliente = str(order["pickup_address"]["firstname"]) + " " + str(order["pickup_address"]["lastname"])

            street = order["pickup_address"]["street"].split("\n")
            dirTipoVia = street[0] if len(street) >= 1 else ""
            direccion = street[1] if len(street) >= 2 else ""
            dirNum = street[2] if len(street) >= 3 else ""
            dirOtros = street[3] if len(street) >= 4 else ""

            codpostal = str(order["pickup_address"]["postcode"])
            codComandaDevol = "WEB" + str(order["increment_id"])
            print("///////////////////codComandaDevol: ", codComandaDevol)
            city = order["pickup_address"]["city"]
            codpais = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "codpais", "codigo = '" + str(codComandaDevol) + "'")
            telefonofac = order["phone"]
            codpago = _i.obtenerCodPago(str(order["payment_method"]))
            email = order["email"]
            codtarjetapuntos = order["card_points"]
            region = order["pickup_address"]["region"]
            codDivisa = str(order["currency"])

            totalNeto = parseFloat(order["subtotal_refunded"]) - (parseFloat(order["discount_refunded"]))
            totalIva = parseFloat(order["tax_refunded"])
            totalVenta = parseFloat(order["total_refunded"])

            curComanda.setValueBuffer("codserie", _i.obtenerCodSerie(codpais, order["pickup_address"]["postcode"]))
            curComanda.setValueBuffer("codejercicio", _i.obtenerEjercicio(str(qsatype.Date())))
            curComanda.setValueBuffer("codcomandadevol", str(codComandaDevol))
            curComanda.setValueBuffer("codtpv_puntoventa", "AWEB")
            curComanda.setValueBuffer("codtpv_agente", "0350")
            curComanda.setValueBuffer("codalmacen", "AWEB")
            curComanda.setValueBuffer("codtienda", "AWEB")
            curComanda.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curComanda.setValueBuffer("hora", _i.obtenerHora(str(qsatype.Date())))
            curComanda.setValueBuffer("nombrecliente", nombreCliente[:100] if nombreCliente else nombreCliente)
            curComanda.setValueBuffer("cifnif", cif)
            curComanda.setValueBuffer("dirtipovia", dirTipoVia[:100] if dirTipoVia else dirTipoVia)
            curComanda.setValueBuffer("direccion", direccion[:100] if direccion else direccion)
            curComanda.setValueBuffer("dirnum", dirNum[:100] if dirNum else dirNum)
            curComanda.setValueBuffer("dirotros", dirOtros[:100] if dirOtros else dirOtros)
            curComanda.setValueBuffer("codpostal", codpostal[:10] if codpostal else codpostal)
            curComanda.setValueBuffer("ciudad", city[:100] if city else city)
            curComanda.setValueBuffer("provincia", region[:100] if region else region)
            curComanda.setValueBuffer("telefono1", telefonofac[:30] if telefonofac else telefonofac)
            curComanda.setValueBuffer("codpais", codpais)
            curComanda.setValueBuffer("codpago", codpago[:10] if codpago else codpago)
            curComanda.setValueBuffer("coddivisa", codDivisa)
            curComanda.setValueBuffer("tasaconv", 1)
            curComanda.setValueBuffer("email", email[:100] if email else email)
            curComanda.setValueBuffer("neto", totalNeto * (-1))
            curComanda.setValueBuffer("totaliva", totalIva * (-1))
            curComanda.setValueBuffer("total", totalVenta * (-1))
            curComanda.setValueBuffer("codtarjetapuntos", codtarjetapuntos[:15] if codtarjetapuntos else codtarjetapuntos)
            curComanda.setValueBuffer("ptesincrofactura", False)
            curComanda.setValueBuffer("egcodfactura", "")

            if not curComanda.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar la cabecera de la venta ", str(codigo)), "mgsyncdevweb")
                return False

            curComanda.select("codigo = '" + str(codigo) + "'")
            if not curComanda.first():
                syncppal.iface.log(ustr("Error. No se pudo recuperar la cabecera guardada para ", str(codigo)), "mgsyncdevweb")
                return False

            curComanda.setModeAccess(curComanda.Edit)
            curComanda.refreshBuffer()

            return curComanda

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_obtenerCodSerie(self, nomPais, codPostal):
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

    def elganso_sync_obtenerEjercicio(self, fecha):
        fecha = fecha[:10]
        datosFecha = fecha.split("-")

        return datosFecha[0]

    def elganso_sync_obtenerHora(self, fecha):
        h = fecha[-(8):]
        h = "23:59:59" if h == "00:00:00" else h

        return h

    def elganso_sync_obtenerCodPais(self, paisfc):
        if not paisfc or paisfc == "":
            return ""

        codPais = qsatype.FLUtil.quickSqlSelect("paises", "codpais", "UPPER(codpais) = '" + paisfc.upper() + "'")
        if not codPais or codPais == "":
            return ""

        return codPais

    def elganso_sync_obtenerCodPago(self, metPago):
        codPago = qsatype.FLUtil.quickSqlSelect("mg_formaspago", "codpago", "mg_metodopago = '" + metPago + "'")
        if not codPago:
            codPago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")

        return codPago

    def elganso_sync_conFac(self, fac):
        if not fac or fac == "":
            return False
        return True

    def elganso_sync_obtenerColor(self, sku):
        arrSku = sku.split("-")
        if len(arrSku) == 1:
            ref = arrSku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '" + ref + "'")
        elif len(arrSku) == 2:
            ref = arrSku[0]
            talla = arrSku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "color", "referencia = '" + ref + "' AND talla = '" + talla + "'")
        else:
            return "U"

    def elganso_sync_obtenerTalla(self, sku):
        arrSku = sku.split("-")
        if len(arrSku) == 1:
            ref = arrSku[0]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "talla", "referencia = '" + ref + "'")
        elif len(arrSku) == 2:
            return arrSku[1]
        else:
            return "TU"

    def elganso_sync_obtenerReferencia(self, sku):
        return sku.split('-')[0]

    def elganso_sync_obtenerNumLineaComanda(self, codigo):
        if not str(codigo).startswith(u"WDV"):
            codigo = "WDV" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(codigo), 9)
        print("codigo: ", codigo)
        idComanda = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
        if not idComanda:
            return 1
        print("idComanda ", idComanda)
        numL = parseInt(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "count(*)", "idtpv_comanda = " + str(idComanda)))
        if isNaN(numL):
            numL = 0
        return numL + 1

    def elganso_sync_obtenerDescripcion(self, sku):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '" + sku.split('-')[0] + "'")

    def elganso_sync_obtenerBarcode(self, sku):
        arrSku = sku.split("-")
        if len(arrSku) == 1:
            ref = arrSku[0].upper()
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '" + ref + "'")
        elif len(arrSku) == 2:
            ref = arrSku[0].upper()
            talla = arrSku[1]
            return qsatype.FLUtil.quickSqlSelect("atributosarticulos", "barcode", "UPPER(referencia) = '" + ref + "' AND talla = '" + talla + "'")
        else:
            return "ERRORNOTALLA"

    def elganso_sync_obtenerCodImpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def elganso_sync_cerrarVentaWeb(self, curComanda, order):
        _i = self.iface
        print("ENTRA EN cerrarVentaWeb")
        try:
            idComanda = curComanda.valueBuffer("idtpv_comanda")

            codArqueo = _i.crearArqueoVentaWeb(curComanda)
            if not codArqueo:
                syncppal.iface.log(ustr("Error. No se pudo crear el arqueo"), "mgsyncdevweb")
                return False

            if not _i.crearPagosDevWeb(curComanda, codArqueo, order):
                syncppal.iface.log(ustr("Error. No se pudo crear el pago para el arqueo ", str(codArqueo)), "mgsyncdevweb")
                return False

            if not qsatype.FLSqlQuery().execSql(u"UPDATE tpv_comandas SET estado = 'Cerrada', editable = true, pagado = total, tipodoc = CASE WHEN total >= 0 THEN 'VENTA' ELSE 'DEVOLUCION' END WHERE idtpv_comanda = " + str(idComanda)):
                syncppal.iface.log(ustr("Error. No se pudo cerrar la venta ", str(idComanda)), "mgsyncdevweb")
                return False

            """if parseFloat(curComanda.valueBuffer("total")) != 0:
                egcodfactura = _i.obtenerCodFactura()
                if not qsatype.FLSqlQuery().execSql(u"UPDATE tpv_comandas SET egcodfactura = '" + str(egcodfactura) + "' WHERE idtpv_comanda = " + str(idComanda)):
                    syncppal.iface.log(ustr("Error al calcular el código de la factura. ", str(idComanda)), "mgsyncdevweb")
                    return False"""

            d = qsatype.Date()
            if not qsatype.FactoriaModulos.get('formtpv_tiendas').iface.marcaFechaSincroTienda("AWEB", "VENTAS_TPV", d):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearArqueoVentaWeb(self, curComanda):
        _i = self.iface

        try:
            codTienda = "AWEB"
            fecha = curComanda.valueBuffer("fecha")

            # Buscamos el primer arqueo a partir de la fecha de la venta sin asiento generado
            idArqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = '" + codTienda + "' AND diadesde >= '" + str(fecha) + "' AND idasiento IS NULL order by diadesde asc")

            if idArqueo:
                return idArqueo

            # Si no lo hemos encontrado buscamos un arqueo para las fechas de hoy con asientos
            fecha = qsatype.Date()
            idArqueo = qsatype.FLUtil.sqlSelect("tpv_arqueos", "idtpv_arqueo", "codtienda = '" + codTienda + "' AND diadesde = '" + str(fecha) + "'")

            # si lo hay devolvemos falso porque significa que ya existe y tiene asiento
            if idArqueo:
                return False

            # si no lo encontramos lo creamos con fecha de hoy
            codTpvPuntoVenta = qsatype.FLUtil.sqlSelect("tpv_puntosventa", "codtpv_puntoventa", "codtienda = '" + codTienda + "'")

            curArqueo = qsatype.FLSqlCursor("tpv_arqueos")
            curArqueo.setActivatedCommitActions(False)
            curArqueo.setActivatedCheckIntegrity(False)
            curArqueo.setModeAccess(curArqueo.Insert)
            curArqueo.refreshBuffer()

            curArqueo.setValueBuffer("abierta", True)
            curArqueo.setValueBuffer("sincronizado", False)
            curArqueo.setValueBuffer("idfactura", 0)
            curArqueo.setValueBuffer("diadesde", fecha)
            curArqueo.setValueBuffer("horadesde", "00:00:01")
            curArqueo.setValueBuffer("ptoventa", codTpvPuntoVenta[:6] if codTpvPuntoVenta else codTpvPuntoVenta)
            curArqueo.setValueBuffer("codtpv_agenteapertura", "0350")
            curArqueo.setValueBuffer("codtienda", codTienda)

            if not _i.masDatosArqueo(curArqueo, curComanda):
                return False

            idArqueo = qsatype.FactoriaModulos.get("formRecordtpv_arqueos").iface.codigoArqueo(curArqueo)
            curArqueo.setValueBuffer("idtpv_arqueo", idArqueo[:8] if idArqueo else idArqueo)

            if not curArqueo.commitBuffer():
                return False

            return idArqueo

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearPagosDevWeb(self, curComanda, idArqueo, order):
        _i = self.iface
        try:
            if not idArqueo or not curComanda:
                return False

            if not _i.crearPagoDevWeb(curComanda, idArqueo, order, "Negativo"):
                return False

            if "items_requested" in order:
                for linea in order["items_refunded"]:
                    if not _i.crearPagoDevWeb(curComanda, idArqueo, order, "Positivo"):
                        return False
            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_masDatosArqueo(self, curArqueo, curComanda):
        fecha = curArqueo.valueBuffer("diadesde")

        curArqueo.setValueBuffer("sincronizado", True)
        curArqueo.setValueBuffer("diahasta", fecha)
        curArqueo.setValueBuffer("horahasta", "23:59:59")

        return True

    def elganso_sync_obtenerCodFactura(self):
        try:
            prefijo = "AWDVX"
            ultimaFact = None

            idUltima = qsatype.FLUtil.sqlSelect("tpv_comandas", "egcodfactura", "egcodfactura LIKE '" + prefijo + "%' ORDER BY egcodfactura DESC")
            if idUltima:
                ultimaFact = parseInt(str(idUltima)[-(12 - len(prefijo)):])
            else:
                ultimaFact = 0
            ultimaFact = ultimaFact + 1

            return prefijo + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(ultimaFact), 12 - len(prefijo))

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaLineaComandaDevWeb(self, linea, curComanda, increment, tipoLinea):
        _i = self.iface
        try:
            curLinea = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLinea.setModeAccess(curLinea.Insert)
            curLinea.refreshBuffer()
            curLinea.setActivatedCommitActions(False)
            curLinea.setActivatedCheckIntegrity(False)
            codigo = curComanda.valueBuffer("codigo")
            nl = _i.obtenerNumLineaComanda(increment)
            iva = parseFloat(linea["tax_percent"])
            if not iva or iva == "":
                iva = 0

            desc = _i.obtenerDescripcion(linea["sku"])
            ref = _i.obtenerReferencia(linea["sku"])
            bc = _i.obtenerBarcode(linea["sku"])
            talla = _i.obtenerTalla(linea["sku"])
            color = _i.obtenerColor(linea["sku"])
            codiva = _i.obtenerCodImpuesto(iva)

            cant = parseFloat(linea["qty"])

            pvpUnitario = parseFloat(linea["price"])
            pvpSinDto = parseFloat(linea["price"]) * cant
            pvpTotal = parseFloat(linea["price"]) * cant
            pvpUnitarioIva = parseFloat(linea["original_price"])
            pvpSinDtoIva = parseFloat(linea["original_price"]) * cant
            pvpTotalIva = parseFloat(linea["original_price"]) * cant

            if tipoLinea == "refounded":
                pvpSinDto = pvpSinDto * (-1)
                pvpTotal = pvpTotal * (-1)
                pvpSinDtoIva = pvpSinDtoIva * (-1)
                pvpTotalIva = pvpTotalIva * (-1)
                cant = cant * (-1)

            curLinea.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curLinea.setValueBuffer("codtienda", "AWEB")
            curLinea.setValueBuffer("cantidad", cant)
            curLinea.setValueBuffer("cantdevuelta", 0)
            curLinea.setValueBuffer("pvpunitario", pvpUnitario)
            curLinea.setValueBuffer("pvpsindto", pvpSinDto)
            curLinea.setValueBuffer("pvptotal", pvpTotal)
            curLinea.setValueBuffer("pvpunitarioiva", pvpUnitarioIva)
            curLinea.setValueBuffer("pvpsindtoiva", pvpSinDtoIva)
            curLinea.setValueBuffer("pvptotaliva", pvpTotalIva)
            curLinea.setValueBuffer("iva", iva)
            curLinea.setValueBuffer("descripcion", desc[:100] if desc else desc)
            curLinea.setValueBuffer("referencia", ref[:18] if ref else ref)
            curLinea.setValueBuffer("barcode", bc[:20] if bc else bc)
            curLinea.setValueBuffer("numlinea", nl)
            curLinea.setValueBuffer("talla", talla[:50] if talla else talla)
            curLinea.setValueBuffer("color", color[:50] if color else color)
            curLinea.setValueBuffer("ivaincluido", True)
            curLinea.setValueBuffer("codimpuesto", codiva[:10] if codiva else codiva)
            curLinea.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)

            idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", curLinea)
            curLinea.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curLinea.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar la línea ", nl, " de la venta ", str(codigo)), "mgsyncdevweb")
                return False

            if not _i.crearRegistroMovistock(curLinea):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_controlTallasDevolucion(self, order):
        _i = self.iface

        refDevol = ""
        refCambio = False

        for linea in order["items_refunded"]:
            refDevol = _i.obtenerReferencia(linea["sku"])

        if "items_requested" in order:
            for linea in order["items_requested"]:
                refCambio = _i.obtenerReferencia(linea["sku"])

        if not refCambio:
            return True

        if refDevol != refCambio:
            syncppal.iface.log("Error. Solo se permite realizar cambios de tallas del mismo artículo", "mgsyncdevweb")
            return False

        return True

    def elganso_sync_crearPagoDevWeb(self, curComanda, idArqueo, order, tipoPago):
        _i = self.iface

        try:

            importe = parseFloat(qsatype.FLUtil.sqlSelect("tpv_lineascomanda", "SUM(pvptotaliva)", "idtpv_comanda = " + str(curComanda.valueBuffer("idtpv_comanda"))))

            if "items_requested" in order:
                importe = parseFloat(qsatype.FLUtil.sqlSelect("tpv_lineascomanda", "SUM(pvptotaliva)", "idtpv_comanda = " + str(curComanda.valueBuffer("idtpv_comanda")) + " AND pvptotaliva < 0 AND referencia <> '0000ATEMP00040'"))

            print("/////////////importe ", importe)
            codPago = _i.obtenerCodPago(str(order["payment_method"]))

            if tipoPago == "Positivo":
                importe = importe * (-1)

            curPago = qsatype.FLSqlCursor("tpv_pagoscomanda")
            curPago.setModeAccess(curPago.Insert)
            curPago.refreshBuffer()

            curPago.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curPago.setValueBuffer("codcomanda", curComanda.valueBuffer("codigo")[:12] if curComanda.valueBuffer("codigo") else curComanda.valueBuffer("codigo"))
            curPago.setValueBuffer("idtpv_arqueo", idArqueo[:8] if idArqueo else idArqueo)
            curPago.setValueBuffer("fecha", curComanda.valueBuffer("fecha"))
            curPago.setValueBuffer("editable", True)
            curPago.setValueBuffer("nogenerarasiento", True)
            curPago.setValueBuffer("anulado", False)
            curPago.setValueBuffer("importe", parseFloat(importe))
            curPago.setValueBuffer("estado", "Pagado")
            curPago.setValueBuffer("codpago", codPago)
            curPago.setValueBuffer("codtpv_puntoventa", str(curComanda.valueBuffer("codtpv_puntoventa"))[:6] if str(curComanda.valueBuffer("codtpv_puntoventa")) else str(curComanda.valueBuffer("codtpv_puntoventa")))
            curPago.setValueBuffer("codtpv_agente", "0350")
            curPago.setValueBuffer("codtienda", "AWEB")

            idsincro = qsatype.FactoriaModulos.get("formRecordtpv_pagoscomanda").iface.commonCalculateField("idsincro", curPago)
            curPago.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curPago.commitBuffer():
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_controlMovBono(self, linea, order, curComanda):
        _i = self.iface
        try:
            if not _i.insertarLineaBono(linea, order, curComanda, "BonoPositivo"):
                syncppal.iface.log("Error. No se ha podido crear la línea del bono", "mgsyncdevweb")
                return False

            if not _i.insertarMovBono(linea, order, curComanda, "BonoPositivo"):
                syncppal.iface.log("Error. No se ha podido crear el movimiento del bono", "mgsyncdevweb")
                return False

            if "items_requested" in order:
                if not _i.insertarLineaBono(linea, order, curComanda, "BonoNegativo"):
                    syncppal.iface.log("Error. No se ha podido crear la línea del bono", "mgsyncdevweb")
                    return False

                if not _i.insertarMovBono(linea, order, curComanda, "BonoNegativo"):
                    syncppal.iface.log("Error. No se ha podido crear el movimiento del bono", "mgsyncdevweb")
                    return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_insertarLineaBono(self, linea, order, curComanda, tipoMov):
        _i = self.iface
        try:

            curLinea = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLinea.setModeAccess(curLinea.Insert)
            curLinea.refreshBuffer()

            codigo = curComanda.valueBuffer("codigo")
            nl = _i.obtenerNumLineaComanda(codigo)
            iva = parseFloat(linea["tax_percent"])
            if not iva or iva == "":
                iva = 0

            sJson = qsatype.FLUtil.sqlSelect("tpv_parametrostienda", "valor", "param = 'GASTAR_BONOS'")

            if not sJson:
                return False
            oGastarBono = None
            try:
                oGastarBono = eval(ustr(u"(", sJson, u")"))
            except Exception as e:
                e = traceback.format_exc()
                sys.warnMsgBox(e)

            if not oGastarBono:
                return False

            codiva = _i.obtenerCodImpuesto(iva)

            pvpUnitario = parseFloat(linea["discount"]) / ((100 + iva) / 100)
            pvpSinDto = pvpUnitario
            pvpTotal = pvpSinDto
            pvpUnitarioIva = parseFloat(linea["discount"])
            pvpSinDtoIva = pvpUnitarioIva
            pvpTotalIva = pvpUnitarioIva

            if tipoMov == "BonoNegativo":
                pvpSinDto = pvpSinDto * (-1)
                pvpTotal = pvpTotal * (-1)
                pvpSinDtoIva = pvpUnitarioIva * (-1)
                pvpTotalIva = pvpUnitarioIva * (-1)

            curLinea.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curLinea.setValueBuffer("codtienda", "AWEB")
            curLinea.setValueBuffer("cantidad", 1)
            curLinea.setValueBuffer("cantdevuelta", 0)
            curLinea.setValueBuffer("pvpunitario", pvpUnitario)
            curLinea.setValueBuffer("pvpsindto", pvpSinDto)
            curLinea.setValueBuffer("pvptotal", pvpTotal)
            curLinea.setValueBuffer("pvpunitarioiva", pvpUnitarioIva)
            curLinea.setValueBuffer("pvpsindtoiva", pvpSinDtoIva)
            curLinea.setValueBuffer("pvptotaliva", pvpTotalIva)
            curLinea.setValueBuffer("iva", iva)
            curLinea.setValueBuffer("descripcion", "BONO " + order["cupon_bono"])
            curLinea.setValueBuffer("referencia", oGastarBono["referenciabono"])
            curLinea.setValueBuffer("barcode", oGastarBono["barcodebono"])
            curLinea.setValueBuffer("numlinea", nl)
            curLinea.setValueBuffer("ivaincluido", True)
            curLinea.setValueBuffer("codimpuesto", codiva[:10] if codiva else codiva)
            curLinea.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)

            idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", curLinea)
            curLinea.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curLinea.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar la línea ", nl, " de la venta ", str(codigo)), "mgsyncdevweb")
                return False
            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_insertarMovBono(self, linea, order, curComanda, tipoMov):
            try:
                importeMovBono = parseFloat(linea["discount"]) * (-1)

                if tipoMov == "BonoPositivo":
                    importeMovBono = parseFloat(linea["discount"])

                curMoviBono = qsatype.FLSqlCursor("eg_movibono")
                curMoviBono.setModeAccess(curMoviBono.Insert)
                curMoviBono.refreshBuffer()
                curMoviBono.setValueBuffer("codbono", str(order["cupon_bono"]))
                curMoviBono.setValueBuffer("fecha", str(qsatype.Date())[:10])
                curMoviBono.setValueBuffer("venta", curComanda.valueBuffer("codigo"))
                curMoviBono.setValueBuffer("importe", importeMovBono)
                if not curMoviBono.commitBuffer():
                    return False

                if not qsatype.FLUtil.execSql(ustr(u"UPDATE eg_bonos SET saldoconsumido = (-1) * (SELECT SUM(importe) FROM eg_movibono WHERE codbono = '", str(order["cupon_bono"]), "'), saldopendiente = saldoinicial + (SELECT SUM(importe) FROM eg_movibono WHERE codbono = '", str(order["cupon_bono"]), "') WHERE codbono = '", str(order["cupon_bono"]), "'")):
                    return False

                return True

            except Exception as e:
                qsatype.debug(e)
                return False

    def elganso_sync_controlMovPuntos(self, linea, order, curComanda):
        _i = self.iface

        try:
            print("/////////////////////////crearLineaDescuentoPuntos")
            if not _i.crearLineaDescuentoPuntos(linea, order, curComanda, "PuntosPositivos"):
                return False

            print("/////////////////////////crearRegistroMovPuntos")
            if not _i.crearRegistroMovPuntos(order, curComanda, "PuntosPositivos"):
                return False

            if "items_requested" in order:
                print("/////////////////////////crearLineaDescuentoPuntos1")
                if not _i.crearLineaDescuentoPuntos(linea, order, curComanda, "PuntosNegativos"):
                    return False

                print("/////////////////////////crearLineaDescuentoPuntos2")
                if not _i.crearRegistroMovPuntos(order, curComanda, "PuntosNegativos"):
                    return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearLineaDescuentoPuntos(self, linea, order, curComanda, tipoMov):
        _i = self.iface
        try:

            curLinea = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLinea.setModeAccess(curLinea.Insert)
            curLinea.refreshBuffer()

            codigo = curComanda.valueBuffer("codigo")
            nl = _i.obtenerNumLineaComanda(codigo)
            iva = parseFloat(linea["tax_percent"])
            if not iva or iva == "":
                iva = 0

            codiva = _i.obtenerCodImpuesto(iva)

            pvpUnitario = (parseFloat(order["discount_refunded"])) / ((100 + iva) / 100)
            pvpSinDto = pvpUnitario
            pvpTotal = pvpSinDto
            pvpUnitarioIva = (parseFloat(order["discount_refunded"]))
            pvpSinDtoIva = pvpUnitarioIva
            pvpTotalIva = pvpUnitarioIva

            if tipoMov == "PuntosNegativos":
                pvpSinDto = pvpSinDto * (-1)
                pvpTotal = pvpTotal * (-1)
                pvpSinDtoIva = pvpUnitarioIva * (-1)
                pvpTotalIva = pvpUnitarioIva * (-1)

            curLinea.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curLinea.setValueBuffer("codtienda", "AWEB")
            curLinea.setValueBuffer("cantidad", 1)
            curLinea.setValueBuffer("cantdevuelta", 0)
            curLinea.setValueBuffer("pvpunitario", pvpUnitario)
            curLinea.setValueBuffer("pvpsindto", pvpSinDto)
            curLinea.setValueBuffer("pvptotal", pvpTotal)
            curLinea.setValueBuffer("pvpunitarioiva", pvpUnitarioIva)
            curLinea.setValueBuffer("pvpsindtoiva", pvpSinDtoIva)
            curLinea.setValueBuffer("pvptotaliva", pvpTotalIva)
            curLinea.setValueBuffer("iva", iva)
            curLinea.setValueBuffer("descripcion", "DESCUENTO PAGO PUNTOS " + str(order["card_points"]))
            curLinea.setValueBuffer("referencia", "0000ATEMP00001")
            curLinea.setValueBuffer("barcode", "8433613403654")
            curLinea.setValueBuffer("numlinea", nl)
            curLinea.setValueBuffer("ivaincluido", True)
            curLinea.setValueBuffer("codimpuesto", codiva[:10] if codiva else codiva)
            curLinea.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)

            idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", curLinea)
            curLinea.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curLinea.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar la línea ", nl, " de la venta ", str(codigo)), "mgsyncdevweb")
                return False
            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearRegistroMovPuntos(self, order, curComanda, tipoMov):
        _i = self.iface
        try:

            canPuntos = parseFloat(order["discount_refunded"])
            if tipoMov == "PuntosNegativos":
                canPuntos = canPuntos * (-1)

            curMP = qsatype.FLSqlCursor("tpv_movpuntos")
            curMP.setModeAccess(curMP.Insert)
            curMP.setActivatedCommitActions(False)
            curMP.refreshBuffer()
            curMP.setValueBuffer("codtarjetapuntos", str(order["card_points"]))
            curMP.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curMP.setValueBuffer("fechamod", str(qsatype.Date())[:10])
            curMP.setValueBuffer("horamod", _i.obtenerHora(str(qsatype.Date())))
            curMP.setValueBuffer("canpuntos", canPuntos)
            curMP.setValueBuffer("operacion", curComanda.valueBuffer("codigo"))
            curMP.setValueBuffer("sincronizado", True)
            curMP.setValueBuffer("codtienda", "AWEB")

            if not qsatype.FactoriaModulos.get('flfact_tpv').iface.controlIdSincroMovPuntos(curMP):
                return False

            if not curMP.commitBuffer():
                print("FALSE MOVPUNTOS")
                return False

            if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_tarjetaspuntos SET saldopuntos = CASE WHEN (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) IS NULL THEN 0 ELSE (SELECT SUM(canpuntos) FROM tpv_movpuntos WHERE codtarjetapuntos = tpv_tarjetaspuntos.codtarjetapuntos) END WHERE codtarjetapuntos = '", str(order["card_points"]), "'")):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_controlMovVale(self, linea, order, curComanda):
        _i = self.iface
        try:
            print("///////////*****ENTRA EN controlMovVale")
            if not _i.crearLineaDescuentoVale(linea, order, curComanda, "ValesPositivos"):
                return False

            if not _i.crearRegistroMovVales(linea, order, curComanda, "ValesPositivos"):
                return False

            if "items_requested" in order:
                if not _i.crearLineaDescuentoVale(linea, order, curComanda, "ValesNegativos"):
                    return False

                if not _i.crearRegistroMovVales(linea, order, curComanda, "ValesNegativos"):
                    return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearLineaDescuentoVale(self, linea, order, curComanda, tipoMov):
        _i = self.iface
        try:
            print("//////////////////ENTRA EN crearLineaDescuentoVale")
            curLinea = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLinea.setModeAccess(curLinea.Insert)
            curLinea.refreshBuffer()

            codigo = curComanda.valueBuffer("codigo")
            nl = _i.obtenerNumLineaComanda(codigo)
            iva = parseFloat(linea["tax_percent"])
            if not iva or iva == "":
                iva = 0

            codiva = _i.obtenerCodImpuesto(iva)

            pvpUnitario = parseFloat(order["vale_total"]) / ((100 + iva) / 100)
            pvpSinDto = pvpUnitario
            pvpTotal = pvpSinDto
            pvpUnitarioIva = parseFloat(order["vale_total"])
            pvpSinDtoIva = pvpUnitarioIva
            pvpTotalIva = pvpUnitarioIva

            if tipoMov == "ValesNegativos":
                pvpSinDto = pvpSinDto * (-1)
                pvpTotal = pvpTotal * (-1)
                pvpSinDtoIva = pvpUnitarioIva * (-1)
                pvpTotalIva = pvpUnitarioIva * (-1)

            curLinea.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curLinea.setValueBuffer("codtienda", "AWEB")
            curLinea.setValueBuffer("cantidad", 1)
            curLinea.setValueBuffer("cantdevuelta", 0)
            curLinea.setValueBuffer("pvpunitario", pvpUnitario)
            curLinea.setValueBuffer("pvpsindto", pvpSinDto)
            curLinea.setValueBuffer("pvptotal", pvpTotal)
            curLinea.setValueBuffer("pvpunitarioiva", pvpUnitarioIva)
            curLinea.setValueBuffer("pvpsindtoiva", pvpSinDtoIva)
            curLinea.setValueBuffer("pvptotaliva", pvpTotalIva)
            curLinea.setValueBuffer("iva", iva)
            curLinea.setValueBuffer("descripcion", "DESCUENTO VALE " + str(order["vale_description"]))
            curLinea.setValueBuffer("referencia", "0000ATEMP00040")
            curLinea.setValueBuffer("barcode", "8433614171347")
            curLinea.setValueBuffer("numlinea", nl)
            curLinea.setValueBuffer("ivaincluido", True)
            curLinea.setValueBuffer("codimpuesto", codiva[:10] if codiva else codiva)
            curLinea.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)

            idsincro = qsatype.FactoriaModulos.get("formRecordlineaspedidoscli").iface.pub_commonCalculateField("idsincro", curLinea)
            curLinea.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)
            print("ANTES COMMIT")
            if not curLinea.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar la línea ", nl, " de la venta ", str(codigo)), "mgsyncdevweb")
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearRegistroMovVales(self, linea, order, curComanda, tipoMov):

        try:
            print("//////////////////ENTRA EN crearRegistroMovVales")
            idSincroLinea = str(qsatype.FLUtil.quickSqlSelect("tpv_lineascomanda", "idsincro", "idtpv_comanda = " + str(curComanda.valueBuffer("idtpv_comanda")) + " AND descripcion LIKE  '%" + str(order["vale_description"]) + "%'"))

            if not idSincroLinea or idSincroLinea == "None":
                syncppal.iface.log("Error. No se encuentra el idsincro relacionado con la línea del vale de la venta " + curComanda.valueBuffer("codigo"), "mgsyncdevweb")
                return False

            importe = parseFloat(order["vale_total"])
            if tipoMov == "ValesNegativos":
                importe = importe * (-1)

            curMovVale = qsatype.FLSqlCursor("tpv_movivale")
            curMovVale.setModeAccess(curMovVale.Insert)
            curMovVale.refreshBuffer()
            curMovVale.setValueBuffer("total", importe)
            curMovVale.setValueBuffer("idsincropago", idSincroLinea)
            curMovVale.setValueBuffer("refvale", str(order["vale_description"]))

            if not curMovVale.commitBuffer():
                return False

            if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_vales SET saldoconsumido = CASE WHEN (SELECT SUM(total) FROM tpv_movivale WHERE refvale = tpv_vales.referencia) IS NULL THEN 0 ELSE (SELECT SUM(total) FROM tpv_movivale WHERE refvale = tpv_vales.referencia) END WHERE referencia = '", str(order["vale_description"]), "'")):
                return False

            if not qsatype.FLUtil.execSql(ustr(u"UPDATE tpv_vales SET saldopendiente = CASE WHEN (total - saldoconsumido) IS NULL THEN 0 ELSE (total - saldoconsumido) END, fechamod = CURRENT_DATE, horamod = CURRENT_TIME WHERE referencia = '", str(order["vale_description"]), "'")):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_actualizarCantDevueltaOrder(self, linea, curComanda, order):
        _i = self.iface
        try:

            ref = _i.obtenerReferencia(linea["sku"])
            bc = _i.obtenerBarcode(linea["sku"])

            idTpvComandaOriginal = str(qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(curComanda.valueBuffer("codcomandadevol")) + "'"))

            if str(idTpvComandaOriginal) == "None":
                return True

            curLinea = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLinea.select("idtpv_comanda = " + str(idTpvComandaOriginal) + " AND barcode = '" + bc + "' AND referencia = '" + ref + "' AND cantdevuelta < cantidad")

            if curLinea.first():
                curLinea.setModeAccess(curLinea.Edit)
                curLinea.setActivatedCheckIntegrity(False)
                curLinea.setActivatedCommitActions(False)
                curLinea.refreshBuffer()
                curLinea.setValueBuffer("cantdevuelta", parseFloat(curLinea.valueBuffer("cantdevuelta")) + parseFloat(linea["qty"]))

                if not curLinea.commitBuffer():
                    return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaMotivosDevolucion(self, linea, curComanda, order):
        _i = self.iface
        try:
            if not _i.creaRegistroDevolucionesTienda(linea, curComanda, order):
                return False

            if not _i.creaRegistroMotivoDevolucion(linea, curComanda, order):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaRegistroDevolucionesTienda(self, linea, curComanda, order):
        _i = self.iface
        try:
            curDevolT = qsatype.FLSqlCursor("eg_devolucionestienda")
            curDevolT.select("codcomandaoriginal = '" + str(curComanda.valueBuffer("codcomandadevol")) + "' AND coddevolucion = '" + str(curComanda.valueBuffer("codigo")) + "'")
            if(curDevolT.first()):
                return True

            curDevolT = qsatype.FLSqlCursor("eg_devolucionestienda")
            curDevolT.setModeAccess(curDevolT.Insert)
            curDevolT.refreshBuffer()
            curDevolT.setValueBuffer("codcomandaoriginal", str(curComanda.valueBuffer("codcomandadevol")))
            curDevolT.setValueBuffer("coddevolucion", str(curComanda.valueBuffer("codigo")))
            curDevolT.setValueBuffer("sincronizada", True)
            curDevolT.setValueBuffer("fecha", str(qsatype.Date())[:10])
            curDevolT.setValueBuffer("hora", _i.obtenerHora(str(qsatype.Date())))
            curDevolT.setValueBuffer("codtienda", "AWEB")

            if "items_requested" in order:
                curDevolT.setValueBuffer("codcomandacambio", str(curComanda.valueBuffer("codigo")))
                curDevolT.setValueBuffer("cambio", True)
            else:
                curDevolT.setNull("codcomandacambio")
                curDevolT.setValueBuffer("cambio", False)

            if not curDevolT.commitBuffer():
                return False

            curDevolT.select("codcomandaoriginal = '" + str(curComanda.valueBuffer("codcomandadevol")) + "' AND coddevolucion = '" + str(curComanda.valueBuffer("codigo")) + "'")
            if(curDevolT.first()):
                curDevolT.setModeAccess(curDevolT.Edit)
                curDevolT.refreshBuffer()
                curDevolT.setValueBuffer("idsincro", str(curComanda.valueBuffer("codigo")) + "_" + str(curDevolT.valueBuffer("id")))
                curDevolT.commitBuffer()

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaRegistroMotivoDevolucion(self, linea, curComanda, order):
        _i = self.iface
        try:

            curMotivos = qsatype.FLSqlCursor("eg_motivosdevolucion")
            curMotivos.setModeAccess(curMotivos.Insert)
            curMotivos.refreshBuffer()
            curMotivos.setValueBuffer("codcomandadevol", str(curComanda.valueBuffer("codigo")))
            curMotivos.setValueBuffer("referencia", _i.obtenerReferencia(linea["sku"]))
            curMotivos.setValueBuffer("barcode", _i.obtenerBarcode(linea["sku"]))
            curMotivos.setValueBuffer("descripcion", _i.obtenerDescripcion(linea["sku"]))
            curMotivos.setValueBuffer("talla", _i.obtenerTalla(linea["sku"]))
            curMotivos.setValueBuffer("cantidad", parseFloat(linea["qty"]))
            curMotivos.setValueBuffer("pvpunitarioiva", parseFloat(linea["original_price"]))
            curMotivos.setValueBuffer("idsincro", str(curComanda.valueBuffer("codigo")) + "_" + str(curMotivos.valueBuffer("id")))
            curMotivos.setValueBuffer("motivos", str(linea["reason"]))
            curMotivos.setValueBuffer("sincronizada", True)
            if not curMotivos.commitBuffer():
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearRegistroMovistock(self, curLinea):
        try:

            idStock = str(qsatype.FLUtil.quickSqlSelect("stocks", "idstock", "barcode = '" + str(curLinea.valueBuffer("barcode")) + "' AND codalmacen = 'AWEB'"))

            curMoviStock = qsatype.FLSqlCursor("movistock")
            curMoviStock.setModeAccess(curMoviStock.Insert)
            curMoviStock.refreshBuffer()
            curMoviStock.setValueBuffer("idlineaco", curLinea.valueBuffer("idtpv_linea"))
            curMoviStock.setValueBuffer("estado", "PTE")
            curMoviStock.setValueBuffer("cantidad", (curLinea.valueBuffer("cantidad") * (-1)))
            curMoviStock.setValueBuffer("referencia", curLinea.valueBuffer("referencia"))
            curMoviStock.setValueBuffer("barcode", curLinea.valueBuffer("barcode"))
            curMoviStock.setValueBuffer("idstock", idStock)
            if not curMoviStock.commitBuffer():
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaRegistroEcommerce(self, linea, curComanda, order):
        _i = self.iface
        try:

            if not qsatype.FLUtil.execSql("INSERT INTO idl_ecommercedevoluciones (idtpv_comanda,codcomanda,tipo,envioidl) VALUES ('" + str(curComanda.valueBuffer("idtpv_comanda")) + "', '" + str(curComanda.valueBuffer("codigo")) + "', 'DEVOLUCION',false)"):
                return False

            if "items_requested" in order:
                for linea in order["items_requested"]:
                    if not _i.crearRegistroECommerceCambio(linea, curComanda, order):
                        return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_crearRegistroECommerceCambio(self, linea, curComanda, order):
        try:
            transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = '" + str(order["carrier"]) + "' OR UPPER(metodoenviomg) = '" + str(order["carrier"]) + "'")

            if not transIDL:
                syncppal.iface.log(ustr("Error. No se encuentra el método de envío ", str(order["carrier"])), "mgsyncorders")
                return False

            metodoIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = '" + str(order["carrier"]) + "' OR UPPER(metodoenviomg) = '" + str(order["carrier"]) + "'")

            impAlbaran = False
            impFactura = False
            impDedicatoria = False
            esRegalo = False
            emisor = ""
            receptor = ""
            mensajeDedicatoria = ""

            if "country" in order["pickup_address"]:
                if str(order["pickup_address"]["country"]) == "ES":
                    if "postcode" in order["pickup_address"]:
                        if str(order["pickup_address"]["postcode"]).startswith("38") or str(order["pickup_address"]["postcode"]).startswith("35"):
                                impFactura = True
                else:
                    imprimirFacturaPais = qsatype.FLUtil.sqlSelect("paises", "imprimirfactura", "codiso = '" + str(order["pickup_address"]["country"]) + "'")
                    if imprimirFacturaPais:
                        impFactura = True

            if not qsatype.FLUtil.execSql("INSERT INTO idl_ecommerce (idtpv_comanda,codcomanda,tipo,transportista,metodoenvioidl,imprimiralbaran,imprimirfactura,imprimirdedicatoria,emisor,receptor,mensajededicatoria,esregalo,facturaimpresa,envioidl,numseguimientoinformado,confirmacionenvio) VALUES ('" + str(curComanda.valueBuffer("idtpv_comanda")) + "', '" + str(curComanda.valueBuffer("codigo")) + "', 'CAMBIO', '" + str(transIDL) + "','" + str(metodoIDL) + "','" + str(impAlbaran) + "','" + str(impFactura) + "','" + str(impDedicatoria) + "','" + str(emisor) + "','" + str(receptor) + "','" + str(mensajeDedicatoria) + "','" + str(esRegalo) + "',false,false,false,'No')"):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)

    def getUnsynchronizedDevWeb(self):
        return self.ctx.elganso_sync_getUnsynchronizedDevWeb()

    def processOrdersDevWeb(self, orders):
        return self.ctx.elganso_sync_processOrdersDevWeb(orders)

    def creaCabeceraComandaDevWeb(self, order, codigo):
        return self.ctx.elganso_sync_creaCabeceraComandaDevWeb(order, codigo)

    def creaLineaComanda(self, linea, curComanda, increment):
        return self.ctx.elganso_sync_creaLineaComanda(linea, curComanda, increment)

    def obtenerCodSerie(self, nomPais=None, codPostal=None):
        return self.ctx.elganso_sync_obtenerCodSerie(nomPais, codPostal)

    def obtenerEjercicio(self, fecha):
        return self.ctx.elganso_sync_obtenerEjercicio(fecha)

    def obtenerHora(self, fecha):
        return self.ctx.elganso_sync_obtenerHora(fecha)

    def obtenerCodPais(self, paisfc=None):
        return self.ctx.elganso_sync_obtenerCodPais(paisfc)

    def obtenerCodPago(self, metPago):
        return self.ctx.elganso_sync_obtenerCodPago(metPago)

    def conFac(self, fac):
        return self.ctx.elganso_sync_conFac(fac)

    def obtenerColor(self, sku):
        return self.ctx.elganso_sync_obtenerColor(sku)

    def obtenerTalla(self, sku):
        return self.ctx.elganso_sync_obtenerTalla(sku)

    def obtenerReferencia(self, sku):
        return self.ctx.elganso_sync_obtenerReferencia(sku)

    def obtenerNumLineaComanda(self, codigo):
        return self.ctx.elganso_sync_obtenerNumLineaComanda(codigo)

    def obtenerDescripcion(self, sku):
        return self.ctx.elganso_sync_obtenerDescripcion(sku)

    def obtenerBarcode(self, sku):
        return self.ctx.elganso_sync_obtenerBarcode(sku)

    def obtenerCodImpuesto(self, iva):
        return self.ctx.elganso_sync_obtenerCodImpuesto(iva)

    def cerrarVentaWeb(self, curComanda, order):
        return self.ctx.elganso_sync_cerrarVentaWeb(curComanda, order)

    def crearArqueoVentaWeb(self, curComanda):
        return self.ctx.elganso_sync_crearArqueoVentaWeb(curComanda)

    def crearPagosDevWeb(self, curComanda, idArqueo, order):
        return self.ctx.elganso_sync_crearPagosDevWeb(curComanda, idArqueo, order)

    def masDatosArqueo(self, curArqueo, curComanda):
        return self.ctx.elganso_sync_masDatosArqueo(curArqueo, curComanda)

    def obtenerCodFactura(self):
        return self.ctx.elganso_sync_obtenerCodFactura()

    def creaLineaComandaDevWeb(self, linea, curComanda, increment, tipoLinea):
        return self.ctx.elganso_sync_creaLineaComandaDevWeb(linea, curComanda, increment, tipoLinea)

    def controlTallasDevolucion(self, order):
        return self.ctx.elganso_sync_controlTallasDevolucion(order)

    def crearPagoDevWeb(self, curComanda, idArqueo, order, tipoPago):
        return self.ctx.elganso_sync_crearPagoDevWeb(curComanda, idArqueo, order, tipoPago)

    def controlMovBono(self, linea, order, curComanda):
        return self.ctx.elganso_sync_controlMovBono(linea, order, curComanda)

    def insertarLineaBono(self, linea, order, curComanda, tipoMov):
        return self.ctx.elganso_sync_insertarLineaBono(linea, order, curComanda, tipoMov)

    def insertarMovBono(self, linea, order, curComanda, tipoMov):
        return self.ctx.elganso_sync_insertarMovBono(linea, order, curComanda, tipoMov)

    def controlMovPuntos(self, linea, order, curComanda):
        return self.ctx.elganso_sync_controlMovPuntos(linea, order, curComanda)

    def crearLineaDescuentoPuntos(self, linea, order, curComanda, tipoMov):
        return self.ctx.elganso_sync_crearLineaDescuentoPuntos(linea, order, curComanda, tipoMov)

    def crearRegistroMovPuntos(self, order, curComanda, tipoMov):
        return self.ctx.elganso_sync_crearRegistroMovPuntos(order, curComanda, tipoMov)

    def controlMovVale(self, linea, order, curComanda):
        return self.ctx.elganso_sync_controlMovVale(linea, order, curComanda)

    def crearLineaDescuentoVale(self, linea, order, curComanda, tipoMov):
        return self.ctx.elganso_sync_crearLineaDescuentoVale(linea, order, curComanda, tipoMov)

    def crearRegistroMovVales(self, linea, order, curComanda, tipoMov):
        return self.ctx.elganso_sync_crearRegistroMovVales(linea, order, curComanda, tipoMov)

    def actualizarCantDevueltaOrder(self, linea, curComanda, order):
        return self.ctx.elganso_sync_actualizarCantDevueltaOrder(linea, curComanda, order)

    def creaMotivosDevolucion(self, linea, curComanda, order):
        return self.ctx.elganso_sync_creaMotivosDevolucion(linea, curComanda, order)

    def creaRegistroDevolucionesTienda(self, linea, curComanda, order):
        return self.ctx.elganso_sync_creaRegistroDevolucionesTienda(linea, curComanda, order)

    def creaRegistroMotivoDevolucion(self, linea, curComanda, order):
        return self.ctx.elganso_sync_creaRegistroMotivoDevolucion(linea, curComanda, order)

    def crearRegistroMovistock(self, curLinea):
        return self.ctx.elganso_sync_crearRegistroMovistock(curLinea)

    def creaRegistroEcommerce(self, linea, curComanda, order):
        return self.ctx.elganso_sync_creaRegistroEcommerce(linea, curComanda, order)

    def crearRegistroECommerceCambio(self, linea, curComanda, order):
        return self.ctx.elganso_sync_crearRegistroECommerceCambio(linea, curComanda, order)


# @class_declaration head #
class head(elganso_sync):

    def __init__(self, context=None):
        super(head, self).__init__(context)


# @class_declaration ifaceCtx #
class ifaceCtx(head):

    def __init__(self, context=None):
        super(ifaceCtx, self).__init__(context)


# @class_declaration FormInternalObj #
class FormInternalObj(qsatype.FormDBWidget):
    def _class_init(self):
        self.iface = ifaceCtx(self)


form = FormInternalObj()
form._class_init()
form.iface.ctx = form.iface
form.iface.iface = form.iface
iface = form.iface
