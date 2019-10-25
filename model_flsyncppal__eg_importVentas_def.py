# @class_declaration interna #
from django.db import transaction
from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from models.flsyncppal import flsyncppal_def as syncppal
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
class elganso_sync(interna):

    @transaction.atomic
    def elganso_sync_getVentasTienda(self, codTienda):
        proceso = 'egsyncvt' + codTienda
        cdSmall = 10
        cdLarge = 180

        cx = self.iface.creaConexion(codTienda)
        print(cx)
        if not cx:
            print("Error. No se pudo conectar con la tienda " + codTienda.upper())
            syncppal.iface.log("Error. No se pudo conectar con la tienda " + codTienda.upper(), proceso)
            return cdLarge

        print("antes comprobar conexion")
        if not self.iface.comprobarConexion(codTienda, cx, proceso):
            return cdLarge

        print("despues comprobar conexion")
        oMtd = self.iface.dameMetadatosVentas(codTienda, cx, proceso)
        print(oMtd)

        listaLafayette = qsatype.FactoriaModulos.get('flfact_tpv').iface.tiendasEmpresaLafayette()
        wComandas = "NOT sincronizada AND tipodoc <> 'PRESUPUESTO' AND estado <> 'Abierta' AND codigo NOT LIKE '#%' AND ((codtienda not in (" + listaLafayette + ") and fecha >= '2018-07-01'))"
        print("wComandas " + str(wComandas))
        print("antes obtener comanda")
        codComanda = self.iface.dameComandaTienda(codTienda, wComandas, cx, proceso)
        # codComanda = self.iface.dameComandaTienda(codTienda, wComandas, cx, proceso)
        print("despues obtener comanda " + str(codComanda))
        ventasSincro = ""
        numVentas = 0
        while codComanda:
            print("while " + codComanda)
            wComandas += " AND codigo <> '" + codComanda + "'"
            oComanda = self.iface.cargaComandaTienda(codComanda, codTienda, oMtd, cx, proceso)
            print(oComanda)
            if not oComanda:
                wComandas += " AND codigo <> '" + codComanda + "'"
                codComanda = self.iface.dameComandaTienda(codTienda, wComandas, cx, proceso)
                continue
            if not self.iface.guardarVentaEnCentral(oComanda, codComanda, codTienda):
                print("Error. No se pudo guardar la venta " + codComanda + " en la central")
                syncppal.iface.log("Error. No se pudo guardar la venta " + codComanda + " en la central", proceso)
                self.iface.cierraConexion(cx)
                return cdLarge

            if ventasSincro != "":
                ventasSincro = ventasSincro + ","
            ventasSincro = ventasSincro + "'" + codComanda + "'"
            numVentas = numVentas + 1

            codComanda = self.iface.dameComandaTienda(codTienda, wComandas, cx, proceso)
            self.iface.marcarVentasSincronizadas(cx, ventasSincro, codTienda, proceso)

        self.iface.actualizarEsquemaSincroObjeto(codTienda)
        if numVentas > 0:
            syncppal.iface.log("Éxito. " + str(numVentas) + " ventas sincronizadas con éxito para la tienda " + codTienda.upper(), proceso)
        else:
            syncppal.iface.log("Éxito. No hay ventas que sincronizar para la tienda " + codTienda.upper(), proceso)
            self.iface.cierraConexion(cx)
            return cdLarge

        print("FINN")
        self.iface.cierraConexion(cx)
        return cdSmall

    def elganso_sync_dameComandaTienda(self, codTienda, wComandas, cx, proceso):
        print("elganso_sync_dameComandaTienda")
        try:
            cx["cur"].execute("select codigo from tpv_comandas where codtienda = '" + codTienda.upper() + "' AND " + wComandas)
        except Exception as e:
            print("Error. " + codTienda.upper() + " No se pudo obtener la siguiente venta (" + str(e) + ")")
            syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo obtener la siguiente venta (" + str(e) + ")", proceso)
            return False

        print("despues del try")
        rows = cx["cur"].fetchall()
        if len(rows) > 0:
            for p in rows:
                return p["codigo"]

        return False

    def elganso_sync_marcarVentasSincronizadas(self, cx, ventasSincro, codTienda, proceso):
        if ventasSincro == "":
            return True

        ventas = ventasSincro.split(",")
        for venta in ventas:
            if qsatype.FLUtil.sqlSelect("so_comandassincro", "codigo", "codigo = " + venta):
                try:
                    cx["cur"].execute("UPDATE tpv_comandas SET sincronizada = true where codigo = " + venta)
                except Exception as e:
                    print("Error. " + codTienda.upper() + " No se pudo marcar la venta sincronizada (" + str(e) + ")")
                    syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo marcar la venta sincronizada (" + str(e) + ")", proceso)
                    return False

                cx["conn"].commit()
            else:
                syncppal.iface.log("Info. La venta " + venta[1:12] + " no se marcó sincronizada en la tienda porque no se encontró en la central", proceso)

        return True

    def elganso_sync_guardarVentaEnCentral(self, oComanda, codComanda, codTienda):
        datos = str(oComanda)
        if not qsatype.FLUtil.sqlSelect("empresa", "id", "1=1", "empresa"):
            syncppal.iface.log("Error. No hay conexión con la central", proceso)
            return False

        curCS = qsatype.FLSqlCursor("so_comandassincro")
        curCS.setModeAccess(curCS.Insert)
        curCS.refreshBuffer()
        curCS.setValueBuffer("datos", datos)
        curCS.setValueBuffer("codigo", codComanda)
        curCS.setValueBuffer("codtienda", codTienda.upper())
        curCS.setValueBuffer("estado", "PTE")
        curCS.setValueBuffer("fecha", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameFechaActual())
        curCS.setValueBuffer("hora", qsatype.FactoriaModulos.get('flfactppal').iface.pub_dameHoraActual())
        if not curCS.commitBuffer():
            return False

        return True

    def elganso_sync_actualizarEsquemaSincroObjeto(self, codTienda):
        idSincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "codtienda = '" + codTienda.upper() + "' AND esquema = 'SINCRO_OBJETO'")
        print(idSincro)
        if idSincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = CURRENT_DATE, horasincro = CURRENT_TIME WHERE codtienda = '" + codTienda.upper() + "' AND esquema = 'SINCRO_OBJETO'")
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda,esquema,fechasincro,horasincro) VALUES ('" + codTienda.upper() + "','SINCRO_OBJETO',CURRENT_DATE,CURRENT_TIME)")
        return True

    def elganso_sync_dameMetadatosVentas(self, codTienda, cx, proceso):
        print("elganso_sync_dameMetadatosVentas")
        oMtd = {"tpv_comandas": False, "tpv_lineascomanda": False, "tpv_pagoscomanda": False, "eg_motivosdevolucion": False}
        for t in oMtd:
            print(t)
            oMtd[t] = self.iface.cargaCamposTabla(t, codTienda, cx, proceso)

        print("fin")
        return oMtd

    def elganso_sync_cargaCamposTabla(self, t, codTienda, cx, proceso):
        print("hola")
        try:
            cx["cur"].execute("select column_name from information_schema.columns where table_name = '" + t + "'")
        except Exception as e:
            print("Error. " + codTienda.upper() + " No se pudo obtener los metadatos para " + t + " (" + str(e) + ")")
            syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo obtener los metadatos para " + t + " (" + str(e) + ")", proceso)
            return False

        print("consulta ejecutada")
        aCamposMtd = []
        rows = cx["cur"].fetchall()
        if len(rows) > 0:
            for p in rows:
                campo = p["column_name"]
                if t == "tpv_comandas":
                    if campo == "idtpv_comanda" or campo == "idfactura" or campo == "egidfacturarec" or campo == "idprovincia":
                        continue
                elif t == "tpv_lineascomanda":
                    if campo == "idtpv_comanda" or campo == "idtpv_linea":
                        continue
                elif t == "tpv_pagoscomanda":
                    if campo == "idtpv_comanda" or campo == "idpago" or campo == "idasiento":
                        continue
                elif t == "eg_motivosdevolucion":
                    if campo == "id":
                        continue
                aCamposMtd.append(campo)

        return aCamposMtd

    def elganso_sync_cargaComandaTienda(self, codComanda, codTienda, oMtd, cx, proceso):
        oComanda = {"cabecera": False, "lineas": [], "pagos": [], "motivos": []}

        print("ventas")
        aCamposC = oMtd["tpv_comandas"]
        oComanda["cabecera"] = False
        try:
            cx["cur"].execute("select idtpv_comanda, " + ", ".join(aCamposC) + " from tpv_comandas where codigo = '" + codComanda + "'")
        except Exception as e:
            print("Error. " + codTienda.upper() + " No se pudieron obtener los datos de ventas (" + str(e) + ")")
            syncppal.iface.log("Error. " + codTienda.upper() + " No se pudieron obtener los datos de ventas (" + str(e) + ")", proceso)
            return False

        rows = cx["cur"].fetchall()
        if len(rows) > 0:
            p = rows[0]
            idComanda = p["idtpv_comanda"]

            object = self.iface.cargaObjDeQuery(p, aCamposC)
            if not object:
                print("Error. " + codTienda.upper() + " No se pudo cargar el objeto de ventas (" + str(e) + ")")
                syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo cargar el objeto de ventas (" + str(e) + ")", proceso)
                return False
            oComanda["cabecera"] = object

        print("Lineas")
        aCamposL = oMtd["tpv_lineascomanda"]
        oComanda["lineas"] = []
        try:
            cx["cur"].execute("select " + ", ".join(aCamposL) + " from tpv_lineascomanda where idtpv_comanda = " + str(idComanda))
        except Exception as e:
            print("Error. " + codTienda.upper() + " No se pudieron obtener los datos de líneas de venta (" + str(e) + ")")
            syncppal.iface.log("Error. " + codTienda.upper() + " No se pudieron obtener los datos de líneas de venta (" + str(e) + ")", proceso)
            return False

        rows = cx["cur"].fetchall()
        for p in rows:
            object = self.iface.cargaObjDeQuery(p, aCamposL)
            if not object:
                print("Error. " + codTienda.upper() + " No se pudo cargar el objeto de líneas de venta (" + str(e) + ")")
                syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo cargar el objeto de líneas de venta (" + str(e) + ")", proceso)
                return False
            oComanda["lineas"].append(object)

        print("pagos")
        aCamposP = oMtd["tpv_pagoscomanda"]
        oComanda["pagos"] = []
        try:
            cx["cur"].execute("select " + ", ".join(aCamposP) + " from tpv_pagoscomanda where idtpv_comanda = " + str(idComanda))
        except Exception as e:
            print("Error. " + codTienda.upper() + " No se pudieron obtener los datos de pagos de venta (" + str(e) + ")")
            syncppal.iface.log("Error. " + codTienda.upper() + " No se pudieron obtener los datos de pagos de venta (" + str(e) + ")", proceso)
            return False

        rows = cx["cur"].fetchall()
        for p in rows:
            object = self.iface.cargaObjDeQuery(p, aCamposP)
            if not object:
                print("Error. " + codTienda.upper() + " No se pudo cargar el objeto de pagos de venta (" + str(e) + ")")
                syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo cargar el objeto de pagos de venta (" + str(e) + ")", proceso)
                return False
            oComanda["pagos"].append(object)

        print("motivos")
        aCamposM = oMtd["eg_motivosdevolucion"]
        oComanda["motivos"] = []
        try:
            cx["cur"].execute("select " + ", ".join(aCamposM) + " from eg_motivosdevolucion where codcomandadevol = '" + codComanda + "'")
        except Exception as e:
            print("Error. " + codTienda.upper() + " No se pudieron obtener los datos de motivos de devolución (" + str(e) + ")")
            syncppal.iface.log("Error. " + codTienda.upper() + " No se pudieron obtener los datos de motivos de devolución (" + str(e) + ")", proceso)
            return False

        rows = cx["cur"].fetchall()
        for p in rows:
            object = self.iface.cargaObjDeQuery(p, aCamposM)
            if not object:
                print("Error. " + codTienda.upper() + " No se pudo cargar el objeto de motivos de devolución (" + str(e) + ")")
                syncppal.iface.log("Error. " + codTienda.upper() + " No se pudo cargar el objeto de motivos de devolución (" + str(e) + ")", proceso)
                return False
            oComanda["motivos"].append(object)

        return oComanda

    def elganso_sync_cargaObjDeQuery(self, datos, aCampos):
        obj = {}

        for campo in aCampos:
            print(campo)
            valor = datos[campo]
            if valor is None:
                valor = ""

            if campo == "fecha" or campo == "fechasincro" or campo == "hora":
                valor = str(valor)

            if campo == "ptesincrofactura":
                valor = "true"

            if str(valor) == "True" or str(valor) == "False":
                valor = str(valor).lower()

            obj[campo] = valor

        return obj

    def elganso_sync_creaConexion(self, codTienda):
        cx = {}
        datosCX = self.iface.dameDatosConexion(codTienda)
        cx["conn"] = self.iface.conectaBd(datosCX)
        if not cx["conn"]:
            return False

        cx["cur"] = cx["conn"].cursor(cursor_factory=RealDictCursor)

        return cx

    def elganso_sync_conectaBd(self, datosCX):
        try:
            return psycopg2.connect(datosCX)

        except Exception as e:
            print("No pudo conectar con BBDD")
            print(e)
            return False

    def elganso_sync_cierraConexion(self, cx):
        if cx["cur"]:
            cx["cur"].close()
        if cx["conn"]:
            cx["conn"].close()

    def elganso_sync_dameDatosConexion(self, codTienda):
        datosCX = ""
        qCampos = qsatype.FLSqlQuery("")
        qCampos.setSelect("usuario,nombrebd,contrasena,puerto,servidor")
        qCampos.setFrom("tpv_tiendas")
        qCampos.setWhere("codtienda = '" + codTienda.upper() + "'")

        if not qCampos.exec_():
            return False

        if not qCampos.first():
            return False

        datosCX = "user='" + qCampos.value("usuario") + "' password='" + qCampos.value("contrasena") + "' dbname='" + qCampos.value("nombrebd") + "' host='" + qCampos.value("servidor") + "' port='" + qCampos.value("puerto") + "'"

        return datosCX

    def elganso_sync_comprobarConexion(self, codTienda, cx, proceso):
        try:
            cx["cur"].execute("SELECT id FROM empresa WHERE 1=1")
        except Exception as e:
            print("Error. No hay conexión con la tienda " + codTienda.upper() + " (" + str(e) + ")")
            syncppal.iface.log("Error. No hay conexión con la tienda " + codTienda.upper() + " (" + str(e) + ")", proceso)
            return False

        return True

    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)

    def getVentasTienda(self, codTienda):
        return self.ctx.elganso_sync_getVentasTienda(codTienda)

    def guardarVentaEnCentral(self, oComanda, codComanda, codTienda):
        return self.ctx.elganso_sync_guardarVentaEnCentral(oComanda, codComanda, codTienda)

    def marcarVentasSincronizadas(self, cx, ventasSincro, codTienda, proceso):
        return self.ctx.elganso_sync_marcarVentasSincronizadas(cx, ventasSincro, codTienda, proceso)

    def actualizarEsquemaSincroObjeto(self, codTienda):
        return self.ctx.elganso_sync_actualizarEsquemaSincroObjeto(codTienda)

    def dameMetadatosVentas(self, codTienda, cx, proceso):
        return self.ctx.elganso_sync_dameMetadatosVentas(codTienda, cx, proceso)

    def cargaCamposTabla(self, t, codTienda, cx, proceso):
        return self.ctx.elganso_sync_cargaCamposTabla(t, codTienda, cx, proceso)

    def cargaComandaTienda(self, codComanda, codTienda, oMtd, cx, proceso):
        return self.ctx.elganso_sync_cargaComandaTienda(codComanda, codTienda, oMtd, cx, proceso)

    def cargaObjDeQuery(self, datos, aCampos):
        return self.ctx.elganso_sync_cargaObjDeQuery(datos, aCampos)

    def creaConexion(self, codTienda):
        return self.ctx.elganso_sync_creaConexion(codTienda)

    def conectaBd(self, datosCX):
        return self.ctx.elganso_sync_conectaBd(datosCX)

    def cierraConexion(self, cx):
        return self.ctx.elganso_sync_cierraConexion(cx)

    def dameDatosConexion(self, codTienda):
        return self.ctx.elganso_sync_dameDatosConexion(codTienda)

    def comprobarConexion(self, codTienda, cx, proceso):
        return self.ctx.elganso_sync_comprobarConexion(codTienda, cx, proceso)

    def dameComandaTienda(self, codTienda, wComandas, cx, poroceso):
        return self.ctx.elganso_sync_dameComandaTienda(codTienda, wComandas, cx, poroceso)


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
