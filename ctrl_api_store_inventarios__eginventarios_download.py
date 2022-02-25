from YBLEGACY import qsatype

from controllers.base.default.controllers.download_sync import DownloadSync
from controllers.api.store.inventarios.serializers.eginventario_serializer import EgStoreInventarioSerializer

from models.flfact_tpv.objects.egstoreinventario_raw import EgStoreInventario


class EgStoreInventariosDownload(DownloadSync):

    def __init__(self, driver, params=None):
        super().__init__("egsynciv{}".format(params["codtienda"].lower()), driver, params)
        print("------------------------ 1")
        self.origin_field = "idsincro"
        self.codtienda = params["codtienda"]
        print("------------------------ " + str(self.codtienda))

        self.set_sync_params({
            "name": params["codtienda"].lower()
        })

    def get_data(self):
        data = []
        print("///////////////// get_data")

        where = "codalmacen = '{}' AND (NOT sincronizado OR sincronizado is null) AND fecha >= '2022-01-01' AND enviado ORDER BY fecha, hora LIMIT 3".format(self.codtienda)
        print("///////////////// get_data where: " + str(where))

        cabeceras = self.execute("SELECT * FROM eg_inventarios WHERE {}".format(where))
        for cabecera in cabeceras:
            lineas = self.execute("SELECT * FROM lineasregstocks WHERE egidsincroinv = '{}'".format(cabecera["idsincro"]))

            data.append({"cabecera": cabecera, "lineas": lineas})

        return data

    def process_data(self, data):
        store_inventario_data = EgStoreInventarioSerializer().serialize(data)

        store_inventario = EgStoreInventario(store_inventario_data)
        store_inventario.save()

    def after_sync(self):
        success_records = []
        error_records = [inventario["cabecera"]["idsincro"] for inventario in self.error_data]
        after_sync_error_records = []

        for inventario in self.success_data:
            try:
                idsincro = inventario["cabecera"]["idsincro"]
                self.execute("UPDATE eg_inventarios SET sincronizado = TRUE, estado = 'TERMINADO' WHERE idsincro = '{}'".format(idsincro))
                self.driver.commit()
                success_records.append(idsincro)
            except Exception as e:
                self.after_sync_error(inventario, e)
                after_sync_error_records.append(idsincro)

        for inventario in self.error_data:
            try:
                idsincro = inventario["cabecera"]["idsincro"]
                self.execute("UPDATE eg_inventarios SET sincronizado = TRUE, estado = 'ERROR' WHERE idsincro = '{}'".format(idsincro))
                self.driver.commit()
            except Exception as e:
                self.after_sync_error(idsincro, e)
                after_sync_error_records.append(idsincro)

        if success_records:
            success_records = ", ".join(success_records)
            self.log("Exito", "Los siguientes inventarios se sincronizaron correctamente: [{}]".format(success_records))

        if error_records:
            error_records = ", ".join(error_records)
            self.log("Error", "Los siguientes inventarios no se han sincronizado correctamente: [{}]".format(error_records))

        if after_sync_error_records:
            after_sync_error_records = ", ".join(after_sync_error_records)
            self.log("Error", "Los siguientes inventarios no se han marcado como sincronizadas: [{}]".format(after_sync_error_records))

        id_sincro = qsatype.FLUtil.sqlSelect("tpv_fechasincrotienda", "id", "codtienda = '{}' AND esquema = 'INVENTARIOS'".format(self.codtienda))

        if id_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE tpv_fechasincrotienda SET fechasincro = '{}', horasincro = '{}' WHERE codtienda = '{}' AND esquema = 'INVENTARIOS'".format(self.start_date, self.start_time, self.codtienda))
        else:
            qsatype.FLSqlQuery().execSql("INSERT INTO tpv_fechasincrotienda (codtienda, esquema, fechasincro, horasincro) VALUES ('{}', 'INVENTARIOS', '{}', '{}')".format(self.codtienda, self.start_date, self.start_time))

        return self.small_sleep
