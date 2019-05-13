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
    def elganso_sync_getUnsynchronizedOrders(self):
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
                url = 'https://www.elganso.com/syncapi/index.php/orders/unsynchronized'
            else:
                url = 'http://local2.elganso.com/syncapi/index.php/orders/unsynchronized'

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
            syncppal.iface.log("Error. No se pudo establecer la conexión con el servidor.", "mgsyncorders")
            return cdLarge

        if json and len(json):
            try:
                aOrders = _i.processOrders(json)

                if not aOrders and not isinstance(aOrders, (list, tuple, dict)):
                    syncppal.iface.log("Error. Ocurrió un error al sincronizar los pedidos.", "mgsyncorders")
                    raise Exception
            except Exception as e:
                print(e)
                return cdSmall

            if aOrders and len(aOrders.keys()):
                strCods = ""
                for k in aOrders.keys():
                    strCods += k if strCods == "" else ", " + k
                syncppal.iface.log(ustr("Éxito. Los siguientes pedidos se han sincronizado correctamente: ", str(strCods)), "mgsyncorders")
                for order in aOrders.keys():
                    try:
                        url = None
                        if qsatype.FLUtil.isInProd():
                            url = 'https://www.elganso.com/syncapi/index.php/orders/' + str(aOrders[order]) + '/synchronized'
                        else:
                            url = 'http://local2.elganso.com/syncapi/index.php/orders/' + str(aOrders[order]) + '/synchronized'

                        print("Llamando a", url)
                        response = requests.put(url, headers=headers)
                        print("Correcto")
                    except Exception:
                        syncppal.iface.log(ustr("Error. El pedido ", str(order), " no ha podido marcarse como sincronizado."), "mgsyncorders")
            elif aOrders == {}:
                syncppal.iface.log("Éxito. No hay pedidos que sincronizar.", "mgsyncorders")
                return cdLarge
        else:
            syncppal.iface.log("Éxito. No hay pedidos que sincronizar.", "mgsyncorders")
            return cdLarge

        return cdSmall

    def elganso_sync_processOrders(self, orders):
        _i = self.iface

        aOrders = {}
        saltar = {}
        iva = 0

        for order in orders:
            if order["entity_id"] in saltar:
                continue

            codigo = "WEB" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(order["increment_id"]), 9)

            if qsatype.FLUtil.sqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + codigo + "'"):
                saltar[order["entity_id"]] = order["entity_id"]
                aOrders[codigo] = order["entity_id"]
                continue

            iva = 0

            curComanda = _i.creaCabeceraComanda(order, codigo)
            if not curComanda:
                return False

            for linea in order["items"]:
                if not _i.creaLineaComanda(linea, curComanda, order["increment_id"]):
                    return False

                iva = linea["iva"]

            if not _i.creaLineaEnvio(order, curComanda):
                return False

            if not _i.creaLineaGastosComanda(curComanda, order["shipping_price"], iva):
                return False

            if not _i.creaLineaDescuento(curComanda, order["discount_amount"], iva):
                return False

            objVale = False
            if order["vale_description"]:
                objVale = {
                    "desc": order["vale_description"],
                    "codcli": order["vale_codigo_cliente"],
                    "total": order["vale_total"]
                }
                if not _i.creaLineaVale(curComanda, objVale, iva):
                    return False

            neto = round(parseFloat(order["grand_total"] / ((100 + iva) / 100)), 2)
            iva = order["grand_total"] - neto
            if not qsatype.FLSqlQuery().execSql(u"UPDATE tpv_comandas SET total = " + str(order["grand_total"]) + ", neto = " + str(neto) + ", totaliva = " + str(iva) + " WHERE codigo = '" + str(codigo) + "'"):
                syncppal.iface.log(ustr("Error. No se pudieron actualizar los totales para ", str(codigo)), "mgsyncorders")
                return False

            iva = 0

            if not _i.cerrarVentaWeb(curComanda):
                syncppal.iface.log(ustr("Error. No se pudo cerrar la venta ", str(codigo)), "mgsyncorders")
                return False

            if not _i.crearRegistroECommerce(order, curComanda):
                syncppal.iface.log(ustr("Error. No se pudo crear el registro para Ecommerce", str(codigo)), "mgsyncorders")
                return False

            codigo = ustr("WEB", qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(ustr(order["increment_id"]), 9))
            aOrders[codigo] = order["entity_id"]

        return aOrders

    def elganso_sync_creaCabeceraComanda(self, order, codigo):
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
            nombrecliente = str(order["billing_address"]["firstname"]) + " " + str(order["billing_address"]["lastname"])

            street = order["billing_address"]["street"].split("\n")
            dirtipovia = street[0] if len(street) >= 1 else ""
            direccion = street[1] if len(street) >= 2 else ""
            dirnum = street[2] if len(street) >= 3 else ""
            dirotros = street[3] if len(street) >= 4 else ""

            codpostal = str(order["billing_address"]["postcode"])
            city = order["billing_address"]["city"]
            region = order["billing_address"]["region"]
            codpais = order["billing_address"]["country_id"]
            telefonofac = order["billing_address"]["telephone"]
            codpago = _i.obtenerCodPago(order["payment_method"])
            email = order["email"]
            codtarjetapuntos = order["card_points"]
            egcodfactura = _i.obtenerCodFactura()

            curComanda.setValueBuffer("codserie", _i.obtenerCodSerie(order["billing_address"]["country_id"], order["billing_address"]["postcode"]))
            curComanda.setValueBuffer("codejercicio", _i.obtenerEjercicio(order["created_at"]))
            curComanda.setValueBuffer("codtpv_puntoventa", "AWEB")
            curComanda.setValueBuffer("codtpv_agente", "0350")
            curComanda.setValueBuffer("codalmacen", "AWEB")
            curComanda.setValueBuffer("codtienda", "AWEB")
            curComanda.setValueBuffer("fecha", order["created_at"][:10])
            curComanda.setValueBuffer("hora", _i.obtenerHora(order["created_at"]))
            curComanda.setValueBuffer("nombrecliente", nombrecliente[:100] if nombrecliente else nombrecliente)
            curComanda.setValueBuffer("cifnif", cif)
            curComanda.setValueBuffer("dirtipovia", dirtipovia[:100] if dirtipovia else dirtipovia)
            curComanda.setValueBuffer("direccion", direccion[:100] if direccion else direccion)
            curComanda.setValueBuffer("dirnum", dirnum[:100] if dirnum else dirnum)
            curComanda.setValueBuffer("dirotros", dirotros[:100] if dirotros else dirotros)
            curComanda.setValueBuffer("codpostal", codpostal[:10] if codpostal else codpostal)
            curComanda.setValueBuffer("ciudad", city[:100] if city else city)
            curComanda.setValueBuffer("provincia", region[:100] if region else region)
            curComanda.setValueBuffer("telefono1", telefonofac[:30] if telefonofac else telefonofac)
            curComanda.setValueBuffer("codpais", codpais[:20] if codpais else codpais)
            curComanda.setValueBuffer("codpago", codpago[:10] if codpago else codpago)
            curComanda.setValueBuffer("coddivisa", "EUR")
            curComanda.setValueBuffer("tasaconv", 1)
            curComanda.setValueBuffer("email", email[:100] if email else email)
            curComanda.setValueBuffer("total", order["grand_total"])
            curComanda.setValueBuffer("neto", order["subtotal"])
            curComanda.setValueBuffer("totaliva", order["tax_amount"])
            curComanda.setValueBuffer("codtarjetapuntos", codtarjetapuntos[:15] if codtarjetapuntos else codtarjetapuntos)
            curComanda.setValueBuffer("ptesincrofactura", True)
            curComanda.setValueBuffer("egcodfactura", egcodfactura[:12] if egcodfactura else egcodfactura)

            if order["shipping_method"].startswith("pl_store_pickup"):
                codtiendarecogida = order["shipping_address"]["lastname"]

                curComanda.setValueBuffer("recogidatienda", True)
                curComanda.setValueBuffer("codtiendarecogida", codtiendarecogida[:10] if codtiendarecogida else codtiendarecogida)

            if not curComanda.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar la cabecera de la venta ", str(codigo)), "mgsyncorders")
                return False

            curComanda.select("codigo = '" + str(codigo) + "'")
            if not curComanda.first():
                syncppal.iface.log(ustr("Error. No se pudo recuperar la cabecera guardada para ", str(codigo)), "mgsyncorders")
                return False

            curComanda.setModeAccess(curComanda.Edit)
            curComanda.refreshBuffer()

            return curComanda

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaLineaEnvio(self, order, curComanda):
        _i = self.iface

        try:
            curEnv = qsatype.FLSqlCursor("mg_datosenviocomanda")
            curEnv.setModeAccess(curEnv.Insert)
            curEnv.refreshBuffer()

            tracking = order["tracking_number"] if order["tracking_number"] and order["tracking_number"] != "" else ""
            street = order["shipping_address"]["street"].split("\n")
            dirtipoviaenv = street[0] if len(street) >= 1 else ""
            direccionenv = street[1] if len(street) >= 2 else ""
            dirnumenv = street[2] if len(street) >= 3 else ""
            dirotrosenv = street[3] if len(street) >= 4 else ""

            numcliente = order["customer_id"]
            email = order["email"]
            metodopago = order["payment_method"]
            metodoenvio = order["shipping_description"]
            nombreenv = order["shipping_address"]["firstname"]
            apellidosenv = order["shipping_address"]["lastname"]
            codpostalenv = str(order["shipping_address"]["postcode"])
            ciudad = order["shipping_address"]["city"]
            region = order["shipping_address"]["region"]
            pais = order["shipping_address"]["country_id"]
            telefonoenv = order["shipping_address"]["telephone"]

            curEnv.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curEnv.setValueBuffer("mg_numcliente", numcliente[:15] if numcliente else numcliente)
            curEnv.setValueBuffer("mg_email", email[:200] if email else email)
            curEnv.setValueBuffer("mg_metodopago", metodopago[:30] if metodopago else metodopago)
            curEnv.setValueBuffer("mg_confac", _i.conFac(False))
            curEnv.setValueBuffer("mg_metodoenvio", metodoenvio[:500] if metodoenvio else metodoenvio)
            curEnv.setValueBuffer("mg_unidadesenv", order["units"])
            curEnv.setValueBuffer("mg_numseguimiento", tracking[:100] if tracking else tracking)
            curEnv.setValueBuffer("mg_nombreenv", nombreenv[:100] if nombreenv else nombreenv)
            curEnv.setValueBuffer("mg_apellidosenv", apellidosenv[:200] if apellidosenv else apellidosenv)
            curEnv.setValueBuffer("mg_dirtipoviaenv", dirtipoviaenv[:100] if dirtipoviaenv else dirtipoviaenv)
            curEnv.setValueBuffer("mg_direccionenv", direccionenv[:200] if direccionenv else direccionenv)
            curEnv.setValueBuffer("mg_dirnumenv", dirnumenv[:100] if dirnumenv else dirnumenv)
            curEnv.setValueBuffer("mg_dirotrosenv", dirotrosenv[:100] if dirotrosenv else dirotrosenv)
            curEnv.setValueBuffer("mg_codpostalenv", codpostalenv[:10] if codpostalenv else codpostalenv)
            curEnv.setValueBuffer("mg_ciudadenv", ciudad[:100] if ciudad else ciudad)
            curEnv.setValueBuffer("mg_provinciaenv", region[:100] if region else region)
            curEnv.setValueBuffer("mg_paisenv", pais[:100] if pais else pais)
            curEnv.setValueBuffer("mg_telefonoenv", telefonoenv[:30] if telefonoenv else telefonoenv)
            curEnv.setValueBuffer("mg_gastosenv", order["shipping_price"])

            if order["shipping_method"].startswith("pl_store_pickup"):
                telefonofac = order["billing_address"]["telephone"]

                curEnv.setValueBuffer("mg_telefonoenv", telefonofac[:30] if telefonofac else telefonofac)

            if not curEnv.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo guardar el envío de la venta ", str(curComanda.valueBuffer("codigo"))), "mgsyncorders")
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaLineaComanda(self, linea, curComanda, increment):
        _i = self.iface

        try:
            curLinea = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLinea.setModeAccess(curLinea.Insert)
            curLinea.refreshBuffer()

            codigo = curComanda.valueBuffer("codigo")
            nl = _i.obtenerNumLineaComanda(increment)
            iva = linea["iva"]
            if not iva or iva == "":
                iva = 0

            desc = _i.obtenerDescripcion(linea["sku"])
            ref = _i.obtenerReferencia(linea["sku"])
            bc = _i.obtenerBarcode(linea["sku"])
            talla = _i.obtenerTalla(linea["sku"])
            color = _i.obtenerColor(linea["sku"])
            codiva = _i.obtenerCodImpuesto(linea["iva"])

            curLinea.setValueBuffer("idtpv_comanda", curComanda.valueBuffer("idtpv_comanda"))
            curLinea.setValueBuffer("codtienda", "AWEB")
            curLinea.setValueBuffer("cantidad", linea["cantidad"])
            curLinea.setValueBuffer("cantdevuelta", 0)
            curLinea.setValueBuffer("pvpunitarioiva", linea["pvpunitarioiva"])
            curLinea.setValueBuffer("pvpsindtoiva", linea["pvpsindtoiva"])
            curLinea.setValueBuffer("pvptotaliva", linea["pvptotaliva"])
            curLinea.setValueBuffer("pvpunitario", parseFloat(linea["pvpunitarioiva"] / ((100 + iva) / 100)))
            curLinea.setValueBuffer("pvpsindto", parseFloat(linea["pvpsindtoiva"] / ((100 + iva) / 100)))
            curLinea.setValueBuffer("pvptotal", parseFloat(linea["pvptotaliva"] / ((100 + iva) / 100)))
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
                syncppal.iface.log(ustr("Error. No se pudo guardar la línea ", nl, " de la venta ", str(codigo)), "mgsyncorders")
                return False

            return True

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
        codigo = "WEB" + qsatype.FactoriaModulos.get("flfactppal").iface.cerosIzquierda(str(codigo), 9)
        idComanda = qsatype.FLUtil.quickSqlSelect("tpv_comandas", "idtpv_comanda", "codigo = '" + str(codigo) + "'")
        numL = parseInt(qsatype.FLUtil.quickSqlSelect("tpv_comandas", "count(*)", "idtpv_comanda = " + str(idComanda)))
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

    def elganso_sync_creaLineaGastosComanda(self, curComanda, gastos, iva):
        try:
            tieneIva = curComanda.valueBuffer("totaliva")
            idComanda = curComanda.valueBuffer("idtpv_comanda")
            codigo = curComanda.valueBuffer("codigo")

            if not idComanda or idComanda == 0:
                return False
            if not gastos or gastos == 0:
                return True

            curLGastos = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLGastos.setModeAccess(curLGastos.Insert)
            curLGastos.refreshBuffer()

            curLGastos.setValueBuffer("idtpv_comanda", idComanda)
            curLGastos.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)
            curLGastos.setValueBuffer("referencia", "0000ATEMP00001")
            curLGastos.setValueBuffer("barcode", "8433613403654")
            curLGastos.setValueBuffer("descripcion", "MANIPULACIÓN Y ENVIO")

            gastosSinIva = None

            if tieneIva and tieneIva != 0:
                curLGastos.setValueBuffer("codimpuesto", "GEN")
                curLGastos.setValueBuffer("iva", iva)
                gastosSinIva = gastos / (1 + (parseFloat(iva) / 100))
            else:
                curLGastos.setValueBuffer("codimpuesto", "EXT")
                curLGastos.setValueBuffer("iva", 0)
                gastosSinIva = gastos

            curLGastos.setValueBuffer("ivaincluido", True)
            curLGastos.setValueBuffer("pvpunitarioiva", gastos)
            curLGastos.setValueBuffer("pvpunitario", gastosSinIva)
            curLGastos.setValueBuffer("pvpsindto", gastosSinIva)
            curLGastos.setValueBuffer("pvptotal", gastosSinIva)
            curLGastos.setValueBuffer("pvptotaliva", gastos)
            curLGastos.setValueBuffer("pvpsindtoiva", gastos)
            curLGastos.setValueBuffer("codtienda", "AWEB")

            idsincro = qsatype.FactoriaModulos.get('formRecordtpv_lineascomanda').iface.pub_commonCalculateField("idsincro", curLGastos)
            curLGastos.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curLGastos.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo crear la línea de gastos de la venta ", str(codigo)), "mgsyncorders")
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaLineaDescuento(self, curComanda, dto, iva):
        try:
            idComanda = curComanda.valueBuffer("idtpv_comanda")
            codigo = curComanda.valueBuffer("codigo")

            if not idComanda or idComanda == 0 or not dto or dto == 0 or dto == "0.0000" or dto == "0.00":
                return True

            descBono = False
            jsonBono = False
            codBono = False
            strBono = qsatype.FLUtil.sqlSelect("tpv_gestionparametros", "valor", "param = 'GASTAR_BONOS'")

            try:
                jsonBono = json.loads(strBono)
            except Exception:
                pass

            if jsonBono and "fechahasta" in jsonBono and jsonBono["fechahasta"] and jsonBono["fechahasta"] != "":
                if qsatype.FLUtil.daysTo(qsatype.Date(), jsonBono["fechahasta"]) >= 0:
                    descBono = True

            if descBono:
                codBono = qsatype.FLUtil.sqlSelect("eg_movibono", "codbono", "venta = '" + codigo + "'")
                if not codBono or codBono == "" or codBono is None:
                    descBono = False

            if descBono:
                dto = qsatype.FLUtil.sqlSelect("eg_movibono", "importe", "codbono = '" + codBono + "' AND venta = '" + codigo + "'")

                if codigo[:4] == "WEB7":
                    dto = dto / 0.8

                ref = jsonBono["referenciabono"]
                bC = jsonBono["barcodebono"]
                desc = "BONO " + codBono
            else:
                ref = "0000ATEMP00001"
                bC = "8433613403654"
                desc = "DESCUENTO"

            curLDesc = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLDesc.setModeAccess(curLDesc.Insert)
            curLDesc.refreshBuffer()
            curLDesc.setValueBuffer("idtpv_comanda", idComanda)
            curLDesc.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)
            curLDesc.setValueBuffer("referencia", ref[:18] if ref else ref)
            curLDesc.setValueBuffer("barcode", bC[:20] if bC else bC)
            curLDesc.setValueBuffer("descripcion", desc[:100] if desc else desc)

            dtoSinIva = None
            print("///////////IVA1: ", iva)
            if iva and iva != 0:
                curLDesc.setValueBuffer("codimpuesto", "GEN")
                curLDesc.setValueBuffer("iva", iva)
                dtoSinIva = dto / (1 + (parseFloat(iva) / 100))
            else:
                curLDesc.setValueBuffer("codimpuesto", "EXT")
                curLDesc.setValueBuffer("iva", 0)
                dtoSinIva = dto

            curLDesc.setValueBuffer("ivaincluido", True)
            curLDesc.setValueBuffer("pvpunitarioiva", dto)
            curLDesc.setValueBuffer("pvpunitario", dtoSinIva)
            curLDesc.setValueBuffer("pvpsindto", dtoSinIva)
            curLDesc.setValueBuffer("pvptotal", dtoSinIva)
            curLDesc.setValueBuffer("pvptotaliva", dto)
            curLDesc.setValueBuffer("pvpsindtoiva", dto)
            curLDesc.setValueBuffer("codtienda", "AWEB")

            idsincro = qsatype.FactoriaModulos.get('formRecordtpv_lineascomanda').iface.pub_commonCalculateField("idsincro", curLDesc)
            curLDesc.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curLDesc.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo crear la línea de descuento de la venta ", str(codigo)), "mgsyncorders")
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_creaLineaVale(self, curComanda, objVale, iva):
        try:
            idComanda = curComanda.valueBuffer("idtpv_comanda")
            codigo = curComanda.valueBuffer("codigo")
            if not objVale["total"] or objVale["total"] == 0:
                return True
            objVale["total"] = round(parseFloat(objVale["total"]) * (-1), 2)
            curLDesc = qsatype.FLSqlCursor("tpv_lineascomanda")
            curLDesc.setModeAccess(curLDesc.Insert)
            curLDesc.refreshBuffer()
            curLDesc.setValueBuffer("idtpv_comanda", idComanda)
            curLDesc.setValueBuffer("codcomanda", codigo[:12] if codigo else codigo)
            curLDesc.setValueBuffer("referencia", "0000ATEMP00040")
            curLDesc.setValueBuffer("barcode", "8433614171347")
            curLDesc.setValueBuffer("descripcion", objVale["desc"] + " " + objVale["codcli"])

            dtoSinIva = None
            print("///////////IVA: ", iva)
            if iva and iva != 0:
                curLDesc.setValueBuffer("codimpuesto", "GEN")
                curLDesc.setValueBuffer("iva", iva)
                dtoSinIva = objVale["total"] / (1 + (parseFloat(iva) / 100))
            else:
                curLDesc.setValueBuffer("codimpuesto", "EXT")
                curLDesc.setValueBuffer("iva", 0)
                dtoSinIva = objVale["total"]

            curLDesc.setValueBuffer("ivaincluido", True)
            curLDesc.setValueBuffer("pvpunitarioiva", objVale["total"])
            curLDesc.setValueBuffer("pvpunitario", dtoSinIva)
            curLDesc.setValueBuffer("pvpsindto", dtoSinIva)
            curLDesc.setValueBuffer("pvptotal", dtoSinIva)
            curLDesc.setValueBuffer("pvptotaliva", objVale["total"])
            curLDesc.setValueBuffer("pvpsindtoiva", objVale["total"])
            curLDesc.setValueBuffer("codtienda", "AWEB")

            idsincro = qsatype.FactoriaModulos.get('formRecordtpv_lineascomanda').iface.pub_commonCalculateField("idsincro", curLDesc)
            curLDesc.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curLDesc.commitBuffer():
                syncppal.iface.log(ustr("Error. No se pudo crear la línea de vale de la venta ", str(codigo)), "mgsyncorders")
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def elganso_sync_cerrarVentaWeb(self, curComanda):
        _i = self.iface

        try:
            idComanda = curComanda.valueBuffer("idtpv_comanda")

            codArqueo = _i.crearArqueoVentaWeb(curComanda)
            if not codArqueo:
                syncppal.iface.log(ustr("Error. No se pudo crear el arqueo"), "mgsyncorders")
                return False

            if not _i.crearPagoVentaWeb(curComanda, codArqueo):
                syncppal.iface.log(ustr("Error. No se pudo crear el pago para el arqueo ", str(codArqueo)), "mgsyncorders")
                return False

            if not qsatype.FLSqlQuery().execSql(u"UPDATE tpv_comandas SET estado = 'Cerrada', editable = true, pagado = total WHERE idtpv_comanda = " + str(idComanda)):
                syncppal.iface.log(ustr("Error. No se pudo cerrar la venta ", str(idComanda)), "mgsyncorders")
                return False

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

    def elganso_sync_crearPagoVentaWeb(self, curComanda, idArqueo):
        try:
            if not idArqueo or not curComanda:
                return False

            fecha = curComanda.valueBuffer("fecha")
            codTienda = "AWEB"
            idComanda = curComanda.valueBuffer("idtpv_comanda")
            codComanda = curComanda.valueBuffer("codigo")
            codTpvPuntoVenta = curComanda.valueBuffer("codtpv_puntoventa")
            codPago = curComanda.valueBuffer("codpago")
            importe = curComanda.valueBuffer("total")

            if not importe:
                importe = 0

            curPago = qsatype.FLSqlCursor("tpv_pagoscomanda")
            curPago.setModeAccess(curPago.Insert)
            curPago.refreshBuffer()

            curPago.setValueBuffer("idtpv_comanda", idComanda)
            curPago.setValueBuffer("codcomanda", codComanda[:12] if codComanda else codComanda)
            curPago.setValueBuffer("idtpv_arqueo", idArqueo[:8] if idArqueo else idArqueo)
            curPago.setValueBuffer("fecha", fecha)
            curPago.setValueBuffer("editable", True)
            curPago.setValueBuffer("nogenerarasiento", True)
            curPago.setValueBuffer("anulado", False)
            curPago.setValueBuffer("importe", importe)
            curPago.setValueBuffer("estado", "Pagado")
            curPago.setValueBuffer("codpago", codPago[:10] if codPago else codPago)
            curPago.setValueBuffer("codtpv_puntoventa", codTpvPuntoVenta[:6] if codTpvPuntoVenta else codTpvPuntoVenta)
            curPago.setValueBuffer("codtpv_agente", "0350")
            curPago.setValueBuffer("codtienda", codTienda)

            idsincro = qsatype.FactoriaModulos.get("formRecordtpv_pagoscomanda").iface.commonCalculateField("idsincro", curPago)
            curPago.setValueBuffer("idsincro", idsincro[:30] if idsincro else idsincro)

            if not curPago.commitBuffer():
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
            prefijo = "AWEBX"
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

    def elganso_sync_crearRegistroECommerce(self, order, curComanda):
        try:
            transIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "transportista", "LOWER(metodoenviomg) = '" + order["shipping_method"] + "' OR UPPER(metodoenviomg) = '" + order["shipping_method"] + "'")

            if not transIDL:
                syncppal.iface.log(ustr("Error. No se encuentra el método de envío ", str(order["shipping_method"])), "mgsyncorders")
                return False

            metodoIDL = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "metodoenvioidl", "LOWER(metodoenviomg) = '" + order["shipping_method"] + "' OR UPPER(metodoenviomg) = '" + order["shipping_method"] + "'")
            esRecogidaTienda = qsatype.FLUtil.sqlSelect("metodosenvio_transportista", "recogidaentienda", "LOWER(metodoenviomg) = '" + order["shipping_method"] + "' OR UPPER(metodoenviomg) = '" + order["shipping_method"] + "'")
            impAlbaran = True
            impFactura = False
            impDedicatoria = False
            esRegalo = False
            emisor = ""
            receptor = ""
            mensajeDedicatoria = ""

            if not esRecogidaTienda and str(order["gift"]) == "None":
                impAlbaran = False

            if str(order["gift"]) != "None":
                if "gift_message_id" in order["gift"]:
                    impDedicatoria = True
                    esRegalo = True
                    emisor = str(order["gift"]["sender"])
                    receptor = str(order["gift"]["recipient"])
                    mensajeDedicatoria = str(order["gift"]["message"])

            if not esRecogidaTienda:
                if "country_id" in order["shipping_address"]:
                    if str(order["shipping_address"]["country_id"]) == "ES":
                        if "region_id" in order["shipping_address"]:
                                esProvinciaFactura = qsatype.FLUtil.sqlSelect("provincias", "imprimirfactura", "mg_idprovincia = " + str(order["shipping_address"]["region_id"]))
                                if esProvinciaFactura:
                                    impFactura = True
                    else:
                        imprimirFacturaPais = qsatype.FLUtil.sqlSelect("paises", "imprimirfactura", "codiso = '" + str(order["shipping_address"]["country_id"]) + "'")
                        if imprimirFacturaPais:
                            impFactura = True

            if not qsatype.FLUtil.execSql("INSERT INTO idl_ecommerce (idtpv_comanda,codcomanda,tipo,transportista,metodoenvioidl,imprimiralbaran,imprimirfactura,imprimirdedicatoria,emisor,receptor,mensajededicatoria,esregalo,facturaimpresa,envioidl,numseguimientoinformado,confirmacionenvio) VALUES ('" + str(curComanda.valueBuffer("idtpv_comanda")) + "', '" + str(curComanda.valueBuffer("codigo")) + "', 'VENTA', '" + str(transIDL) + "','" + str(metodoIDL) + "','" + str(impAlbaran) + "','" + str(impFactura) + "','" + str(impDedicatoria) + "','" + str(emisor) + "','" + str(receptor) + "','" + str(mensajeDedicatoria) + "','" + str(esRegalo) + "',false,false,false,'No')"):
                return False

            return True

        except Exception as e:
            qsatype.debug(e)
            return False

    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)

    def getUnsynchronizedOrders(self):
        return self.ctx.elganso_sync_getUnsynchronizedOrders()

    def processOrders(self, orders):
        return self.ctx.elganso_sync_processOrders(orders)

    def creaCabeceraComanda(self, order, codigo):
        return self.ctx.elganso_sync_creaCabeceraComanda(order, codigo)

    def creaLineaEnvio(self, order, curComanda):
        return self.ctx.elganso_sync_creaLineaEnvio(order, curComanda)

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

    def creaLineaGastosComanda(self, curComanda, gastos, iva):
        return self.ctx.elganso_sync_creaLineaGastosComanda(curComanda, gastos, iva)

    def creaLineaDescuento(self, curComanda, dto, iva):
        return self.ctx.elganso_sync_creaLineaDescuento(curComanda, dto, iva)

    def creaLineaVale(self, curComanda, objVale, iva):
        return self.ctx.elganso_sync_creaLineaVale(curComanda, objVale, iva)

    def cerrarVentaWeb(self, curComanda):
        return self.ctx.elganso_sync_cerrarVentaWeb(curComanda)

    def crearArqueoVentaWeb(self, curComanda):
        return self.ctx.elganso_sync_crearArqueoVentaWeb(curComanda)

    def crearPagoVentaWeb(self, curComanda, idArqueo):
        return self.ctx.elganso_sync_crearPagoVentaWeb(curComanda, idArqueo)

    def masDatosArqueo(self, curArqueo, curComanda):
        return self.ctx.elganso_sync_masDatosArqueo(curArqueo, curComanda)

    def obtenerCodFactura(self):
        return self.ctx.elganso_sync_obtenerCodFactura()

    def crearRegistroECommerce(self, order, curComanda):
        return self.ctx.elganso_sync_crearRegistroECommerce(order, curComanda)


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
