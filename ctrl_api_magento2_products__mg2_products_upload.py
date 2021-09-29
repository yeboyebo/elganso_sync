import json

from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
from controllers.api.magento2.products.serializers.configurable_product_serializer import ConfigurableProductSerializer
from controllers.api.magento2.products.serializers.simple_product_serializer import SimpleProductSerializer
from controllers.base.magento2.products.serializers.product_link_serializer import ProductLinkSerializer


class Mg2ProductsUpload(ProductsUpload):

    def __init__(self, params=None):
        super().__init__("mg2ProductsUpload", params)

        product_params = self.get_param_sincro('mg2ProductsUpload')
        self.product_url = product_params['url']
        self.product_test_url = product_params['test_url']

        link_params = self.get_param_sincro('mg2ProductsUploadLink')
        self.link_url = link_params['url']
        self.link_test_url = link_params['test_url']

        get_params = self.get_param_sincro('mg2ProductsGet')
        self.get_url = get_params['url']
        self.get_test_url = get_params['test_url']

        self.set_sync_params(self.get_param_sincro('mg2'))

        self.small_sleep = 5
        self.large_sleep = 60
        self.no_sync_sleep = 120

    def dame_almacenessincroweb(self):

        listaAlmacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'")
        if not listaAlmacenes or listaAlmacenes == "" or str(listaAlmacenes) == "None" or listaAlmacenes == None:
            return "AWEB"

        return listaAlmacenes

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "tiposincro = 'Enviar productos' AND NOT sincronizado AND website = 'MG2' ORDER BY id LIMIT 100")

        if not idlinea:
            return body

        self.idlinea = idlinea

        aListaAlmacenes = self.dame_almacenessincroweb().split(",")

        q = qsatype.FLSqlQuery()
        q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta, a.egcomposicion, a.egsignoslavado, tp.gruporemarketing, gm.descripcion, a.egcolor, ic.indicecommunity, a.codtemporada, a.anno")
        q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a ON lsc.idobjeto = a.referencia INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN indicessincrocatalogo t ON (aa.talla = t.valor and t.tipo = 'tallas') INNER JOIN indicessincrocatalogo ic ON (a.egcolor = ic.valor AND ic.tipo = 'colores') LEFT JOIN tiposprenda tp on tp.codtipoprenda = a.codtipoprenda LEFT JOIN gruposmoda gm on gm.codgrupomoda = a.codgrupomoda")
        q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, lsc.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta, a.egcomposicion, a.egsignoslavado, tp.gruporemarketing, gm.descripcion, a.egcolor, ic.indicecommunity,a.codtemporada, a.anno ORDER BY lsc.id, lsc.idobjeto, aa.barcode".format(self.idlinea))

        q.exec_()

        if not q.size():
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.referencia = body[0]["lsc.idobjeto"]

        for row in body:
            disponible = qsatype.FLUtil.sqlSelect("stocks", "sum(disponible)", "barcode = '" + row["aa.barcode"] + "' AND disponible > 0 AND codalmacen IN ('" + "', '".join(aListaAlmacenes) + "')")

            if disponible and float(disponible) > 0:
                self.stock_disponible = True
            self.indice_tallas.append(row["t.indicecommunity"])

        return body

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        data[0]["indice_tallas"] = self.indice_tallas
        data[0]["stock_disponible"] = self.stock_disponible
        data[0]["store_id"] = "all"

        configurable_product_default = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "ES"
        configurable_product_es = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "EN"
        configurable_product_en = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "FR"
        configurable_product_fr = self.get_configurable_product_serializer().serialize(data[0])
        simple_products_default = []
        simple_products_es = []
        simple_products_en = []
        simple_products_fr = []
        product_links = []

        for row in data:
            row["store_id"] = "all"
            simple_products_default.append(self.get_simple_product_serializer().serialize(row))
            row["store_id"] = "ES"
            simple_products_es.append(self.get_simple_product_serializer().serialize(row))
            row["store_id"] = "EN"
            simple_products_en.append(self.get_simple_product_serializer().serialize(row))
            row["store_id"] = "FR"
            simple_products_fr.append(self.get_simple_product_serializer().serialize(row))
            product_links.append(self.get_product_link_serializer().serialize(row))

        if not configurable_product_default and not simple_products_default and not product_links:
            return False

        if product_links[0] == False:
            product_links = False

        return {
            "configurable_product_default": configurable_product_default,
            "configurable_product_es": configurable_product_es,
            "configurable_product_en": configurable_product_en,
            "configurable_product_fr": configurable_product_fr,
            "simple_products_default": simple_products_default,
            "simple_products_es": simple_products_es,
            "simple_products_en": simple_products_en,
            "simple_products_fr": simple_products_fr,
            "product_links": product_links,
        }

    def get_configurable_product_serializer(self):
        return ConfigurableProductSerializer()

    def get_simple_product_serializer(self):
        return SimpleProductSerializer()

    def get_product_link_serializer(self):
        return ProductLinkSerializer()

    def send_data(self, data):
        product_url = self.product_url if self.driver.in_production else self.product_test_url
        link_url = self.link_url if self.driver.in_production else self.link_test_url
        get_url = self.get_url if self.driver.in_production else self.get_test_url

        if data["configurable_product_default"]:
            self.send_request("post", url=product_url.format("all"), data=json.dumps(data["configurable_product_default"]))

        if data["configurable_product_es"]:
            self.send_request("post", url=product_url.format("es"), data=json.dumps(data["configurable_product_es"]))
            self.send_request("post", url=product_url.format("es_cn"), data=json.dumps(data["configurable_product_es"]))
            self.send_request("post", url=product_url.format("intl_es"), data=json.dumps(data["configurable_product_es"]))
            self.send_request("post", url=product_url.format("pt_es"), data=json.dumps(data["configurable_product_es"]))

        if data["configurable_product_en"]:
            self.send_request("post", url=product_url.format("en"), data=json.dumps(data["configurable_product_en"]))
            self.send_request("post", url=product_url.format("intl_en"), data=json.dumps(data["configurable_product_en"]))
            self.send_request("post", url=product_url.format("intl_uk"), data=json.dumps(data["configurable_product_en"]))
            self.send_request("post", url=product_url.format("pt_en"), data=json.dumps(data["configurable_product_en"]))

        if data["configurable_product_fr"]:
            self.send_request("post", url=product_url.format("fr"), data=json.dumps(data["configurable_product_fr"]))
            self.send_request("post", url=product_url.format("intl_fr"), data=json.dumps(data["configurable_product_fr"]))
            self.send_request("post", url=product_url.format("fr_fr"), data=json.dumps(data["configurable_product_fr"]))

        if data["simple_products_default"]:
            for simple_product in data["simple_products_default"]:
                self.send_request("post", url=product_url.format("all"), data=json.dumps(simple_product))

        if data["simple_products_es"]:
            for simple_product in data["simple_products_es"]:
                self.send_request("post", url=product_url.format("es"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("es_cn"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("intl_es"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("pt_es"), data=json.dumps(simple_product))

        if data["simple_products_en"]:
            for simple_product in data["simple_products_en"]:
                self.send_request("post", url=product_url.format("en"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("intl_en"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("intl_uk"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("pt_en"), data=json.dumps(simple_product))

        if data["simple_products_fr"]:
            for simple_product in data["simple_products_fr"]:
                self.send_request("post", url=product_url.format("fr"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("intl_fr"), data=json.dumps(simple_product))
                self.send_request("post", url=product_url.format("fr_fr"), data=json.dumps(simple_product))

        if data["product_links"]:
            for product_link in data["product_links"]:
                print(str(json.dumps(product_link)))
                self.send_request("post", url=link_url.format(data["configurable_product_default"]["product"]["sku"]), data=json.dumps(product_link))

        try:
            self.send_request("get", url=get_url.format(self.referencia))
        except Exception as e:
            return data

        return data

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))
        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        if not lineas_no_sincro:
            qsatype.FLSqlQuery().execSql("UPDATE sincro_catalogo SET ptesincro = FALSE WHERE idsincro = '{}'".format(self.idsincro))

        self.log("Exito", "Productos sincronizados correctamente (referencia: {})".format(self.referencia))

        return self.small_sleep
