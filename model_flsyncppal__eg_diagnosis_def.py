# @class_declaration interna #
import datetime

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

            cxC["cur"].execute("SELECT c.codigo AS codigo FROM tpv_comandas c LEFT OUTER JOIN tpv_lineascomanda p ON c.idtpv_comanda = p.idtpv_comanda WHERE c.fecha >= '2019-05-01' AND c.total <> 0 AND p.idtpv_linea IS NULL AND c.codtienda <> 'PROD';")
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

    @periodic_task(run_every=crontab(minute='55', hour='5'))
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

            cxC["cur"].execute("SELECT c.codigo AS codigo, c.idtpv_comanda AS idcomanda, c.codpais AS pais from tpv_comandas c left outer join idl_ecommerce e on c.idtpv_comanda = e.idtpv_comanda where c.fecha >= '2019-10-01' and c.egcodpedidoweb is not null and c.egcodpedidoweb like '20190%' and e.id is null")
            rows = cxC["cur"].fetchall()
            codigos = ""
            if len(rows) > 0:
                for p in rows:
                    if codigos != "":
                        codigos += ", "
                    codigos += p["codigo"] + "-" + p["idcomanda"] + "-" + p["pais"]

                syncppal.iface.log("Error. Hay direct orders sin enviar a idl: " + codigos, proceso)
            else:
                syncppal.iface.log("Éxito. No hay direct orders sin enviar a idl", proceso)

        except Exception as e:
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

            cxC["cur"].execute("SELECT valor FROM param_parametros WHERE nombre = 'FECHA_FACTURAS_ECI'")
            rows = cxC["cur"].fetchall()
            if len(rows) <= 0:
                syncppal.iface.log("Error. No se pudo obtener la fecha de diagnóstico de facturación ECI", proceso)
                return False

            fecha = rows[0]["valor"]
            cxC["cur"].execute("SELECT facturascli.enviadoeciedicom AS enviadas, count(*) AS count FROM facturascli WHERE facturascli.codcliente IN ('001039') AND facturascli.total > 0 AND facturascli.codeci IS NOT NULL AND facturascli.codeci <> '' AND facturascli.pedidoeci IS NOT NULL AND facturascli.pedidoeci <> '' AND facturascli.albaraneci IS NOT NULL AND facturascli.albaraneci <> '' AND facturascli.departamentoeci IS NOT NULL AND facturascli.departamentoeci <> '' AND facturascli.codejercicio IN ('2019') AND facturascli.codserie <> 'MY' AND facturascli.automatica = false AND facturascli.fecha >= '" + str(fecha) + "' GROUP BY facturascli.enviadoeciedicom")

            rows = cxC["cur"].fetchall()
            enviadas = 0
            noenviadas = 0
            if len(rows) > 0:
                for p in rows:
                    if p["enviadas"]:
                        enviadas = p["count"]
                    if not p["enviadas"]:
                        noenviadas = p["count"]

                syncppal.iface.log("Error. Hay facturas ECI. Enviadas: " + str(enviadas) + " No enviadas: " + str(noenviadas), proceso)
            else:
                syncppal.iface.log("Éxito. No hay facturas ECI", proceso)

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

            cxC["cur"].execute("SELECT count(*) AS ventas FROM tpv_comandas c INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda WHERE c.fecha = current_date-1 AND t.idempresa = 15")

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

            hayError = False;
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


    @periodic_task(run_every=crontab(minute='20', hour='6'))
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
