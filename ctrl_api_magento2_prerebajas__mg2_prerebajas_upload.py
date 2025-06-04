import json

from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
from controllers.api.magento2.prerebajas.serializers.simple_prerebajas_serializer import SimplePrerebajasSerializer
from controllers.api.magento2.prerebajas.serializers.configurable_prerebajas_serializer import ConfigurablePrerebajasSerializer


class Mg2PrerebajasUpload(ProductsUpload):

    error = False

    def __init__(self, params=None):
        super().__init__("mg2Prerebajas", params)

        product_params = self.get_param_sincro('mg2PreRebajas')
        self.product_url = product_params['url']
        self.product_test_url = product_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 1
        self.cod_plan = ""
        self.sku = ""
        self.stores_id = []
        self.articulos_no_existentes = ""
        self.articulos_fallo_guardar = ""

    def get_db_data(self):
        body = []
        self.stores_id = []
        self.cod_plan = qsatype.FLUtil.sqlSelect("lineassincro_planpreciosprerebajas", "codplan", "sincronizado = false")
        if not self.cod_plan:
            return body

        s = qsatype.FLSqlQuery()
        s.setSelect("at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento")
        s.setFrom("lineassincro_planpreciosprerebajas pr INNER JOIN atributosarticulos at ON pr.sku = at.referencia INNER JOIN eg_tiendasplanprecios t ON pr.codplan = t.codplan INNER JOIN mg_storeviews mg ON mg.egcodtiendarebajas = t.codtienda")
        # s.setWhere("pr.codplan = '{}' AND (pr.descripcionsincro IS NULL OR pr.descripcionsincro = '') GROUP BY at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento ORDER BY at.referencia, mg.idmagento".format(self.cod_plan))
        s.setWhere("pr.sincronizado = false AND pr.codplan = '" + str(self.cod_plan) + "' AND pr.sku in (SELECT sku from lineassincro_planpreciosprerebajas WHERE codplan = '" + str(self.cod_plan) + "' AND sincronizado = false ORDER BY sku LIMIT 50) GROUP BY at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento ORDER BY at.referencia, mg.idmagento")
        s.exec_()

        body = self.fetch_query(s)
        self.error = False

        return body

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        new_rebaja = []
        referencia = ""
        store_id = ""
        for row in data:
            if referencia == "":
                referencia = row["at.referencia"]
                store_id = row["mg.idmagento"]
                new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))
                if self.sku == "":
                    self.sku = "'" + row["at.referencia"] + "'"
                else:
                    self.sku += ",'" + row["at.referencia"] + "'"

            if referencia != row["at.referencia"]:
                referencia = row["at.referencia"]
                new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))
                if self.sku == "":
                    self.sku = "'" + row["at.referencia"] + "'"
                else:
                    self.sku += ",'" + row["at.referencia"] + "'"
            else:
                if store_id != row["mg.idmagento"]:
                    new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))
                    store_id = row["mg.idmagento"]

            new_rebaja.append(self.get_simple_prerebajas_serializer().serialize(row))

        return {
            "promoPrices": new_rebaja
        }

    def get_simple_prerebajas_serializer(self):
        return SimplePrerebajasSerializer()

    def get_configurable_prerebajas_serializer(self):
        return ConfigurablePrerebajasSerializer()

    def send_data(self, data):
        product_url = self.product_url if self.driver.in_production else self.product_test_url
        
        for idx in range(len(data["promoPrices"])):
            del data["promoPrices"][idx]["children"]

        try:
            result = self.send_request("post", url=product_url, data=json.dumps(data))
 
            articulos_sincro = json.loads(result["mssg"])
            if "articulos_no_existentes_en_magento" in articulos_sincro:
                for articulo in range(len(articulos_sincro["articulos_no_existentes_en_magento"])):
                    if self.articulos_no_existentes == "":
                        self.articulos_no_existentes = "'" + articulos_sincro["articulos_no_existentes_en_magento"][articulo] + "'"
                    else:
                        self.articulos_no_existentes += ",'" + articulos_sincro["articulos_no_existentes_en_magento"][articulo] + "'"

            if "articulos_fallo_guardar" in articulos_sincro:
                for articulo in range(len(articulos_sincro["articulos_fallo_guardar"])):
                    if self.articulos_fallo_guardar == "":
                        self.articulos_fallo_guardar = "'" + articulos_sincro["articulos_fallo_guardar"][articulo] + "'"
                    else:
                        self.articulos_fallo_guardar += ",'" + articulos_sincro["articulos_fallo_guardar"][articulo] + "'"
                    
            if(str(result) == "False"):
                self.error = True
        except Exception as e:
            print("exception")
            self.error = True

        return True

    def after_sync(self, response_data=None):

        if self.error:
            self.log("Error", "No se pudo sincronizar las Pre-rebajas del planificador: " + str(self.cod_plan) + " y ref.:" + str(self.sku) + ")")
            return self.small_sleep

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET sincronizado = TRUE, descripcionsincro = 'CORRECTO' WHERE codplan = '" + str(self.cod_plan) + "' AND sku IN (" + str(self.sku) + ")")

        if str(self.articulos_no_existentes) != "":
            qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET descripcionsincro = 'Articulo no existe en Magento' WHERE codplan = '" + str(self.cod_plan) + "' AND sku IN (" + str(self.articulos_no_existentes) + ")")
        
        if str(self.articulos_fallo_guardar) != "":
            qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET descripcionsincro = 'Fallo al guardar el articulo' WHERE codplan = '" + str(self.cod_plan) + "' AND sku IN (" + str(self.articulos_fallo_guardar) + ")")

        self.log("Exito", "Plan Precios PreRebajas " + str(self.cod_plan) + " sincronizado correctamente.")

        return self.small_sleep
