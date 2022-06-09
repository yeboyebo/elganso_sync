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
        self.set_string_value("stock_id", str(linea["st.idstockmagento"]))

        cant_disponible = qsatype.FLUtil.sqlSelect("stocks s LEFT JOIN param_parametros p ON 'RSTOCK_' || s.codalmacen = p.nombre", "COALESCE(SUM(CASE WHEN (s.disponible-COALESCE(CAST(p.valor as integer),0)) > 0 THEN (s.disponible-COALESCE(CAST(p.valor as integer),0)) ELSE 0 END), 0)", "s.barcode = '" + barcode + "' and s.codalmacen IN (" + almacenes + ")")

        status = 0
        if cant_disponible > 0:
            status = 1

        self.set_string_value("quantity", cant_disponible)
        self.set_string_value("status", status)
        return True



