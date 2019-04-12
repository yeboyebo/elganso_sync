from AQNEXT.celery import app
from YBLEGACY import qsatype
from YBUTILS import globalValues
from YBUTILS import DbRouter

from models.flsyncppal import flsyncppal_def as syncppal
from models.flsyncppal import mg_importOrders_def as iMgOrders
from models.flsyncppal import mg_updateStocks_def as iMgStocks
from models.flsyncppal import mg_updatePoints_def as iMgPoints
from models.flsyncppal import mg_importCustomers_def as iMgCust
from models.flsyncppal import eg_importVentas_def as iTdaVentas
from models.flsyncppal import mg_updatePrices_def as iMgPrices
from models.flsyncppal import mg_importDevWeb_def as iMgDevWeb

globalValues.registrarmodulos()
cdDef = 10


def getActivity():
    i = app.control.inspect()
    active = i.active()
    scheduled = i.scheduled()
    reserved = i.reserved()

    aActive = {}
    for w in active:
        for t in active[w]:
            aActive[t['id']] = {}
            aActive[t['id']]['worker'] = w
            aActive[t['id']]['id'] = t['id']
            aActive[t['id']]['name'] = t['name']
            aActive[t['id']]['args'] = t['args']
    aScheduled = {}
    for w in scheduled:
        for t in scheduled[w]:
            aScheduled[t['request']['id']] = {}
            aScheduled[t['request']['id']]['worker'] = w
            aScheduled[t['request']['id']]['eta'] = t['eta'][:19]
            aScheduled[t['request']['id']]['id'] = t['request']['id']
            aScheduled[t['request']['id']]['name'] = t['request']['name']
            aScheduled[t['request']['id']]['args'] = t['request']['args']
    aReserved = {}
    for w in reserved:
        for t in reserved[w]:
            aReserved[t['id']] = {}
            aReserved[t['id']]['worker'] = w
            aReserved[t['id']]['id'] = t['id']
            aReserved[t['id']]['name'] = t['name']
            aReserved[t['id']]['args'] = t['args']

    return {'active': aActive, 'scheduled': aScheduled, 'reserved': aReserved}


def revoke(id):
    app.control.revoke(id, terminate=True)
    return True


@app.task
def getUnsynchronizedOrders(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iMgOrders.iface.getUnsynchronizedOrders() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsyncorders")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsyncorders'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        getUnsynchronizedOrders.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsyncorders")


@app.task
def updateProductStock(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iMgStocks.iface.updateProductStock() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsyncstock")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsyncstock'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        updateProductStock.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsyncstock")


@app.task
def updateProductPrices(r, first=True):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = None
        currT = str(qsatype.Date())[-(8):]

        dow = qsatype.FLUtil.sqlSelect("tpv_datosgenerales", "EXTRACT(DOW FROM CURRENT_DATE)", "1 = 1 LIMIT 1")

        if (currT > "02:00:00" and currT < "06:00:00" and int(dow) == 1) or first:
            cdTime = iMgPrices.iface.updateProductPrices() or cdDef
        else:
            syncppal.iface.log("Éxito. No es momento de sincronizar.", "mgsyncprices")
            cdTime = 300
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsyncprices")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsyncprices'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        updateProductPrices.apply_async((r, False), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsyncprices")


@app.task
def updatePointMovements(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iMgPoints.iface.updatePointMovements() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsyncpoints")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsyncpoints'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        updatePointMovements.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsyncpoints")


@app.task
def getUnsynchronizedCustomers(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iMgCust.iface.getUnsynchronizedCustomers() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsynccust")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsynccust'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        getUnsynchronizedCustomers.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsynccust")


@app.task
def getVentasTienda(r, codTienda):
    proceso = 'egsyncvt' + codTienda
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iTdaVentas.iface.getVentasTienda(codTienda) or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", proceso)
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = '" + proceso + "'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        getVentasTienda.apply_async((r, codTienda), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", proceso)


@app.task
def getUnsynchronizedDevWeb(r):
    DbRouter.ThreadLocalMiddleware.process_request_celery(None, r)

    try:
        cdTime = iMgDevWeb.iface.getUnsynchronizedDevWeb() or cdDef
    except Exception:
        syncppal.iface.log("Error. Fallo en tasks", "mgsyncdevweb")
        cdTime = cdDef

    activo = False
    try:
        resul = qsatype.FLSqlQuery().execSql("SELECT activo FROM yb_procesos WHERE proceso = 'mgsyncdevweb'", "yeboyebo")
        activo = resul[0][0]
    except Exception:
        activo = False

    if activo:
        getUnsynchronizedDevWeb.apply_async((r,), countdown=cdTime)
    else:
        syncppal.iface.log("Info. Proceso detenido", "mgsyncdevweb")