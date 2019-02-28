# @class_declaration interna #
import datetime

from celery.task import periodic_task
from celery.schedules import crontab

from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from models.flsyncppal import flsyncppal_def as syncppal


class interna(qsatype.objetoBase):

    ctx = qsatype.Object()

    def __init__(self, context=None):
        self.ctx = context


# @class_declaration elganso_sync #
class elganso_sync(interna):

    # @periodic_task(run_every=crontab(minute='*/30'))
    # def elganso_sync_diagventasmagento():
    #     try:
    #         qM = qsatype.FLSqlQuery("", "magento")
    #         qM.setSelect("increment_id")
    #         qM.setFrom("sales_flat_order")
    #         # Desde los ultimos 2 meses a los ultimos 30 minutos
    #         qM.setWhere("status IN ('complete', 'processing') AND is_exported = 1 AND created_at <= DATE_SUB(NOW(), INTERVAL 30 MINUTE) AND SUBSTRING(created_at FROM 1 FOR 10) >= DATE_SUB(CURDATE(), INTERVAL 2 MONTH) AND increment_id <> '620007251-1'")

    #         if not qM.exec_():
    #             syncppal.iface.log("Error. Falló la consulta de diagnóstico de ventas de Magento (en la web)", "diagventasmagento")
    #             return False

    #         q = qsatype.FLSqlQuery()
    #         q.setSelect("codigo")
    #         q.setFrom("tpv_comandas")

    #         numPedidos = 0
    #         while qM.next():
    #             q.setWhere("codigo = 'WEB" + str(qM.value(0)) + "'")

    #             if not q.exec_():
    #                 syncppal.iface.log("Error. Falló la consulta de diagnóstico de ventas de Magento (en central)", "diagventasmagento")
    #                 return False

    #             if not q.first():
    #                 numPedidos = numPedidos + 1

    #         if numPedidos > 0:
    #             syncppal.iface.log("Error. Hay " + str(numPedidos) + " pedidos de Magento sin sincronizar", "diagventasmagento")
    #             return False

    #         syncppal.iface.log("Éxito. Todos los pedidos de magento están sincronizados", "diagventasmagento")

    #     except Exception as e:
    #         print(e)
    #         qsatype.debug(e)
    #         syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de ventas de Magento", "diagventasmagento")
    #         return False

    #     return True

    @periodic_task(run_every=crontab(minute='30', hour='0,8,16'))
    def elganso_sync_diagdevolucionesweb():
        try:
            fh = qsatype.Date().now()

            q = qsatype.FLSqlQuery()
            q.setSelect("COUNT(*)")
            q.setFrom("tpv_comandas c LEFT OUTER JOIN eg_devolucionesweb d ON c.codigo = d.codigo INNER JOIN tpv_agentes a ON c.codtpv_agente = a.codtpv_agente")
            # Ultimos 2 meses
            q.setWhere("c.fecha >= '2017-05-01' AND c.fecha >= timestamp '" + fh + "' - INTERVAL '2 MONTH' AND c.codtienda = 'AWEB' AND d.id IS NULL AND a.codtienda <> 'AWEB' AND a.codtpv_agente <> '9999'")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de diagnóstico de devoluciones web", "diagdevolucionesweb")
                return False

            if not q.first():
                syncppal.iface.log("Error. No se encontraron resultados válidos para diagnóstico de devoluciones web", "diagdevolucionesweb")
                return False

            if q.value(0) > 0:
                syncppal.iface.log("Error. Hay " + str(q.value(0)) + " registros de devoluciones web sin crear", "diagdevolucionesweb")
                return False

            syncppal.iface.log("Éxito. No hay registros de devoluciones web sin crear", "diagdevolucionesweb")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de devoluciones web", "diagdevolucionesweb")
            return False

        return True

    @periodic_task(run_every=crontab(minute='30', hour='8'))
    def elganso_sync_diagverificacioncontable():
        diffLimit = 1

        try:
            oErrores = {}

            q = qsatype.FLSqlQuery()
            q.setSelect("SUM(p.haber - p.debe), t.codsubcentro, ca.fecha, t.codtienda, a.idtpv_arqueo")
            q.setFrom("tpv_arqueos a INNER JOIN co_asientos ca ON (ca.idasiento = a.idasiento OR ca.idasiento = a.idasientovale) LEFT OUTER JOIN co_partidas p ON ca.idasiento = p.idasiento INNER JOIN co_subcuentas cs ON cs.idsubcuenta = p.idsubcuenta INNER JOIN co_cuentas c ON c.idcuenta = cs.idcuenta INNER JOIN tpv_tiendas t ON t.codtienda = a.codtienda INNER JOIN empresa e ON t.idempresa = e.id")
            # Desde hace 6 días hasta ayer
            q.setWhere("e.contintegrada AND a.diadesde <= CURRENT_DATE - 1 AND a.diadesde >= CURRENT_DATE - 6 AND t.codsubcentro IS NOT NULL AND c.codcuenta IN ('700', '708', '7000', '7080') GROUP BY t.codsubcentro, ca.fecha, t.codtienda, a.idtpv_arqueo ORDER BY ca.fecha, t.codsubcentro")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de verificación contable (neto)", "diagverificacioncontable")
                return False

            # Como ALIL y ALMJ se contabilizan juntas, incluimos un campo de excepción para estas
            excAlilAlmj = {}

            importePagos = 0
            importePagosSinIva = 0
            resta = 0

            while q.next():
                fecha = q.value("ca.fecha").strftime("%Y-%m-%d")

                importePagos = q.value("SUM(p.haber - p.debe)")

                if q.value("t.codtienda") == "AWEB":
                    importePagosSinIva = qsatype.FLUtil.sqlSelect("facturascli f INNER JOIN lineasfacturascli l ON f.idfactura = l.idfactura INNER JOIN tpv_comandas c ON f.idfactura = c.idfactura", "SUM(l.pvptotal)", "c.idtpv_comanda IN (SELECT DISTINCT idtpv_comanda FROM tpv_pagoscomanda WHERE idtpv_arqueo = '" + q.value("a.idtpv_arqueo") + "') AND l.descripcion NOT ILIKE '%descuento%'", "facturascli,tpv_comandas")
                else:
                    importePagosSinIva = qsatype.FLUtil.sqlSelect("facturascli f INNER JOIN tpv_comandas c ON f.idfactura = c.idfactura", "SUM(f.neto)", "c.idtpv_comanda IN (SELECT DISTINCT idtpv_comanda FROM tpv_pagoscomanda WHERE idtpv_arqueo = '" + q.value("a.idtpv_arqueo") + "')", "facturascli,tpv_comandas")

                if importePagos is None:
                    importePagos = 0
                if importePagos < 0:
                    importePagos = importePagos * (-1)

                if importePagosSinIva is None:
                    importePagosSinIva = 0
                if importePagosSinIva < 0:
                    importePagosSinIva = importePagosSinIva * (-1)

                importePagos = qsatype.FLUtil.roundFieldValue(importePagos, "lineaspedidoscli", "pvptotaliva")
                importePagosSinIva = qsatype.FLUtil.roundFieldValue(importePagosSinIva, "lineaspedidoscli", "pvptotaliva")
                resta = qsatype.FLUtil.roundFieldValue(importePagos - importePagosSinIva, "lineaspedidoscli", "pvptotaliva")

                if abs(resta) > diffLimit:
                    if q.value("t.codtienda") in ["ALIL", "ALMJ"]:
                        if fecha not in excAlilAlmj or excAlilAlmj[fecha] is None:
                            excAlilAlmj[fecha] = resta
                            continue
                        else:
                            if abs(excAlilAlmj[fecha] + resta) < diffLimit:
                                excAlilAlmj[fecha] = None
                                continue

                    fecha = qsatype.FLUtil.dateAMDtoDMA(fecha)

                    if fecha not in oErrores:
                        oErrores[fecha] = []

                    oErrores[fecha].append(q.value("a.idtpv_arqueo"))

            if len(oErrores.keys()) > 1:
                syncppal.iface.log("Error. Hay descuadres en la verificación contable (neto) de " + str(len(oErrores.keys())) + " días", "diagverificacioncontable")
                return False

            for f in oErrores:
                if len(oErrores[f]) > 1:
                    syncppal.iface.log("Error. Hay descuadres en la verificación contable (neto) del día " + f + " en " + str(len(oErrores[f])) + " arqueos", "diagverificacioncontable")
                    return False

                syncppal.iface.log("Error. Hay descuadres en la verificación contable (neto) del día " + f + " en " + oErrores[f][0], "diagverificacioncontable")
                return False

            if len(excAlilAlmj):
                for f in excAlilAlmj:
                    if abs(excAlilAlmj[f]) > diffLimit:
                        syncppal.iface.log("Error. Hay descuadres en la verificación contable (neto) en ALIL o ALMJ", "diagverificacioncontable")
                        return False

            oErrores = {}

            q = qsatype.FLSqlQuery()
            q.setSelect("SUM(p.haber - p.debe), t.codsubcentro, ca.fecha, t.codtienda, a.idtpv_arqueo")
            q.setFrom("tpv_arqueos a INNER JOIN co_asientos ca ON (ca.idasiento = a.idasiento OR ca.idasiento = a.idasientovale) LEFT OUTER JOIN co_partidas p ON ca.idasiento = p.idasiento INNER JOIN co_subcuentas cs ON cs.idsubcuenta = p.idsubcuenta INNER JOIN co_cuentas c ON c.idcuenta = cs.idcuenta INNER JOIN tpv_tiendas t ON t.codtienda = a.codtienda INNER JOIN empresa e ON t.idempresa = e.id")
            # Desde hace 6 días hasta ayer
            q.setWhere("e.contintegrada AND a.diadesde <= CURRENT_DATE - 1 AND a.diadesde >= CURRENT_DATE - 6 AND t.codsubcentro IS NOT NULL AND c.codcuenta IN ('477', '4770') GROUP BY t.codsubcentro, ca.fecha, t.codtienda, a.idtpv_arqueo ORDER BY ca.fecha, t.codsubcentro")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de verificación contable (iva)", "diagverificacioncontable")
                return False

            # Como ALIL y ALMJ se contabilizan juntas, incluimos un campo de excepción para estas
            excAlilAlmj = {}

            impAsientosArqueo = 0
            impAsientosFactura = 0
            resta = 0

            while q.next():
                fecha = q.value("ca.fecha").strftime("%Y-%m-%d")

                impAsientosArqueo = q.value("SUM(p.haber - p.debe)")
                impAsientosFactura = qsatype.FLUtil.sqlSelect("co_partidas p INNER JOIN co_asientos a ON p.idasiento = a.idasiento INNER JOIN facturascli f ON a.idasiento = f.idasiento INNER JOIN tpv_comandas c ON f.idfactura = c.idfactura", "SUM(p.haber - p.debe)", "c.idtpv_comanda IN (SELECT DISTINCT idtpv_comanda FROM tpv_pagoscomanda WHERE idtpv_arqueo = '" + q.value("a.idtpv_arqueo") + "') AND p.idcontrapartida IS NOT NULL", "co_partidas,co_asientos,facturascli,tpv_comandas")

                if q.value("t.codtienda") == "AWEB":
                    impDescuentosFactura = qsatype.FLUtil.sqlSelect("facturascli f INNER JOIN lineasfacturascli lf ON f.idfactura = lf.idfactura INNER JOIN tpv_comandas c ON f.idfactura = c.idfactura", "SUM(lf.pvptotaliva - lf.pvptotal)", "c.idtpv_comanda IN (SELECT DISTINCT idtpv_comanda FROM tpv_pagoscomanda WHERE idtpv_arqueo = '" + q.value("a.idtpv_arqueo") + "') AND lf.descripcion ILIKE '%descuento%'", "facturascli,lineasfacturascli,tpv_comandas")
                    impAsientosFactura = impAsientosFactura - impDescuentosFactura

                if impAsientosArqueo is None:
                    impAsientosArqueo = 0
                if impAsientosArqueo < 0:
                    impAsientosArqueo = impAsientosArqueo * (-1)

                if impAsientosFactura is None:
                    impAsientosFactura = 0
                if impAsientosFactura < 0:
                    impAsientosFactura = impAsientosFactura * (-1)

                impAsientosArqueo = qsatype.FLUtil.roundFieldValue(impAsientosArqueo, "lineaspedidoscli", "pvptotaliva")
                impAsientosFactura = qsatype.FLUtil.roundFieldValue(impAsientosFactura, "lineaspedidoscli", "pvptotaliva")
                resta = qsatype.FLUtil.roundFieldValue(impAsientosArqueo - impAsientosFactura, "lineaspedidoscli", "pvptotaliva")

                if abs(resta) > diffLimit:
                    if q.value("t.codtienda") in ["ALIL", "ALMJ"]:
                        if fecha not in excAlilAlmj or excAlilAlmj[fecha] is None:
                            excAlilAlmj[fecha] = resta
                            continue
                        else:
                            if abs(excAlilAlmj[fecha] + resta) < diffLimit:
                                excAlilAlmj[fecha] = None
                                continue

                    fecha = qsatype.FLUtil.dateAMDtoDMA(fecha)

                    if fecha not in oErrores:
                        oErrores[fecha] = []

                    oErrores[fecha].append(q.value("a.idtpv_arqueo"))

            if len(oErrores.keys()) > 1:
                syncppal.iface.log("Error. Hay descuadres en la verificación contable (iva) de " + str(len(oErrores.keys())) + " días", "diagverificacioncontable")
                return False

            for f in oErrores:
                if len(oErrores[f]) > 1:
                    syncppal.iface.log("Error. Hay descuadres en la verificación contable (iva) del día " + f + " en " + str(len(oErrores[f])) + " arqueos", "diagverificacioncontable")
                    return False

                syncppal.iface.log("Error. Hay descuadres en la verificación contable (iva) del día " + f + " en el arqueo " + oErrores[f][0], "diagverificacioncontable")
                return False

            if len(excAlilAlmj):
                for f in excAlilAlmj:
                    if abs(excAlilAlmj[f]) > diffLimit:
                        syncppal.iface.log("Error. Hay descuadres en la verificación contable (iva) en ALIL o ALMJ", "diagverificacioncontable")
                        return False

            syncppal.iface.log("Éxito. Contabilidad verificada", "diagverificacioncontable")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de verificación contable", "diagverificacioncontable")
            return False

        return True

    @periodic_task(run_every=crontab(hour='*/1', minute='0'))
    def elganso_sync_diagfacturacionventas():
        try:
            fh = qsatype.Date().now()

            # Ventas tiendas nacionales
            q = qsatype.FLSqlQuery()
            q.setSelect("COUNT(*)")
            q.setFrom("tpv_comandas c LEFT OUTER JOIN facturascli f ON c.codigo = f.codigo INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda INNER JOIN empresa e ON t.idempresa = e.id")
            # Desde hace dos meses hasta ayer
            q.setWhere("c.fecha >= '2017-06-01' AND c.fecha <= CURRENT_DATE - 1 AND c.fecha >= timestamp '" + fh + "' - INTERVAL '2 MONTH' AND c.codtienda <> 'AWEB' AND e.contintegrada AND e.id = 1 AND f.idfactura IS NULL AND c.idfactura <> 1")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de facturación de ventas de tiendas nacionales", "diagfacturacionventas")
                return False

            if not q.first():
                syncppal.iface.log("Error. No se encontraron resultados válidos para ventas de tiendas nacionales", "diagfacturacionventas")
                return False

            if q.value(0) > 0:
                syncppal.iface.log("Error. Hay " + str(q.value(0)) + " ventas de tiendas nacionales sin facturar", "diagfacturacionventas")
                return False

            # Ventas tiendas internacionales
            q = qsatype.FLSqlQuery()
            q.setSelect("COUNT(*)")
            q.setFrom("tpv_comandas c LEFT OUTER JOIN facturascli f ON c.egcodfactura = f.codigo INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda INNER JOIN empresa e ON t.idempresa = e.id")
            # Desde hace dos meses hasta ayer
            q.setWhere("c.fecha >= '2017-06-01' AND c.fecha <= CURRENT_DATE - 1 AND c.fecha >= timestamp '" + fh + "' - INTERVAL '2 MONTH' AND c.codtienda <> 'AWEB' AND e.contintegrada AND e.id <> 1 AND f.idfactura IS NULL")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de facturación de ventas de tiendas internacionales", "diagfacturacionventas")
                return False

            if not q.first():
                syncppal.iface.log("Error. No se encontraron resultados válidos para ventas de tiendas internacionales", "diagfacturacionventas")
                return False

            if q.value(0) > 0:
                syncppal.iface.log("Error. Hay " + str(q.value(0)) + " ventas de tiendas internacionales sin facturar", "diagfacturacionventas")
                return False

            # Ventas web
            q = qsatype.FLSqlQuery()
            q.setSelect("COUNT(*)")
            q.setFrom("tpv_comandas c LEFT OUTER JOIN facturascli f ON c.egcodfactura = f.codigo INNER JOIN tpv_tiendas t ON c.codtienda = t.codtienda INNER JOIN empresa e ON t.idempresa = e.id")
            # Desde hace dos meses hasta ayer
            q.setWhere("c.fecha >= '2017-06-01' AND c.fecha <= CURRENT_DATE - 1 AND c.fecha >= timestamp '" + fh + "' - INTERVAL '2 MONTH' AND c.codtienda = 'AWEB' AND e.contintegrada AND f.idfactura IS NULL")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de facturación de ventas web", "diagfacturacionventas")
                return False

            if not q.first():
                syncppal.iface.log("Error. No se encontraron resultados válidos para ventas web", "diagfacturacionventas")
                return False

            if q.value(0) > 0:
                syncppal.iface.log("Error. Hay " + str(q.value(0)) + " ventas web sin facturar", "diagfacturacionventas")
                return False

            syncppal.iface.log("Éxito. Todas las ventas están facturadas", "diagfacturacionventas")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de facturación de ventas", "diagfacturacionventas")
            return False

        return True

    @periodic_task(run_every=crontab(minute='*/30'))
    def elganso_sync_diagsincroventas():
        try:
            horasNoCorner = 8
            horasNoCornerGrupo = 4
            ntNoCorner = 6
            horasCornerGrupo = 30
            ntCorner = 15

            fh = qsatype.Date().now()
            whereFijo = "t.sincroactiva AND t.servidor IS NOT NULL AND esquema = 'VENTAS_TPV'"
            orderBy = " ORDER BY f.fechasincro, f.horasincro"

            tiendasNac = "'" + "','".join(qsatype.FactoriaModulos.get('formtpv_tiendas').iface.dameTiendasSincro("NOCORNER_ES").split(",")) + "'"
            tiendasInt = "'" + "','".join(qsatype.FactoriaModulos.get('formtpv_tiendas').iface.dameTiendasSincro("NOCORNER_EXT").split(",")) + "'"
            tiendasCorner = "'" + "','".join(qsatype.FactoriaModulos.get('formtpv_tiendas').iface.dameTiendasSincro("CORNER").split(",")) + "'"

            # Tiendas nacionales grupo
            q = qsatype.FLSqlQuery()
            q.setSelect("t.codtienda")
            q.setFrom("tpv_tiendas t LEFT OUTER JOIN tpv_fechasincrotienda f ON t.codtienda = f.codtienda")
            q.setWhere(whereFijo + " AND t.codtienda IN (" + tiendasNac + ") AND timestamp '" + fh + "' - INTERVAL '" + str(horasNoCornerGrupo) + " HOUR' > CAST(fechasincro || 'T' || horasincro as timestamp)" + orderBy)

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de ventas de tiendas nacionales en grupo", "diagsincroventas")
                return False

            if q.size() >= ntNoCorner:
                syncppal.iface.log("Error. Hay " + str(q.size()) + " tiendas nacionales que llevan más de " + str(horasNoCornerGrupo) + " horas sin sincronizar ventas", "diagsincroventas")
                return False

            # Tiendas internacionales grupo
            q = qsatype.FLSqlQuery()
            q.setSelect("t.codtienda")
            q.setFrom("tpv_tiendas t LEFT OUTER JOIN tpv_fechasincrotienda f ON t.codtienda = f.codtienda")
            q.setWhere(whereFijo + " AND t.codtienda IN (" + tiendasInt + ") AND timestamp '" + fh + "' - INTERVAL '" + str(horasNoCornerGrupo) + " HOUR' > CAST(fechasincro || 'T' || horasincro as timestamp)" + orderBy)

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de ventas de tiendas internacionales en grupo", "diagsincroventas")
                return False

            if q.size() >= ntNoCorner:
                syncppal.iface.log("Error. Hay " + str(q.size()) + " tiendas internacionales que llevan más de " + str(horasNoCornerGrupo) + " horas sin sincronizar ventas", "diagsincroventas")
                return False

            # Tiendas corner grupo
            q = qsatype.FLSqlQuery()
            q.setSelect("t.codtienda")
            q.setFrom("tpv_tiendas t LEFT OUTER JOIN tpv_fechasincrotienda f ON t.codtienda = f.codtienda")
            q.setWhere(whereFijo + " AND t.codtienda IN (" + tiendasCorner + ") AND timestamp '" + fh + "' - INTERVAL '" + str(horasCornerGrupo) + " HOUR' > CAST(fechasincro || 'T' || horasincro as timestamp)" + orderBy)

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de ventas de corners en grupo", "diagsincroventas")
                return False

            if q.size() >= ntCorner:
                syncppal.iface.log("Error. Hay " + str(q.size()) + " corners que llevan más de " + str(horasCornerGrupo) + " horas sin sincronizar ventas", "diagsincroventas")
                return False

            # Tiendas no corner individuales
            q = qsatype.FLSqlQuery()
            q.setSelect("t.codtienda")
            q.setFrom("tpv_tiendas t LEFT OUTER JOIN tpv_fechasincrotienda f ON t.codtienda = f.codtienda")
            q.setWhere(whereFijo + " AND (t.codtienda IN (" + tiendasNac + ") OR t.codtienda IN (" + tiendasInt + ")) AND timestamp '" + fh + "' - INTERVAL '" + str(horasNoCorner) + " HOUR' > CAST(fechasincro || 'T' || horasincro as timestamp)" + orderBy)

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de ventas de tiendas individuales", "diagsincroventas")
                return False

            if q.size() > 0:
                aTiendas = []
                while q.next():
                    aTiendas.append(q.value(0))
                syncppal.iface.log("Error. Las tiendas " + ",".join(aTiendas[:3]) + "... llevan más de " + str(horasNoCorner) + " horas sin sincronizar ventas", "diagsincroventas")
                return False

            syncppal.iface.log("Éxito. Todas las ventas de tiendas están sincronizadas", "diagsincroventas")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de sincronización de ventas", "diagsincroventas")
            return False

        return True

    @periodic_task(run_every=crontab(minute='30', hour='8'))
    def elganso_sync_diagsaldovales():
        try:
            f = qsatype.Date().today()
            f = qsatype.FLUtil.addYears(f, -1)[:10]

            q = qsatype.FLSqlQuery("")
            q.setSelect("COUNT(*)")
            q.setFrom("tpv_comandas c INNER JOIN tpv_pagoscomanda p ON c.codigo = p.refvale")
            # Ultimo anyo
            q.setWhere("c.fecha >= '2017-01-01' AND c.fecha >= '" + f + "' AND c.estado <> 'Anulada' AND p.idtpv_comanda NOT IN (SELECT idtpv_comanda FROM tpv_comandas WHERE idtpv_comanda = p.idtpv_comanda AND estado = 'Anulada') GROUP BY c.codigo, c.saldoconsumido, c.total, c.estado HAVING ABS(c.saldoconsumido - SUM(p.importe)) > 0.00001")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de saldo de vales", "diagsaldovales")
                return False

            if not q.first():
                syncppal.iface.log("Error. No se encontraron resultados válidos", "diagsaldovales")
                return False

            if q.value(0) > 0:
                syncppal.iface.log("Error. Hay " + str(q.value(0)) + " vales con saldo erróneo", "diagsaldovales")
                return False

            syncppal.iface.log("Éxito. Todos los vales tienen el saldo correcto", "diagsaldovales")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso", "diagsaldovales")
            return False

        return True

    @periodic_task(run_every=crontab(minute='30', hour='8'))
    def elganso_sync_diagcontanalitica():
        try:
            horasNoSincro = 26

            fh = qsatype.Date()

            q = qsatype.FLSqlQuery()
            q.setSelect("fechasincro, horasincro")
            q.setFrom("tpv_fechasincrotienda")
            q.setWhere("codtienda = 'ACEN' AND esquema = 'CONTANALITICA'")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de contabilidad analítica", "diagcontanalitica")
                return False

            if not q.first():
                syncppal.iface.log("Error. No hay registros para la sincro de contabilidad analítica", "diagcontanalitica")
                return False

            dtNoSincro = datetime.timedelta(hours=horasNoSincro)
            fhNoSincro = fh - dtNoSincro
            fhSincro = qsatype.Date(str(q.value("fechasincro")) + " " + str(q.value("horasincro")))
            if fhNoSincro > fhSincro:
                syncppal.iface.log("Error. La contabilidad analítica lleva más de " + str(horasNoSincro) + " horas sin sincronizar", "diagcontanalitica")
                return False

            syncppal.iface.log("Éxito. Contabilidad analítica sincronizada correctamente", "diagcontanalitica")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de contabilidad analítica", "diagcontanalitica")
            return False

        return True

    @periodic_task(run_every=crontab(minute='30', hour='8'))
    def elganso_sync_diagsolrepoweb():
        try:
            horasNoSincro = 26

            fh = qsatype.Date()

            q = qsatype.FLSqlQuery()
            q.setSelect("fechasincro, horasincro")
            q.setFrom("tpv_fechasincrotienda")
            q.setWhere("codtienda = 'WEBM' AND esquema = 'SOLICITUD_REPOSICION'")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de solicitudes de reposición", "diagsolrepoweb")
                return False

            if not q.first():
                syncppal.iface.log("Error. No hay registros para la sincro de solicitudes de reposición", "diagsolrepoweb")
                return False

            dtNoSincro = datetime.timedelta(hours=horasNoSincro)
            fhNoSincro = fh - dtNoSincro
            fhSincro = qsatype.Date(str(q.value("fechasincro")) + " " + str(q.value("horasincro")))
            if fhNoSincro > fhSincro:
                syncppal.iface.log("Error. Las solicitudes de reposición llevan más de " + str(horasNoSincro) + " horas sin sincronizar", "diagsolrepoweb")
                return False

            syncppal.iface.log("Éxito. Solicitudes de reposición sincronizada correctamente", "diagsolrepoweb")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de solicitudes de reposición", "diagsolrepoweb")
            return False

        return True

    @periodic_task(run_every=crontab(hour='*/1', minute='0'))
    def elganso_sync_diaganalyticalways():
        try:
            horasNoSincro = 12

            fh = qsatype.Date()

            q = qsatype.FLSqlQuery()
            q.setSelect("fechasincro, horasincro")
            q.setFrom("tpv_fechasincrotienda")
            q.setWhere("esquema = 'ANALYTICALWAYS'")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de analytic always", "diaganalyticalways")
                return False

            if not q.first():
                syncppal.iface.log("Error. No hay registros para analytic always", "diaganalyticalways")
                return False

            dtNoSincro = datetime.timedelta(hours=horasNoSincro)
            fhNoSincro = fh - dtNoSincro
            fhSincro = qsatype.Date(str(q.value("fechasincro")) + " " + str(q.value("horasincro")))
            if fhNoSincro > fhSincro:
                syncppal.iface.log("Error. Analytic always lleva más de " + str(horasNoSincro) + " horas sin sincronizar", "diaganalyticalways")
                return False

            syncppal.iface.log("Éxito. Analytic always sincronizada correctamente", "diaganalyticalways")

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de Analytic always", "diaganalyticalways")
            return False

        return True

    @periodic_task(run_every=crontab(hour='*/1', minute='4'))
    def elganso_sync_diagbloqueos():
        try:
            q = qsatype.FLSqlQuery()
            q.setSelect("bl.pid AS blocked_pid, a.usename AS blocked_user, kl.pid AS blocking_pid, ka.usename AS blocking_user, a.query AS blocked_statement ")
            q.setFrom("pg_catalog.pg_locks bl JOIN pg_catalog.pg_stat_activity a ON a.pid = bl.pid JOIN pg_catalog.pg_locks kl ON kl.transactionid = bl.transactionid AND kl.pid != bl.pid JOIN pg_catalog.pg_stat_activity ka ON ka.pid = kl.pid")
            q.setWhere("NOT bl.granted")

            if not q.exec_():
                syncppal.iface.log("Error. Falló la consulta de diagnóstico de bloqueos", "diagbloqueos")
                return False

            if not q.first():
                syncppal.iface.log("Éxito. No hay bloqueos en central", "diagbloqueos")
                return True
            else:
                syncppal.iface.log("Error. Hay bloqueos en central", "diagbloqueos")
                return False

        except Exception as e:
            print(e)
            qsatype.debug(e)
            syncppal.iface.log("Error. Ocurrió un error durante el proceso de diagnóstico de bloqueos", "diagbloqueos")
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
