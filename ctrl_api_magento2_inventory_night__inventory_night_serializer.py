from YBLEGACY import qsatype
from YBLEGACY.constantes import *
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class InventoryNightSerializer(DefaultSerializer):

    def get_data(self):

        referencia = str(self.init_data["aa.referencia"]) + "-" + str(self.init_data["aa.talla"])
        if str(self.init_data["aa.talla"]) == "TU":
            referencia = str(self.init_data["aa.referencia"])

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
            raise NameError("Error. Existe un registro cuyo almacén no está en la lista de almacenes de sincronizacion con Magento. " + str(self.init_data["ssw.idssw"]))

        cant_disponible = qty
        if str(str(self.init_data["s.codalmacen"])) != "AWEB":
            cant_reservada = self.get_cantreservada(str(self.init_data["s.codalmacen"]))
            cant_disponible = parseFloat(qty) - parseFloat(cant_reservada)
            if cant_disponible < 0:
                cant_disponible = 0

        self.set_string_value("quantity", cant_disponible)
        self.set_string_value("status", status)
        return True

    def dame_stock(self, disponible):
        if not disponible or isNaN(disponible) or disponible < 0:
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
