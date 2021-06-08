import json

from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
from controllers.api.magento2.products.serializers.configurable_product_serializer import ConfigurableProductSerializer
from controllers.api.magento2.products.serializers.simple_product_serializer import SimpleProductSerializer


class Mg2ProductsUpload(ProductsUpload):

    def __init__(self, params=None):
        super().__init__("mg2ProductsUpload", params)

        product_params = self.get_param_sincro('mg2ProductsUpload')
        self.product_url = product_params['url']
        self.product_test_url = product_params['test_url']

        link_params = self.get_param_sincro('mg2ProductsUploadLink')
        self.link_url = link_params['url']
        self.link_test_url = link_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar productos' AND NOT sincronizado AND website = 'MG2' ORDER BY id LIMIT 1")

        if not idlinea:
            return body

        self.idlinea = idlinea

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, s.disponible, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a ON lsc.idobjeto = a.referencia INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia LEFT JOIN stocks s ON aa.barcode = s.barcode INNER JOIN indicessincrocatalogo t ON aa.talla = t.valor")
        q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, s.disponible, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.referencia = body[0]["lsc.idobjeto"]

        for row in body:
            if str(row["s.disponible"]) != "None" and float(row["s.disponible"]) > 0:
                self.stock_disponible = True
            self.indice_tallas.append(row["t.indicecommunity"])

        return body

    def get_configurable_product_serializer(self):
        return ConfigurableProductSerializer()

    def get_simple_product_serializer(self):
        return SimpleProductSerializer()

    def send_data(self, data):
        product_url = self.product_url if self.driver.in_production else self.product_test_url
        link_url = self.link_url if self.driver.in_production else self.link_test_url
        if data["configurable_product_default"]:
            self.send_request("post", url=product_url.format("all"), data=json.dumps(data["configurable_product_default"]))
        
        if data["configurable_product_es"]:
            self.send_request("post", url=product_url.format("es"), data=json.dumps(data["configurable_product_es"]))

        if data["configurable_product_en"]:
            self.send_request("post", url=product_url.format("en"), data=json.dumps(data["configurable_product_en"]))

        if data["simple_products_default"]:
            for simple_product in data["simple_products_default"]:
                self.send_request("post", url=product_url.format("all"), data=json.dumps(simple_product))

        if data["simple_products_es"]:
            for simple_product in data["simple_products_es"]:
                self.send_request("post", url=product_url.format("es"), data=json.dumps(simple_product))

        if data["simple_products_en"]:
            for simple_product in data["simple_products_en"]:
                self.send_request("post", url=product_url.format("en"), data=json.dumps(simple_product))

        if data["product_links"]:
            for product_link in data["product_links"]:
                self.send_request("post", url=link_url.format(data["configurable_product_default"]["product"]["sku"]), data=json.dumps(product_link))
        return data

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))
        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        if not lineas_no_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = FALSE WHERE idsincro = '{}'".format(self.idsincro))

        self.log("Exito", "Productos sincronizados correctamente (referencia: {})".format(self.referencia))

        return self.small_sleep
