from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class InventorySerializer(DefaultSerializer):

    def get_data(self):    
    
        oCanales = self.get_init_value("ocanales")
        linea = self.get_init_value("linea")

        almacenes = ""
        codcanalweb = ""
        for canalweb in oCanales:
            if str(canalweb) == str(linea["ssw.codcanalweb"]):
                codcanalweb = canalweb
                aAlmacenes = oCanales[canalweb].split(",")
                almacenes = "'" + "', '".join(aAlmacenes) + "'"
        
        barcode = str(linea["ssw.barcode"])
        referencia = str(linea["aa.referencia"]) + "-" + str(linea["aa.talla"])
        
        if str(linea["aa.talla"]) == "TU":
            referencia = str(linea["aa.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_value("source_code", str(linea["ssw.codcanalweb"]))

        cant_disponible = qsatype.FLUtil.sqlSelect("stocks s LEFT JOIN param_parametros p ON 'RSTOCK_' || s.codalmacen = p.nombre", "COALESCE(SUM(disponible - COALESCE(CAST(valor AS INTEGER), 0)), 0)", "s.barcode = '" + barcode + "' and s.codalmacen IN (" + almacenes + ")")

        cant_rv = self.get_reservado(barcode, codcanalweb, almacenes)
        cant_disponible += cant_rv

        status = 0
        if cant_disponible > 0:
            status = 1

        self.set_string_value("quantity", cant_disponible)
        self.set_string_value("status", status)
        return True

    def get_reservado(self, barcode, codcanalweb, almacenes):
            return self.get_reservado_idl(barcode, codcanalweb) + self.get_reservado_pedidos(barcode, codcanalweb, almacenes) + self.get_reservado_viajestransito(barcode, almacenes) + self.get_reservado_tienda(barcode, codcanalweb, almacenes) + self.get_reservado_otros(barcode, codcanalweb, almacenes)

    @staticmethod
    def get_reservado_idl(barcode, codcanalweb):
        return qsatype.FLUtil.sqlSelect("idl_ecommerce e INNER JOIN tpv_comandas c on e.idtpv_comanda = c.idtpv_comanda INNER JOIN tpv_lineascomanda l on c.idtpv_comanda = l.idtpv_comanda left outer join eg_lineasecommerceexcluidas ex on l.idtpv_linea = ex.idtpv_linea", "COALESCE(sum(l.cantidad), 0)", "(e.confirmacionenvio = 'No' OR e.confirmacionenvio = 'Parcial') AND idlogenvio > 1 AND c.codtienda = 'AWEB' AND (c.codigo like 'WEB%' or c.codigo like 'WDV2%') AND c.fecha >= CURRENT_DATE-30 AND ex.id is null AND l.barcode = '" + str(barcode) + "' AND c.codigo in (select codcomanda from eg_logpedidosweb where fechaalta >= CURRENT_DATE-30 AND codcanalweb = '" + str(codcanalweb) + "')")

    @staticmethod
    def get_reservado_pedidos(barcode, codcanalweb, almacenes):
        return qsatype.FLUtil.sqlSelect("pedidoscli p INNER JOIN lineaspedidoscli l on p.idpedido = l.idpedido", "COALESCE(sum(l.cantidad), 0)", "p.fecha >= CURRENT_DATE-30 AND p.codserie = 'SW' AND l.barcode = '" + str(barcode) + "' AND p.codalmacen IN (" + str(almacenes) + ") AND p.observaciones IN (SELECT codcomanda FROM eg_logpedidosweb WHERE fechaalta >= CURRENT_DATE-30 AND codcanalweb = '" + codcanalweb + "')")

    @staticmethod
    def get_reservado_tienda(barcode, codcanalweb, almacenes):
        return qsatype.FLUtil.sqlSelect("tpv_comandas c INNER JOIN tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea", "COALESCE(sum(l.cantidad), 0)", "c.fecha >= CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = false AND e.pedidopreparado = false AND e.faltantecreada = false AND l.barcode = '" + str(barcode) + "' and e.codalmacen IN (" + str(almacenes) + ") AND c.codigo in (select codcomanda from eg_logpedidosweb where fechaalta >= CURRENT_DATE-30 AND codcanalweb = '" + str(codcanalweb) + "')")

    @staticmethod
    def get_reservado_otros(barcode, codcanalweb, almacenes):
        return qsatype.FLUtil.sqlSelect("tpv_comandas c inner join tpv_lineascomanda l ON c.idtpv_comanda = l.idtpv_comanda INNER JOIN eg_lineasecommerceexcluidas e ON l.idtpv_linea = e.idtpv_linea inner join eg_seguimientoenvios sg on (e.codalmacen = sg.codalmacen and c.codigo = sg.coddocumento) inner join almacenes a on e.codalmacen = a.codalmacen", "COALESCE(sum(l.cantidad), 0)", "c.fecha > CURRENT_DATE-30 AND e.pedidoanulado = false AND e.pedidoenviado = true AND e.pedidopreparado = true AND e.faltantecreada = false AND (sg.numseguimiento IS NULL OR sg.numseguimiento = '') and l.barcode = '" + str(barcode) + "' and e.codalmacen IN (" + str(almacenes) + ") AND c.codigo in (select codcomanda from eg_logpedidosweb where fechaalta >= CURRENT_DATE-30 AND codcanalweb = '" + str(codcanalweb) + "')")

    @staticmethod
    def get_reservado_viajestransito(barcode, almacenes):
        viajes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'STOCK_WEB_VIAJES_ECI_TRANSITO'")
        
        return qsatype.FLUtil.sqlSelect("tpv_lineasmultitransstock", "COALESCE(sum(cantenviada), 0)", "codalmadestino = 'AWEB' AND barcode = '" + str(barcode) + "' AND estado = 'EN TRANSITO' AND idviajemultitrans IN (" + str(viajes) + ") AND codalmadestino IN (" + almacenes + ")")


