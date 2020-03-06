from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.controllers.upload_sync import UploadSync


class EgStockUpload(UploadSync):

    _ssw = None

    def __init__(self, driver, params=None):
        super().__init__("mgsyncstock", driver, params)

        self.set_sync_params(self.get_param_sincro('b2c'))
        self.set_sync_params(self.get_param_sincro('b2cStockUpload'))

    def get_data(self):
        q = qsatype.FLSqlQuery()
        q.setSelect("aa.referencia, aa.talla, aa.barcode, s.disponible, s.cantidad, s.idstock, ssw.idssw, s.codalmacen")
        q.setFrom("articulos a INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN stocks s ON aa.barcode = s.barcode LEFT OUTER JOIN eg_sincrostockweb ssw ON s.idstock = ssw.idstock")
        q.setWhere("NOT ssw.sincronizado OR ssw.sincronizado = false ORDER BY aa.referencia LIMIT 1000")

        q.exec_()

        body = []
        if not q.size():
            return body

        while q.next():
            sku = self.dame_sku(q.value("aa.referencia"), q.value("aa.talla"))
            # qty = parseInt(self.dame_stock(q.value("s.disponible")))
            hoy = qsatype.Date()
            stockReservado = qsatype.FLUtil.sqlSelect("eg_anulacionstockreservado", "idstock", "idstock = {} AND activo = true AND fechatope >= '{}'".format(q.value("s.idstock"), hoy))
            if stockReservado and stockReservado != 0:
                cantA = parseInt(qsatype.FLUtil.sqlSelect("eg_anulacionstockreservado", "cantstockreservadoanulado", "idstock = {} AND activo = true AND fechatope >= '{}'".format(q.value("s.idstock"), hoy)))
                if not cantA:
                    cantA = 0

                qty = parseInt(self.dame_stock(q.value("s.disponible"))) + cantA
            else:
                qty = parseInt(self.dame_stock(q.value("s.disponible")))

            aListaAlmacenes = self.dame_almacenessincroweb().split(",")
            if q.value("s.codalmacen") not in aListaAlmacenes:
                raise NameError("Error. Existe un registro cuyo almacén no está en la lista de almacenes de sincronización con Magento. " + str(q.value("ssw.idssw")))

            cant_disponible = qty
            if str(q.value("s.codalmacen")) != "AWEB":
                cant_reservada = self.get_cantreservada(q.value("s.codalmacen"))
                cant_disponible = parseFloat(qty) - parseFloat(cant_reservada)
                if cant_disponible < 0:
                    cant_disponible = 0

            body.append({"sku": sku, "qty": cant_disponible, "sincroStock": True, "almacen": q.value("s.codalmacen")})

            if not self._ssw:
                self._ssw = ""
            else:
                self._ssw += ","
            self._ssw += str(q.value("ssw.idssw"))

        return body

    def dame_sku(self, referencia, talla):
        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def dame_stock(self, disponible):
        if not disponible or isNaN(disponible) or disponible < 0:
            return 0

        return disponible

    def after_sync(self, response_data=None):
        if response_data and "request_id" in response_data:
            qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockweb SET sincronizado = true WHERE idssw IN ({})".format(self._ssw))
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = 'AWEB' AND esquema = 'STOCK_WEB'".format(self.start_date, self.start_time))
            self.log("Éxito", "Stock sincronizado correctamente (id: {})".format(response_data["request_id"]))
        else:
            raise NameError("No se recibió una respuesta correcta del servidor")

        return self.small_sleep

    def dame_almacenessincroweb(self):

        listaAlmacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'")
        if not listaAlmacenes or listaAlmacenes == "" or str(listaAlmacenes) == "None" or listaAlmacenes == None:
            return "AWEB"

        return listaAlmacenes

    def get_cantreservada(self, codalmacen):

        cant_reservada = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'RSTOCK_" + str(codalmacen) + "'")
        if not cant_reservada or cant_reservada == "" or str(cant_reservada) == "None" or cant_reservada == None:
            return 0

        return parseFloat(cant_reservada)

