from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class InventorySerializer(DefaultSerializer):

    def get_data(self):

        barcode = str(self.init_data["s.barcode"])
        referencia = str(self.init_data["s.referencia"]) + "-" + str(self.init_data["s.talla"])
        if str(self.init_data["s.talla"]) == "TU":
            referencia = str(self.init_data["s.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_value("source_code", str(self.init_data["s.codalmacen"]))
        status = 0
        if self.init_data["s.disponible"] > 0:
            status = 1

        hoy = qsatype.Date()
        stockReservado = qsatype.FLUtil.sqlSelect("eg_anulacionstockreservado", "idstock", "idstock = {} AND activo = true AND fechatope >= '{}'".format(self.init_data["s.idstock"], hoy))
        if stockReservado and stockReservado != 0:
            cantA = parseInt(qsatype.FLUtil.sqlSelect("eg_anulacionstockreservado", "cantstockreservadoanulado", "idstock = {} AND activo = true AND fechatope >= '{}'".format(self.init_data["s.idstock"], hoy)))
            if not cantA:
                cantA = 0

            qty = parseInt(self.dame_stock(self.init_data["s.disponible"])) + cantA
        else:
            qty = parseInt(self.dame_stock(self.init_data["s.disponible"]))

        aListaAlmacenes = self.dame_almacenessincroweb().split(",")
        if str(self.init_data["s.codalmacen"]) not in aListaAlmacenes:
            raise NameError("Error. Existe un registro cuyo almacén no está en la lista de almacenes de sincronización con Magento. " + str(self.init_data["ssw.idssw"]))

        cant_disponible = qty
        if str(str(self.init_data["s.codalmacen"])) != "AWEB":
            cant_reservada = self.get_cantreservada(str(self.init_data["s.codalmacen"]))
            cant_disponible = parseFloat(qty) - parseFloat(cant_reservada)

        cant_rv = self.get_reservado(barcode, str(self.init_data["s.codalmacen"]))
        cant_disponible += cant_rv

        self.set_string_value("quantity", cant_disponible)
        self.set_string_value("status", status)
        return True

    def dame_stock(self, disponible):
        if not disponible or isNaN(disponible):
            return 0

        return disponible

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

    def get_reservado(self, barcode, almacen):
        if self.tipo_almacen(almacen) == "Principal":
            return self.get_reservado_idl(barcode) + self.get_reservado_pedidos(barcode)
        elif self.tipo_almacen(almacen) == "Tienda":
            return self.get_reservado_tienda(barcode, almacen)
        elif self.tipo_almacen(almacen) == "Otros":
            return self.get_reservado_otros(barcode, almacen)

    @staticmethod
    def get_reservado_idl(barcode):

        return qsatype.FLUtil.sqlSelect("idl_ecommerce e INNER JOIN tpv_comandas c on e.idtpv_comanda = c.idtpv_comanda INNER JOIN tpv_lineascomanda l on c.idtpv_comanda = l.idtpv_comanda left outer join eg_lineasecommerceexcluidas ex on l.idtpv_linea = ex.idtpv_linea", "COALESCE(sum(l.cantidad), 0)", "(e.confirmacionenvio = 'No' OR e.confirmacionenvio = 'Parcial') AND idlogenvio > 0 AND idlogenvio <> 999999 AND c.codtienda = 'AWEB' AND (c.codigo like 'WEB%' or c.codigo like 'WDV2%') AND c.fecha >= CURRENT_DATE-30 AND ex.id is null AND l.barcode = '" + str(barcode) + "'")

    @staticmethod
    def get_reservado_pedidos(barcode):
        return qsatype.FLUtil.sqlSelect("pedidoscli p INNER JOIN lineaspedidoscli l on p.idpedido = l.idpedido", "COALESCE(sum(l.cantidad), 0)", "p.codserie = 'SW' AND l.barcode = '" + str(barcode) + "'")

    @staticmethod
    def get_reservado_tienda(barcode, almacen):
        return qsatype.FLUtil.sqlSelect("tpv_comandas c INNER JOIN tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea", "COALESCE(sum(l.cantidad), 0)", "c.fecha > CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = false AND e.pedidopreparado = false AND e.faltantecreada = false AND l.barcode = '" + str(barcode) + "' and e.codalmacen = '" + str(almacen) + "'")

    @staticmethod
    def get_reservado_otros(barcode, almacen):
        return qsatype.FLUtil.sqlSelect("tpv_comandas c inner join tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea inner join eg_seguimientoenvios sg on (e.codalmacen = sg.codalmacen and c.codigo = sg.coddocumento) inner join almacenes a on e.codalmacen = a.codalmacen", "COALESCE(sum(l.cantidad), 0)", "c.fecha > CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = true AND e.pedidopreparado = true AND e.faltantecreada = false AND (sg.numseguimiento IS NULL OR sg.numseguimiento = '') and l.barcode = '" + str(barcode) + "' and e.codalmacen = '" + str(almacen) + "'")

    @staticmethod
    def tipo_almacen(almacen):
        if almacen == "AWEB":
            return "Principal"
        elif qsatype.FLUtil.sqlSelect("almacenes", "codalmacen", "codalmacen = '" + str(almacen) + "' AND codalmacen <> 'AWEB' AND codalmacen <> 'LFWB' AND lower(egtipoalmacen) <> 'community'"):
            return "Tienda"

        return "Otros"
