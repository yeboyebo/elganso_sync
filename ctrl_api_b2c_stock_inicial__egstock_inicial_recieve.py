from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.controllers.recieve_sync import RecieveSync


class EgStockInicialRecieve(RecieveSync):

    def __init__(self, params=None):
        super().__init__("mgsyncstockinicial", params)

    def sync(self):
        data = self.params
        if "sku" in data:
            listaAlmacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'")
            if not listaAlmacenes or listaAlmacenes == "" or str(listaAlmacenes) == "None" or listaAlmacenes == None:
                listaAlmacenes =  "AWEB"
            listaAlmacenes = listaAlmacenes.split(",")
            for sku in data["sku"]:
                for i in range(len(listaAlmacenes)):
                    q = qsatype.FLSqlQuery()
                    q.setSelect("s.idstock")
                    q.setFrom("stocks s")
                    q.setWhere("s.referencia = '" + sku + "' AND s.codalmacen = '" + listaAlmacenes[i] + "'")

                    q.exec_()

                    if not q.size():
                        raise NameError("No se encuentran registros de stock para ninguna de las referencias.")

                    while q.next():
                        if not qsatype. FactoriaModulos.get("flfactalma").iface.marcaSincroStockWeb(q.value("s.idstock"), False, False, listaAlmacenes[i]):
                            raise NameError(" No se ha podido marcar el stock web para el idstock: " + str(q.value("s.idstock")) + " y el almacén: " + str(listaAlmacenes[i]))
        else:
            raise NameError("No se han pasado referencias por parámetro.")

        self.log("Exito", "Stocks marcados correctamente")
        return {
            "data": {"log": self.logs},
            "status": 200
        }