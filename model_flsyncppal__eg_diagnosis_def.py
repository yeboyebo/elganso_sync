# @class_declaration interna #
import datetime
import json
import requests
import http.client

from celery.task import periodic_task
from celery.schedules import crontab

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal import flsyncppal_def as syncppal
from models.flsyncppal import eg_importVentas_def as importVentas


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
class elganso_sync(interna):

    @periodic_task(run_every=crontab(minute='30', hour='5'))
    def elganso_sync_diagsincroventasobjeto():
        proceso = "diagsincroventasobjeto"
        try:
            whereFijo = "sincroactiva AND servidor IS NOT NULL"
            tiendas = "'" + "','".join(qsatype.FactoriaModulos.get('formtpv_tiendas').iface.dameTiendasSincro("NOCORNER").split(",")) + "'"

            #tiendas = "'ACOR'"
           
            q = qsatype.FLSqlQuery()
            q.setSelect("codtienda")
            q.setFrom("tpv_tiendas")
            q.setWhere(whereFijo + " AND codtienda IN (" + tiendas + ")")

            if not q.exec_():
                 syncppal.iface.log("Error. Falló la consulta de tiendas de sincro de ventas objeto.", proceso)
                 return False

            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            while q.next():
                codTienda = q.value("codtienda")
                cx = importVentas.iface.creaConexion(codTienda)
                if not cx:
                    syncppal.iface.log("Info. No se pudo conectar con la tienda " + codTienda.upper(), proceso)
                    continue

                if not importVentas.iface.comprobarConexion(codTienda, cx, proceso):
                    syncppal.iface.log("Info. No se pudo conectar con la tienda " + codTienda.upper(), proceso)
                    continue

                cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas WHERE ((fecha >= CURRENT_DATE-7 AND fecha < CURRENT_DATE) OR (fecha = CURRENT_DATE AND hora < (CURRENT_TIME + (-60 * interval '1 minute')))) AND codtienda = '" + codTienda + "'")
                rows = cxC["cur"].fetchall()
                if len(rows) > 0:
                    for p in rows:
                        ventasC = p["ventas"]

                cx["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas WHERE ((fecha >= CURRENT_DATE-7 AND fecha < CURRENT_DATE) OR (fecha = CURRENT_DATE AND hora < (CURRENT_TIME + (-60 * interval '1 minute')))) AND codtienda = '" + codTienda + "'")
                rows = cx["cur"].fetchall()
                if len(rows) > 0:
                    for p in rows:
                        ventasT = p["ventas"]

                if ventasC != ventasT:
                    hayError = True
                    syncppal.iface.log("Error. " + codTienda + ": Num Ventas Central: " +str(ventasC) + " Tienda: " + str(ventasT), proceso)

                cxC["cur"].execute("SELECT count(*) AS lineas FROM tpv_lineascomanda WHERE codtienda = '" + codTienda + "' AND idtpv_comanda IN (SELECT idtpv_comanda FROM tpv_comandas WHERE (fecha >= CURRENT_DATE-7 AND fecha < CURRENT_DATE) OR (fecha = CURRENT_DATE AND hora < (CURRENT_TIME + (-60 * interval '1 minute'))))")
                rows = cxC["cur"].fetchall()
                if len(rows) > 0:
                    for p in rows:
                        lineasC = p["lineas"]

                cx["cur"].execute("SELECT count(*) AS lineas FROM tpv_lineascomanda WHERE codtienda = '" + codTienda + "' AND idtpv_comanda IN (SELECT idtpv_comanda FROM tpv_comandas WHERE (fecha >= CURRENT_DATE-7 AND fecha < CURRENT_DATE) OR (fecha = CURRENT_DATE AND hora < (CURRENT_TIME + (-60 * interval '1 minute'))))")
                rows = cx["cur"].fetchall()
                if len(rows) > 0:
                    for p in rows:
                        lineasT = p["lineas"]

                if lineasC != lineasT:
                    hayError = True
                    syncppal.iface.log("Error. " + codTienda + ": Num Lineas Central: " +str(lineasC) + " Tienda: " + str(lineasT), proceso)

                cxC["cur"].execute("SELECT count(*) AS pagos FROM tpv_pagoscomanda WHERE codtienda = '" + codTienda + "' AND idtpv_comanda IN (SELECT idtpv_comanda FROM tpv_comandas WHERE (fecha >= CURRENT_DATE-7 AND fecha < CURRENT_DATE) OR (fecha = CURRENT_DATE AND hora < (CURRENT_TIME + (-60 * interval '1 minute'))))")
                rows = cxC["cur"].fetchall()
                if len(rows) > 0:
                    for p in rows:
                        pagosC = p["pagos"]

                cx["cur"].execute("SELECT count(*) AS pagos FROM tpv_pagoscomanda WHERE codtienda = '" + codTienda + "' AND idtpv_comanda IN (SELECT idtpv_comanda FROM tpv_comandas WHERE (fecha >= CURRENT_DATE-7 AND fecha < CURRENT_DATE) OR (fecha = CURRENT_DATE AND hora < (CURRENT_TIME + (-60 * interval '1 minute'))))")
                rows = cx["cur"].fetchall()
                if len(rows) > 0:
                    for p in rows:
                        pagosT = p["pagos"]

                if pagosC != pagosT:
                    hayError = True
                    syncppal.iface.log("Error. " + codTienda + ": Num Pagos Central: " +str(pagosC) + " Tienda: " + str(pagosT), proceso)

            if not hayError:
                syncppal.iface.log("Éxito. Están todas las ventas sincroizadas correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de sincro de ventas objeto", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='45', hour='5'))
    def elganso_sync_diagidlerroneos():
        proceso = "diagidlerroneos"
        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT count(*) AS errores FROM idl_erroneos")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["errores"] > 0:
                    syncppal.iface.log("Error. Hay registros en idl_erroneos", proceso)
                else:
                    syncppal.iface.log("Éxito. Envíos a idl correctos", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de idl erroneos", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='46', hour='5'))
    def elganso_sync_diagventastiendaficticia():
        proceso = "diagventastiendaficticia"
        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_arqueos a INNER JOIN tpv_pagoscomanda p ON a.idtpv_arqueo = p.idtpv_arqueo INNER JOIN eg_ventaslafayette vf ON p.idtpv_comanda = vf.idcomanda WHERE a.diadesde >= CURRENT_DATE-7 AND a.idtpv_arqueo LIKE 'LF%' AND p.importe >= 0 GROUP BY vf.codtiendalf")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["ventas"] > 0:
                    syncppal.iface.log("Error. Hay " + str(rows[0]["ventas"]) + " ventas en Lafayette ficticio", proceso)
                    hayError = True

            cxC["cur"].execute("SELECT COUNT(*) AS ventas FROM tpv_arqueos a INNER JOIN tpv_pagoscomanda p ON a.idtpv_arqueo = p.idtpv_arqueo INNER JOIN eg_ventaseci vc ON p.idtpv_comanda = vc.idcomanda WHERE a.diadesde >= CURRENT_DATE-7 AND a.idtpv_arqueo LIKE 'CF%' AND p.importe >= 0 GROUP BY vc.codtiendaeci")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["ventas"] > 0:
                    syncppal.iface.log("Error. Hay " + str(rows[0]["ventas"]) + " ventas en ECI ficticio", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. No hay ventas en tiendas ficticias", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de ventas en tiendas ficticias", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='47', hour='5'))
    def elganso_sync_diagventassinlineas():
        proceso = "diagventassinlineas"
        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT c.codigo AS codigo FROM tpv_comandas c LEFT OUTER JOIN tpv_lineascomanda p ON c.idtpv_comanda = p.idtpv_comanda WHERE c.fecha >= '2019-05-01' AND c.total <> 0 AND p.idtpv_linea IS NULL AND c.codtienda <> 'PROD'")
            rows = cxC["cur"].fetchall()
            codigos = ""
            if len(rows) > 0:
                for p in rows:
                    if codigos != "":
                        codigos += ", "
                    codigos += p["codigo"]

                syncppal.iface.log("Error. Hay ventas sin líneas: " + codigos, proceso)
            else:
                syncppal.iface.log("Éxito. No hay ventas sin líneas", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de ventas sin líneas", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='50', hour='5'))
    def elganso_sync_diagventassinpagos():
        proceso = "diagventassinpagos"
        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT c.codigo AS codigo FROM tpv_comandas c LEFT OUTER JOIN tpv_pagoscomanda p ON c.idtpv_comanda = p.idtpv_comanda WHERE c.fecha >= '2019-05-01' AND c.total <> 0 AND p.idpago IS NULL AND c.codtienda <> 'PROD' AND c.codigo NOT LIKE 'WDV%' AND c.codigo NOT LIKE 'EDV%'")
            rows = cxC["cur"].fetchall()
            codigos = ""
            if len(rows) > 0:
                for p in rows:
                    if codigos != "":
                        codigos += ", "
                    codigos += p["codigo"]

                syncppal.iface.log("Error. Hay ventas sin pagos: " + codigos, proceso)
            else:
                syncppal.iface.log("Éxito. No hay ventas sin pagos", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de ventas sin pagos", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='22', hour='6'))
    def elganso_sync_diagdirectordersnoidl():
        proceso = "diagdirectordersnoidl"
        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT c.codigo AS codigo, c.idtpv_comanda AS idcomanda, c.codpais AS pais from tpv_comandas c left outer join idl_ecommerce e on c.idtpv_comanda = e.idtpv_comanda where c.fecha >= '2019-10-01' and c.egcodpedidoweb is not null and c.egcodpedidoweb like date_part('year', CURRENT_DATE) || '%' and e.id is null")
            rows = cxC["cur"].fetchall()
            codigos = ""
            if len(rows) > 0:
                for p in rows:
                    if codigos != "":
                        codigos += ", "
                    codigos += str(p["codigo"]) + "-" + str(p["idcomanda"]) + "-" + str(p["pais"])

                syncppal.iface.log("Error. Hay direct orders sin enviar a idl: " + codigos, proceso)
            else:
                syncppal.iface.log("Éxito. No hay direct orders sin enviar a idl", proceso)

        except Exception as e:
            print(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de direct orders sin enviar a idl", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='0', hour='6'))
    def elganso_sync_diagfacturaseci():
        proceso = "diagfacturaseci"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            # cxC["cur"].execute("SELECT valor FROM param_parametros WHERE nombre = 'FECHA_FACTURAS_ECI'")
            # rows = cxC["cur"].fetchall()
            # if len(rows) <= 0:
            #     syncppal.iface.log("Error. No se pudo obtener la fecha de diagnóstico de facturación ECI", proceso)
            #     return False

            # fecha = rows[0]["valor"]
            cxC["cur"].execute("SELECT count(*) AS facturas FROM facturascli WHERE facturascli.codcliente IN ('001039','010683') AND facturascli.total > 0 AND facturascli.enviadoeciedicom = false AND facturascli.codeci IS NOT NULL AND facturascli.codeci <> '' AND facturascli.pedidoeci IS NOT NULL AND facturascli.pedidoeci <> '' AND facturascli.albaraneci IS NOT NULL AND facturascli.albaraneci <> '' AND facturascli.departamentoeci IS NOT NULL AND facturascli.departamentoeci <> '' AND facturascli.codejercicio IN ('2018','2019','2020','2021','2022','2023','2024','2025') GROUP BY facturascli.enviadoeciedicom")
              
            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                for p in rows:
                    if p["facturas"] > 0:     
                        syncppal.iface.log("Error. Hay " + str(p["facturas"]) + " facturas ECI sin enviar a EDICOM", proceso)
                    else:
                        syncppal.iface.log("Éxito. No hay facturas ECI sin enviar a EDICOM", proceso)
            else:
                syncppal.iface.log("Éxito. No hay facturas ECI sin enviar a EDICOM", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de facturación ECI", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='15', hour='11'))
    def elganso_sync_diagcontabilidad():
        proceso = "diagcontabilidad"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT count(*) AS arqueos from tpv_arqueos ar INNER JOIN tpv_tiendas t ON ar.codtienda = t.codtienda INNER JOIN empresa e ON e.id = t.idempresa WHERE e.contintegrada AND ar.diadesde >= '2019-01-01' AND diadesde < CURRENT_DATE AND ar.idasiento is null AND t.sincroactiva AND t.codtienda NOT IN ('PROD','EVEN','EVE2')")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                if rows[0]["arqueos"] > 0:
                    syncppal.iface.log("Error. Hay arqueos sin sincronizar", proceso)
                else:
                    syncppal.iface.log("Éxito. Arqueos sincronizados correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico sincronización de arqueos", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='0', hour='12'))
    def elganso_sync_diagventaseci():
        proceso = "diagventaseci"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas c INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda WHERE c.fecha = CURRENT_DATE-7 AND t.idempresa = 15")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                if rows[0]["ventas"] <= 0:
                    syncppal.iface.log("Error. No se han sincronizado las ventas ECI", proceso)
                else:
                    syncppal.iface.log("Éxito. Ventas ECI sincronizadas correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico sincronización de ventas ECI", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='30', hour='11'))
    def elganso_sync_diagventassinfacturar():
        proceso = "diagventassinfacturar"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas c LEFT OUTER JOIN facturascli f ON c.egcodfactura = f.codigo INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda INNER JOIN empresa e ON t.idempresa = e.id LEFT OUTER JOIN idl_ecommercedevoluciones d ON c.codigo = d.codcomanda WHERE c.fecha >= CURRENT_DATE - 15 AND c.fecha <= CURRENT_DATE - 1 AND c.codtienda = 'AWEB' AND e.contintegrada AND f.idfactura is NULL AND c.codigo NOT LIKE '#%' AND NOT (c.codigo LIKE 'WDV%' AND c.total = 0) AND (d.confirmacionrecepcion = 'Si' OR d.confirmacionrecepcion IS NULL) AND c.estado = 'Cerrada'")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                if rows[0]["ventas"] > 0:
                    syncppal.iface.log("Error. Hay ventas Web sin facturar", proceso)
                    hayError = True

            cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas c LEFT OUTER JOIN facturascli f ON c.egcodfactura = f.codigo INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda INNER JOIN empresa e ON t.idempresa = e.id WHERE c.fecha >= CURRENT_DATE - 15 AND c.fecha <= CURRENT_DATE - 1 AND c.codtienda <> 'AWEB' AND e.contintegrada AND e.id = 1 AND f.idfactura is NULL AND (c.idfactura IS NULL OR c.idfactura = 0) AND c.codigo NOT LIKE 'PROD%'")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                if rows[0]["ventas"] > 0:
                    syncppal.iface.log("Error. Hay ventas Nacionales sin facturar", proceso)
                    hayError = True

            cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas c LEFT OUTER JOIN facturascli f ON c.egcodfactura = f.codigo INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda INNER JOIN empresa e ON t.idempresa = e.id WHERE c.fecha >= CURRENT_DATE - 15 AND c.fecha <= CURRENT_DATE - 1 AND c.codtienda <> 'AWEB' AND e.contintegrada AND e.id <> 1 AND f.idfactura is NULL")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                if rows[0]["ventas"] > 0:
                    syncppal.iface.log("Error. Hay ventas Internacionales sin facturar", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Ventas facturadas correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de ventas sin facturar", proceso)
            return False

        return True

    @periodic_task(run_every=crontab(minute='10', hour='6'))
    def elganso_sync_diagfacturacionsii():
        proceso = "diagfacturacionsii"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT count(*) AS sii FROM sii_presentaciones WHERE hora < '06:00:00' AND fecha = CURRENT_DATE AND estado = 'ABIERTA'")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                if rows[0]["sii"] <= 0:
                    syncppal.iface.log("Error. No se ha generado la presentación al SII", proceso)
                else:
                    syncppal.iface.log("Éxito. Generación del SII correcta", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de la generación del SII", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='11', hour='6'))
    def elganso_sync_diagfichprocesados():
        proceso = "diagfichprocesados"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            
            cxC["cur"].execute("SELECT count(*) AS error FROM eg_fichprocesados WHERE estado = 'Error' AND fecha >= CURRENT_DATE-1")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["error"] > 0:
                    syncppal.iface.log("Error. Hay " + str(rows[0]["error"]) + " registros en eg_fichprocesados en estado Error", proceso)
                    hayError = True
            
            cxC["cur"].execute("SELECT count(*) AS proceso FROM eg_fichprocesados WHERE estado = 'En proceso' AND fecha >= CURRENT_DATE-1")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["proceso"] > 0:
                    syncppal.iface.log("Error. Hay " + str(rows[0]["proceso"]) + " registros en eg_fichprocesados en estado En proceso", proceso)
                    hayError = True

            cxC["cur"].execute("SELECT count(*) as pte FROM eg_fichprocesados WHERE estado = 'PTE'")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["pte"] > 0:
                    syncppal.iface.log("Error. Hay " + str(rows[0]["pte"]) + " registros en eg_fichprocesados en estado PTE", proceso)
                    hayError = True

            cxC["cur"].execute("SELECT tipo FROM eg_fichprocesados WHERE tipo LIKE 'IDL%' OR tipo IN ('PWS','TWS','RWS','ECO','WDV','FAL','AJS')")
            rows = cxC["cur"].fetchall()

            if len(rows) > 0:
                tipos = ""
                for p in rows:
                    if tipos != "":
                        tipos += ", "
                    tipos += p["tipo"]

                if tipos != "":
                    syncppal.iface.log("Error. Hay registros en eg_fichprocesados para los tipos: " + tipos, proceso)
                    hayError = True

            if not hayError:  
                syncppal.iface.log("Éxito. Registros en ficheros procesados correctos", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de ficheros procesados", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='20', hour='6'))
    def elganso_sync_diagmovimientosviajes():
        proceso = "diagmovimientosviajes"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS mov FROM eg_lineasptesmovistock WHERE 1=1")

            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["mov"] > 0:
                    syncppal.iface.log("Error. Hay líneas pendientes de movimientos de viajes", proceso)
                    hayError = True

            cxC["cur"].execute("SELECT count(*) AS viajes FROM tpv_lineasmultitransstock l INNER JOIN movistock m ON (m.idlineatto = l.idlinea OR m.idlineattd = l.idlinea) INNER JOIN stocks s ON s.idstock = m.idstock WHERE l.estado = 'RECIBIDO' AND s.codalmacen LIKE 'TR%' AND l.fecharx >= '2019-10-01' AND l.fecharx < CURRENT_DATE GROUP BY l.idviajemultitrans, l.fecharx HAVING SUM(m.cantidad) <> 0")

            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["viajes"] > 0:
                    syncppal.iface.log("Error. Hay movimientos en tránsito", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Movimientos de viajes corectos", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de movimientos de viajes", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='25', hour='6'))
    def elganso_sync_diagpedidosservidoseditables():
        proceso = "diagpedidosservidoseditables"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            cxC["cur"].execute("SELECT COUNT(*) as pedidos FROM pedidoscli WHERE servido LIKE 'S%' AND editable")

            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["pedidos"] > 0:
                    syncppal.iface.log("Error. Hay pedidos de cliente servidos y editables", proceso)
                else:
                    syncppal.iface.log("Éxito. Pedidos de cliente servidos correctos", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de pedidos de cliente servidos", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='30', hour='6'))
    def elganso_sync_diagarticulosidl():
        proceso = "diagarticulosidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS articulos FROM articulos a INNER JOIN idl_articulos idla ON (a.referencia = idla.referencia AND idla.referencia IN (SELECT referencia FROM idl_articulos WHERE ok = false AND idlog is NULL AND referencia NOT LIKE '(C)%' ORDER BY referencia ASC LIMIT 20)) INNER JOIN atributosarticulos at ON a.referencia = at.referencia INNER JOIN articulosprov ap ON a.referencia = ap.referencia INNER JOIN proveedores p ON a.codproveedor = p.codproveedor INNER JOIN dirproveedores dp ON p.codproveedor = dp.codproveedor INNER JOIN paises pa ON dp.codpais = pa.codpais WHERE idla.ok = false AND idla.idlog IS NULL GROUP BY at.referencia || '-' || at.talla, a.descripcion, a.formatollegada, a.mgcomposicion, at.barcode, a.peso, a.alto, a.largo, a.ancho, a.volumen, a.sevende, pa.codzona, at.referencia")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["articulos"] > 0:
                    syncppal.iface.log("Error. Hay artículos no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Artículos enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de articulos IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='31', hour='6'))
    def elganso_sync_diagclientesidl():
        proceso = "diagclientesidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS clientes FROM clientes c INNER JOIN idl_clientes idlc ON c.codcliente = idlc.codcliente LEFT JOIN dirclientes dc ON c.codcliente = dc.codcliente LEFT JOIN tpv_tiendas t ON c.codcliente = t.codcliente WHERE idlc.ok = false AND idlc.idlog IS NULL")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["clientes"] > 0:
                    syncppal.iface.log("Error. Hay clientes no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Clientes enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de clientes IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='32', hour='6'))
    def elganso_sync_diagproveedoresidl():
        proceso = "diagproveedoresidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS proveedores FROM idl_proveedores i INNER JOIN proveedores p ON i.codproveedor = p.codproveedor INNER JOIN dirproveedores d ON p.codproveedor = d.codproveedor AND d.direccionppal WHERE i.idlog = 0 OR i.idlog IS NULL")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["proveedores"] > 0:
                    syncppal.iface.log("Error. Hay proveedores no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Proveedores enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de proveedores IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='33', hour='6'))
    def elganso_sync_diagpedidoscliidl():
        proceso = "diagpedidoscliidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS pedidoscli FROM pedidoscli p INNER JOIN almacenesidl a ON p.codalmacen = a.codalmacen INNER JOIN clientes c ON c.codcliente = p.codcliente INNER JOIN agenciastrans_idl ag ON c.codagenciaidl = ag.codagenciaidl INNER JOIN idl_clientes i ON p.codcliente = i.codcliente AND ok = true LEFT OUTER JOIN paises pa ON p.codpais = pa.codpais LEFT OUTER JOIN eg_pedidosenviados e ON p.idpedido = e.idpedido  WHERE p.enviado = true AND p.fichero IS NULL AND p.ciudad IS NOT NULL AND p.direccion IS NOT NULL AND p.provincia IS NOT NULL AND p.codpostal IS NOT NULL AND p.codcliente IS NOT NULL AND p.fecha >= '2018-01-01' AND p.idpedido IN (SELECT idpedido FROM lineaspedidoscli WHERE idpedido = p.idpedido AND incluidoenfichero) AND pa.codiso3 IS NOT NULL GROUP BY p.codigo, a.codalmacenidl, p.nombrecliente, p.fecha, p.fechasalida, p.codcliente, p.direccion, p.codpostal, p.ciudad, p.provincia, pa.codiso3, p.idpedido, ag.nombre, ag.descripcion")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["pedidoscli"] > 0:
                    syncppal.iface.log("Error. Hay pedidos de cliente no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Pedidos de cliente enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de pedidos de cliente IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='34', hour='6'))
    def elganso_sync_diagpedidoscdidl():
        proceso = "diagpedidoscdidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS pedidosCrossDock FROM albaranescd cd INNER JOIN lineasalbaranescd lc ON cd.idalbaran = lc.idalbaran INNER JOIN pedidosprov p ON lc.idpedido = p.idpedido INNER JOIN almacenesidl a ON p.codalmacen = a.codalmacen LEFT OUTER JOIN eg_pedidosrecibidos r ON lc.codpedido = r.codpedido WHERE cd.enviado = true AND cd.fichero IS NULL AND cd.idalbaran IN (SELECT idalbaran FROM lineasalbaranescd WHERE idalbaran = cd.idalbaran) GROUP BY r.idpedido, cd.codigo, cd.idalbaran, cd.fecharecepcion,cd.horarecepcion, p.fecha, a.codalmacenidl, a.nombre")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["pedidosCrossDock"] > 0:
                    syncppal.iface.log("Error. Hay pedidos Cross Docking no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Pedidos Cross Docking enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de pedidos cross docking IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='35', hour='6'))
    def elganso_sync_diagpedidosprovidl():
        proceso = "diagpedidosprovidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS pedidosprov FROM pedidosprov pp INNER JOIN almacenesidl ai ON pp.codalmacen = ai.codalmacen INNER JOIN idl_proveedores ip ON (pp.codproveedor = ip.codproveedor AND ip.ok = true) LEFT OUTER JOIN eg_pedidosrecibidos pr ON pp.idpedido = pr.idpedido WHERE (pp.enviado = true AND pp.fichero is NULL AND pp.codproveedor IS NOT NULL AND pp.idpedido IN (SELECT lpp.idpedido FROM lineaspedidosprov lpp WHERE lpp.idpedido = pp.idpedido)) GROUP BY pr.idpedido, pp.codigo, pp.idpedido, pp.fechaentrada, pp.fecha, pp.enviomodificado, ai.codalmacenidl, ai.nombre, pp.codproveedor ORDER BY pp.fecha ASC LIMIT 1")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["pedidosprov"] > 0:
                    syncppal.iface.log("Error. Hay pedidos de proveedor no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Pedidos de proveedor enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de pedidos de proveedor IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='36', hour='6'))
    def elganso_sync_diagviajesorigenidl():
        proceso = "diagviajesorigenidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS viajesorigen FROM tpv_viajesmultitransstock v LEFT JOIN tpv_multitransstock m ON v.codmultitransstock = m.codmultitransstock INNER JOIN almacenesidl a ON v.codalmaorigen = a.codalmacen INNER JOIN almacenes d ON v.codalmadestino = d.codalmacen LEFT OUTER JOIN tpv_tiendas t ON d.codalmacen = t.codalmacen INNER JOIN clientes c ON c.codcliente = t.codcliente INNER JOIN idl_clientes i ON t.codcliente = i.codcliente AND ok = true LEFT OUTER JOIN paises pa ON d.codpais = pa.codpais INNER JOIN agenciastrans_idl ag ON c.codagenciaidl = ag.codagenciaidl WHERE v.codalbarancd IS NULL AND codalmadestino NOT IN (SELECT codalmacen FROM almacenesidl) AND (m.estado = 'Aceptado' OR m.estado is null) AND v.fecha >= '2020-01-01' AND v.ptesincroenvio = true AND azkarok = false AND v.idviajemultitrans IN (SELECT idviajemultitrans FROM tpv_lineasmultitransstock WHERE idviajemultitrans = v.idviajemultitrans) AND v.estado = 'PTE ENVIO'")

            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["viajesorigen"] > 0:
                    syncppal.iface.log("Error. Hay viajes origen no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Viajes origen enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de viajes origen IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='37', hour='6'))
    def elganso_sync_diagviajesdestinoidl():
        proceso = "diagviajesdestinoidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS viajesdestino FROM tpv_viajesmultitransstock v INNER JOIN almacenesidl a ON v.codalmadestino = a.codalmacen INNER JOIN almacenes al ON a.codalmacen = al.codalmacen LEFT JOIN idl_ecommercefaltante f ON v.idviajemultitrans = f.idviajemultitrans LEFT JOIN idl_ecommerce e ON f.idecommerce = e.id WHERE v.codalmaorigen NOT IN (SELECT codalmacen FROM almacenesidl) AND (v.estado = 'EN TRANSITO' OR v.estado = 'RECIBIDO PARCIAL') AND v.enviocompletado = true AND v.azkarok = false AND v.fecha >= '2018-09-01' AND v.idviajemultitrans IN (SELECT idviajemultitrans FROM tpv_lineasmultitransstock WHERE idviajemultitrans = v.idviajemultitrans)")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["viajesdestino"] > 0:
                    syncppal.iface.log("Error. Hay viajes destino no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Viajes destino enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de viajes destino IDL", proceso)
            return False

        return True


    # @periodic_task(run_every=crontab(minute='38', hour='6'))
    # def elganso_sync_diagviajestransferenciaidl():
    #     proceso = "diagviajestransferenciaidl"

    #     try:
    #         cxC = importVentas.iface.creaConexion("ACEN")

    #         if not cxC:
    #             syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
    #             return False

    #         if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
    #             syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
    #             return False

    #         hayError = False
    #         cxC["cur"].execute("SELECT count(*) AS viajestransferencia FROM tpv_viajesmultitransstock v LEFT JOIN tpv_multitransstock m ON v.codmultitransstock = m.codmultitransstock INNER JOIN almacenesidl a ON v.codalmaorigen = a.codalmacen INNER JOIN almacenes d ON v.codalmadestino = d.codalmacen LEFT OUTER JOIN paises pa ON d.codpais = pa.codpais WHERE v.codalbarancd IS NULL AND (m.estado = 'Aceptado' OR m.estado IS NULL) AND v.fecha >= '2018-07-18' AND v.idviajemultitrans IN (SELECT idviajemultitrans FROM tpv_lineasmultitransstock WHERE idviajemultitrans = v.idviajemultitrans) AND v.estado = 'PTE ENVIO' AND v.codalmaorigen IN (SELECT codalmacen FROM almacenesidl) AND v.codalmadestino IN (SELECT codalmacen FROM almacenesidl) AND azkarok = false")
    #         rows = cxC["cur"].fetchall()
    #         if len(rows) > 0:
    #             if rows[0]["viajestransferencia"] > 0:
    #                 syncppal.iface.log("Error. Hay viajes transferencia no enviados a IDL", proceso)
    #                 hayError = True

    #         if not hayError:
    #             syncppal.iface.log("Éxito. Viajes transferencia enviados a IDL Correctamente", proceso)

    #     except Exception as e:
    #         syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de viajes transferencia IDL", proceso)
    #         return False

    #     return True


    @periodic_task(run_every=crontab(minute='39', hour='6'))
    def elganso_sync_diagviajescdidl():
        proceso = "diagviajescdidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS viajescd FROM tpv_viajesmultitransstock v LEFT JOIN tpv_multitransstock m ON (v.codmultitransstock = m.codmultitransstock AND m.estado = 'Aceptado') INNER JOIN almacenesidl a ON v.codalmaorigen = a.codalmacen INNER JOIN almacenes d ON v.codalmadestino = d.codalmacen LEFT OUTER JOIN tpv_tiendas t ON d.codalmacen = t.codalmacen INNER JOIN clientes c ON c.codcliente = t.codcliente LEFT OUTER JOIN paises pa ON d.codpais = pa.codpais INNER JOIN agenciastrans_idl ag ON c.codagenciaidl = ag.codagenciaidl WHERE codalmadestino NOT IN (SELECT codalmacen FROM almacenesidl) AND v.fecha >= '2018-07-18' AND azkarok = false AND v.idviajemultitrans IN (SELECT idviajemultitrans FROM tpv_lineasmultitransstock WHERE idviajemultitrans = v.idviajemultitrans) AND v.estado = 'PTE ENVIO' AND v.codalbarancd IS NOT NULL")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["viajescd"] > 0:
                    syncppal.iface.log("Error. Hay viajes Cross Docking no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Viajes Cross Docking enviados a IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de viajes Cross Docking IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='40', hour='6'))
    def elganso_sync_diagpedidosecommerceidl():
        proceso = "diagpedidosecommerceidl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS ecommerce FROM idl_ecommerce eco INNER JOIN tpv_comandas c ON (eco.idtpv_comanda = c.idtpv_comanda AND eco.codcomanda = c.codigo) LEFT OUTER JOIN mg_datosenviocomanda de ON c.idtpv_comanda = de.idtpv_comanda LEFT OUTER JOIN paises pa ON de.mg_paisenv = pa.codpais LEFT OUTER JOIN idiomas i ON pa.codidioma = i.codidioma LEFT OUTER JOIN paises pac ON c.codpais = pac.codpais LEFT OUTER JOIN idiomas ic ON pac.codidioma = ic.codidioma LEFT OUTER JOIN tpv_tiendas t ON c.codtiendarecogida = t.codtienda LEFT OUTER JOIN paises pat ON t.codpais = pat.codpais LEFT OUTER JOIN idiomas it ON pat.codidioma = it.codidioma WHERE eco.envioidl = false AND (eco.idlogenvio IS NULL OR eco.idlogenvio = 0) AND (eco.imprimirfactura = false OR (eco.imprimirfactura = true AND eco.facturaimpresa = true)) AND (c.egcodpedidoweb is null or c.egcodpedidoweb <> 'Pendiente') AND eco.codcomanda IS NOT NULL")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["ecommerce"] > 0:
                    syncppal.iface.log("Error. Hay pedidos ecommerce no enviados a IDL", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Pedidos ecommerce IDL Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de pedidos ecommerce IDL", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='41', hour='6'))
    def elganso_sync_diagdevecorecibidas():
        proceso = "diagdevecorecibidas"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS ecodevol FROM idl_ecommercedevoluciones ecodev INNER JOIN tpv_comandas c ON ecodev.idtpv_comanda = c.idtpv_comanda WHERE ecodev.envioidl = false AND (ecodev.idlogrecepcion IS NULL OR ecodev.idlogrecepcion = 0)")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["ecodevol"] > 0:
                    syncppal.iface.log("Error. Hay devoluciones ecommerce no recibidas", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Devoluciones ecommerce recibidas correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de devolucionse ecommerce recibidas", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='30', hour='6'))
    def elganso_sync_diagdevecomagento():
        proceso = "diagdevecomagento"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")

            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False

            hayError = False
            cxC["cur"].execute("SELECT count(*) AS informadomagento FROM idl_ecommercedevoluciones d LEFT OUTER JOIN idl_ecommerce v ON d.codcomanda = v.codcomanda WHERE d.confirmacionrecepcion = 'Si' AND (d.informadomagento IS NULL OR d.informadomagento = false) AND (v.codcomanda IS NULL OR v.codcomanda IS NOT NULL AND v.confirmacionenvio = 'Si') AND d.codcomanda like 'WDV%'")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["informadomagento"] > 0:
                    syncppal.iface.log("Error. Hay devoluciones ecommerce confirmadas y no informadas a magento", proceso)
                    hayError = True

            if not hayError:
                syncppal.iface.log("Éxito. Devoluciones ecommerce informadas a magento Correctamente", proceso)

        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de devolucionse ecommerce informadas a magento", proceso)
            return False

        return True


    @periodic_task(run_every=crontab(minute='0', hour='6'))
    def elganso_sync_diagarticulosactivosmirakl():
        proceso = "diagarticulosactivosmirakl"

        try:
            cxC = importVentas.iface.creaConexion("ACEN")
            if not cxC:
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False
            if not importVentas.iface.comprobarConexion("ACEN", cxC, proceso):
                syncppal.iface.log("Error. No se pudo conectar con la central", proceso)
                return False
            hayError = False
            cxC["cur"].execute("SELECT count(*) AS articulos FROM ew_jsonarticulosactivos")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                if rows[0]["articulos"] > 1:
                    syncppal.iface.log("Error. Hay registros en ew_jsonarticulosactivos", proceso)
                    hayError = True
            cxC["cur"].execute("SELECT count(*) AS articulos FROM ew_articuloseciweb")
            rows = cxC["cur"].fetchall()
            if len(rows) > 0:
                numArtAbanQ = rows[0]["articulos"]
                cxC["cur"].execute("SELECT valor FROM param_parametros WHERE NOMBRE = 'WSEW_ARTPUBLICADOS'")
                row = cxC["cur"].fetchall()
                valor = row[0]["valor"]
                datosCX = json.loads(valor)
                url = datosCX["url"]
                auth = datosCX["auth"]
                params = {"max":"1"}
                url = url + "?max=1" 
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": auth
                }
                response = requests.get(url,  headers=headers)
                result = response.text.encode("utf-8").decode("ISO8859-15")
                jSResult = json.loads(result)
                totalCount = jSResult["total_count"]
                if totalCount > numArtAbanQ:
                    syncppal.iface.log("Error. El número de artícuos en mirakl es mayor que el de abanq", proceso)
                    hayError = True
            if not hayError:
                syncppal.iface.log("Éxito. No hay registros en ew_jsonarticulosactivos", proceso)
        except Exception as e:
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de articulos eciweb en abanq", proceso)
            return False

        return True


    def __init__(self, context=None):
        super(elganso_sync, self).__init__(context)


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
