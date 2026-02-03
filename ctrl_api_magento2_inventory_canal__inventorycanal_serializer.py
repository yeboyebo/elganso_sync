from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class InventorySerializer(DefaultSerializer):

    def get_data(self):    
    
        oCanales = self.get_init_value("ocanales")
        linea = self.get_init_value("linea")

        almacenes = ""
        codcanalweb = ""
        barcode = str(linea["ssw.barcode"])
        for canalweb in oCanales:
            if str(canalweb) == str(linea["ssw.codcanalweb"]):
                codcanalweb = canalweb
                aAlmacenes = oCanales[canalweb].split(",")
                for almacen in aAlmacenes:
                    filtro_articulo = str(qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'FA_" + almacen + "'"))
                    if filtro_articulo and filtro_articulo != "None" and filtro_articulo != "":
                        existe_barcode = str(qsatype.FLUtil.sqlSelect("stocks s INNER JOIN articulos a ON s.referencia = a.referencia", "s.barcode", "s.barcode = '" + barcode + "' and " + filtro_articulo))
                        if existe_barcode and  existe_barcode != "None" and existe_barcode != "":
                            if almacenes == "":
                                almacenes = "'" + almacen + "'"
                            else:
                                almacenes += ",'" + almacen + "'"

        if almacenes == "":
            return False
        
        referencia = str(linea["aa.referencia"]) + "-" + str(linea["aa.talla"])
        
        if str(linea["aa.talla"]) == "TU":
            referencia = str(linea["aa.referencia"])

        self.set_string_value("sku", referencia)
        self.set_string_value("source_code", str(linea["ssw.codcanalweb"]))
        self.set_string_value("stock_id", str(linea["st.idstockmagento"]))

        cant_disponible = qsatype.FLUtil.sqlSelect("stocks s LEFT JOIN param_parametros p ON 'RSTOCK_' || s.codalmacen = p.nombre", "COALESCE(SUM(CASE WHEN (s.disponible-COALESCE(CAST(p.valor as integer),0)) > 0 THEN (s.disponible-COALESCE(CAST(p.valor as integer),0)) ELSE 0 END), 0)", "s.barcode = '" + barcode + "' and s.codalmacen IN (" + almacenes + ")")

        if not cant_disponible:
            cant_disponible = 0

        status = 0
        tallas_agotadas = 0
        if cant_disponible > 0:
            status = 1
        else:
            tallas_agotadas = qsatype.FLUtil.sqlSelect("stocks s LEFT JOIN param_parametros p ON 'RSTOCK_' || s.codalmacen = p.nombre", "CASE WHEN (COALESCE(SUM(CASE WHEN (s.disponible-COALESCE(CAST(p.valor as integer),0)) > 0 THEN (s.disponible-COALESCE(CAST(p.valor as integer),0)) ELSE 0 END), 0)) > 0 THEN 0 ELSE 1 END", "s.referencia = '" + str(linea["aa.referencia"]) + "' and s.codalmacen IN (" + almacenes + ")")

        self.set_string_value("quantity", cant_disponible)
        self.set_string_value("status", status)
        self.set_string_value("tallas_agotadas", int(tallas_agotadas))
        return True
