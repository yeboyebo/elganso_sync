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
        self.articulos_sin_sincronizar = ""

    def get_db_data(self):
        body = []
        self.stores_id = []
        self.cod_plan = qsatype.FLUtil.sqlSelect("lineassincro_planpreciosprerebajas", "codplan", "sincronizado = false")
        if not self.cod_plan:
            return body

        s = qsatype.FLSqlQuery()
        s.setSelect("at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento")
        s.setFrom("lineassincro_planpreciosprerebajas pr INNER JOIN atributosarticulos at ON pr.sku = at.referencia INNER JOIN eg_tiendasplanprecios t ON pr.codplan = t.codplan INNER JOIN mg_storeviews mg ON mg.egcodtiendarebajas = t.codtienda")
        s.setWhere("pr.codplan = '{}' AND (pr.descripcionsincro IS NULL OR pr.descripcionsincro = '') GROUP BY at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento ORDER BY at.referencia, mg.idmagento".format(self.cod_plan))
        # s.setWhere("pr.sincronizado = false AND pr.codplan = '" + str(self.cod_plan) + "' AND pr.sku in (SELECT sku from lineassincro_planpreciosprerebajas WHERE codplan = '" + str(self.cod_plan) + "' AND sincronizado = false ORDER BY sku LIMIT 1) GROUP BY at.referencia,at.talla,pr.pvp,pr.desde,mg.idmagento ORDER BY at.referencia, mg.idmagento")
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
            self.sku = row["at.referencia"]
            if referencia == "":
                referencia = row["at.referencia"]
                store_id = row["mg.idmagento"]
                new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))

            if referencia != row["at.referencia"]:
                referencia = row["at.referencia"]
                new_rebaja.append(self.get_configurable_prerebajas_serializer().serialize(row))
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
        print("DATA: " + json.dumps(data))
        print("URL: " + product_url)
        try:
            result = self.send_request("post", url=product_url, data=json.dumps(data))
            """result = {
                "result": True,
                "mssg": "{\"articulos_sincronizados\":\"Se han sincronizado 14 referencias\",\"articulos_no_existentes_en_magento\":[\"NOEXIST\",\"NOEXIST\"]}"
            }"""
            print(str(result))
            print(str(result["result"]))
            articulos_sincro = json.loads(result["mssg"])
            print(str(articulos_sincro["articulos_no_existentes_en_magento"]))  
            print(len(articulos_sincro["articulos_no_existentes_en_magento"]))  
            for articulo in range(len(articulos_sincro["articulos_no_existentes_en_magento"])):
                print(articulo)
                if self.articulos_sin_sincronizar == "":
                    self.articulos_sin_sincronizar = "'" + articulos_sincro["articulos_no_existentes_en_magento"][articulo] + "'"
                else:
                    self.articulos_sin_sincronizar += ",'" + articulos_sincro["articulos_no_existentes_en_magento"][articulo] + "'"
            print(self.articulos_sin_sincronizar)
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

        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET sincronizado = TRUE, descripcionsincro = 'CORRECTO' WHERE codplan = '" + str(self.cod_plan) + "' AND sku IN ('" + str(self.sku) + "') AND sku NOT IN (" + str(self.articulos_sin_sincronizar) + ")")
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_planpreciosprerebajas SET descripcionsincro = 'No existe en Magento' WHERE codplan = '" + str(self.cod_plan) + "' AND sku IN (" + str(self.articulos_sin_sincronizar) + ")")

        self.log("Exito", "Plan Precios PreRebajas " + str(self.cod_plan) + " y ref.: " + str(self.sku) + " sincronizado correctamente.")

        return self.small_sleep
