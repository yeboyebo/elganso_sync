import json

from YBLEGACY import qsatype

from controllers.base.magento2.products.controllers.products_upload import ProductsUpload
from controllers.api.magento2.products.serializers.configurable_product_serializer import ConfigurableProductSerializer
from controllers.api.magento2.products.serializers.simple_product_serializer import SimpleProductSerializer
from controllers.base.magento2.products.serializers.product_link_serializer import ProductLinkSerializer


class Mg2ProductsUpload(ProductsUpload):

    indice_colores = None
    indiceconfigurable = 0

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

        self.small_sleep = 2
        self.indice_colores = []
        self.indice_tallas = []
        self.sincronizarsimple = True

    def dame_almacenessincroweb(self):

        listaAlmacenes = qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'ALMACENES_SINCRO'")
        if not listaAlmacenes or listaAlmacenes == "" or str(listaAlmacenes) == "None" or listaAlmacenes == None:
            return "AWEB"

        return listaAlmacenes

    def get_db_data(self):
        body = []

        idlinea = qsatype.FLUtil.sqlSelect("lineassincro_catalogo l inner join articulos a on l.idobjeto = a.referencia", "l.id", "l.tiposincro = 'Enviar productos' AND NOT l.sincronizado AND l.website = 'MG2' ORDER BY a.configurable DESC,l.id LIMIT 100")

        if not idlinea:
            return body

        self.idlinea = idlinea

        aListaAlmacenes = self.dame_almacenessincroweb().split(",")

        refConfig = qsatype.FLUtil.sqlSelect("articulos a INNER JOIN lineassincro_catalogo l on a.referencia = l.idobjeto", "referenciaconfigurable", "l.id = " + str(idlinea))

        q = qsatype.FLSqlQuery()

        if (str(refConfig)) != "None":
            q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, a.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta, a.egcomposicion, a.egsignoslavado, tp.gruporemarketing, gm.descripcion, a.egcolor, ic.indicecommunity, a.codtemporada, a.anno, a.mgmasinfo, a.mgtallamodelo, a.mgmedidasmodelo, a.referencia, a3.configurable, a3.referenciaconfigurable, aa.referencia")
            q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a3 ON lsc.idobjeto = a3.referencia INNER JOIN articulos a2 on a3.referenciaconfigurable = a2.referencia INNER JOIN articulos a on a2.referencia = a.referenciaconfigurable INNER JOIN atributosarticulos aa ON (a.referencia = aa.referencia) INNER JOIN indicessincrocatalogo t ON (aa.talla = t.valor and t.tipo = 'tallas') INNER JOIN indicessincrocatalogo ic ON (a.egcolor = ic.valor AND ic.tipo = 'colores') LEFT JOIN tiposprenda tp on tp.codtipoprenda = a.codtipoprenda LEFT JOIN gruposmoda gm on gm.codgrupomoda = a.codgrupomoda")
            q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, a.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta, a.egcomposicion, a.egsignoslavado, tp.gruporemarketing, gm.descripcion, a.egcolor, ic.indicecommunity, a.codtemporada, a.anno, a.mgmasinfo, a.mgtallamodelo, a.mgmedidasmodelo, a.referencia, a3.configurable, a3.referenciaconfigurable, aa.referencia".format(self.idlinea))
        else:
            q.setSelect("lsc.id, lsc.idsincro, lsc.idobjeto, a.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta, a.egcomposicion, a.egsignoslavado, tp.gruporemarketing, gm.descripcion, a.egcolor, ic.indicecommunity, a.codtemporada, a.anno, a.mgmasinfo, a.mgtallamodelo, a.mgmedidasmodelo, a.referencia, a.configurable, a.referenciaconfigurable, aa.referencia")
            q.setFrom("lineassincro_catalogo lsc INNER JOIN articulos a ON lsc.idobjeto = a.referencia INNER JOIN atributosarticulos aa ON a.referencia = aa.referencia INNER JOIN indicessincrocatalogo t ON (aa.talla = t.valor and t.tipo = 'tallas') INNER JOIN indicessincrocatalogo ic ON (a.egcolor = ic.valor AND ic.tipo = 'colores') LEFT JOIN tiposprenda tp on tp.codtipoprenda = a.codtipoprenda LEFT JOIN gruposmoda gm on gm.codgrupomoda = a.codgrupomoda")
            q.setWhere("lsc.id = {} GROUP BY lsc.id, lsc.idsincro, lsc.idobjeto, a.descripcion, a.pvp, a.peso, aa.barcode, aa.talla, t.indicecommunity, a.mgdescripcion, a.mgdescripcioncorta, a.egcomposicion, a.egsignoslavado, tp.gruporemarketing, gm.descripcion, a.egcolor, ic.indicecommunity, a.codtemporada, a.anno, a.mgmasinfo, a.mgtallamodelo, a.mgmedidasmodelo, a.referencia, a.configurable, a.referenciaconfigurable, aa.referencia".format(self.idlinea))

        q.exec_()

        if not q.size():
            qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))
            return body

        body = self.fetch_query(q)
        self.idsincro = body[0]["lsc.idsincro"]
        self.referencia = body[0]["lsc.idobjeto"]

        i = 0
        print(str(i))
        for row in body:
            disponible = qsatype.FLUtil.sqlSelect("stocks", "sum(disponible)", "barcode = '" + row["aa.barcode"] + "' AND disponible > 0 AND codalmacen IN ('" + "', '".join(aListaAlmacenes) + "')")

            if disponible and float(disponible) > 0:
                self.stock_disponible = True

            if row["t.indicecommunity"] not in self.indice_tallas:
                self.indice_tallas.append(row["t.indicecommunity"])

            if row["ic.indicecommunity"] not in self.indice_colores:
                self.indice_colores.append(row["ic.indicecommunity"])

            if (str(refConfig)) != "None":
                if str(row["a3.referenciaconfigurable"]) != "None":
                    if str(row["a3.configurable"]) != "True":
                        self.sincronizarsimple = False
            if str(row["lsc.idobjeto"]) == str(row["a.referencia"]):
                self.indiceconfigurable = int(i)
            i = i + 1

        print(str(self.indiceconfigurable))

        return body

    def get_data(self):
        data = self.get_db_data()

        if data == []:
            return data

        '''
        data[0]["indice_tallas"] = self.indice_tallas
        data[0]["indice_colores"] = self.indice_colores
        data[0]["stock_disponible"] = self.stock_disponible
        data[0]["store_id"] = "all"

        str(self.indiceconfigurable)

        configurable_product_default = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "ES"
        configurable_product_es = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "EN"
        configurable_product_en = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "FR"
        configurable_product_fr = self.get_configurable_product_serializer().serialize(data[0])
        data[0]["store_id"] = "DE"
        configurable_product_de = self.get_configurable_product_serializer().serialize(data[0])'''

        data[self.indiceconfigurable]["indice_tallas"] = self.indice_tallas
        data[self.indiceconfigurable]["indice_colores"] = self.indice_colores
        data[self.indiceconfigurable]["stock_disponible"] = self.stock_disponible
        data[self.indiceconfigurable]["store_id"] = "all"

        configurable_product_default = self.get_configurable_product_serializer().serialize(data[self.indiceconfigurable])
        data[self.indiceconfigurable]["store_id"] = "ES"
        configurable_product_es = self.get_configurable_product_serializer().serialize(data[self.indiceconfigurable])
        data[self.indiceconfigurable]["store_id"] = "EN"
        configurable_product_en = self.get_configurable_product_serializer().serialize(data[self.indiceconfigurable])
        data[self.indiceconfigurable]["store_id"] = "FR"
        configurable_product_fr = self.get_configurable_product_serializer().serialize(data[self.indiceconfigurable])
        data[self.indiceconfigurable]["store_id"] = "DE"
        configurable_product_de = self.get_configurable_product_serializer().serialize(data[self.indiceconfigurable])
        
        simple_products_default = False
        if self.sincronizarsimple:
            simple_products_default = []
            simple_products_es = []
            simple_products_en = []
            simple_products_fr = []
            simple_products_de = []
        product_links = []

        for row in data:
            if self.sincronizarsimple:
                row["store_id"] = "all"
                simple_products_default.append(self.get_simple_product_serializer().serialize(row))
                row["store_id"] = "ES"
                simple_products_es.append(self.get_simple_product_serializer().serialize(row))
                row["store_id"] = "EN"
                simple_products_en.append(self.get_simple_product_serializer().serialize(row))
                row["store_id"] = "FR"
                simple_products_fr.append(self.get_simple_product_serializer().serialize(row))
                row["store_id"] = "DE"
                simple_products_de.append(self.get_simple_product_serializer().serialize(row))
            product_links.append(self.get_product_link_serializer().serialize(row))

        if not configurable_product_default and not simple_products_default and not product_links:
            return False

        if product_links[0] == False:
            product_links = False

        if self.sincronizarsimple:
            return {
                "configurable_product_default": configurable_product_default,
                "configurable_product_es": configurable_product_es,
                "configurable_product_en": configurable_product_en,
                "configurable_product_fr": configurable_product_fr,
                "configurable_product_de": configurable_product_de,
                "simple_products_default": simple_products_default,
                "simple_products_es": simple_products_es,
                "simple_products_en": simple_products_en,
                "simple_products_fr": simple_products_fr,
                "simple_products_de": simple_products_de,
                "product_links": product_links,
            }

        return {
            "configurable_product_default": configurable_product_default,
            "configurable_product_es": configurable_product_es,
            "configurable_product_en": configurable_product_en,
            "configurable_product_fr": configurable_product_fr,
            "configurable_product_de": configurable_product_de,
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
            print(str(product_url.format("all")))
            print(str(json.dumps(data["configurable_product_default"])))
            print("---------------------")
            self.send_request("post", url=product_url.format("all"), data=json.dumps(data["configurable_product_default"]))

        '''if data["configurable_product_es"]:
            self.send_request("post", url=product_url.format("es"), data=json.dumps(data["configurable_product_es"]))
            self.send_request("post", url=product_url.format("es_cn"), data=json.dumps(data["configurable_product_es"]))
            self.send_request("post", url=product_url.format("intl_es"), data=json.dumps(data["configurable_product_es"]))
            self.send_request("post", url=product_url.format("pt_es"), data=json.dumps(data["configurable_product_es"]))

            print(str(product_url.format("es")))
            print(str(product_url.format("es_cn")))
            print(str(product_url.format("intl_es")))
            print(str(product_url.format("pt_es")))
            print(str(json.dumps(data["configurable_product_es"])))
            print("---------------------")'''

        if data["configurable_product_en"]:
            self.send_request("post", url=product_url.format("en"), data=json.dumps(data["configurable_product_en"]))
            self.send_request("post", url=product_url.format("intl_en"), data=json.dumps(data["configurable_product_en"]))
            self.send_request("post", url=product_url.format("intl_uk"), data=json.dumps(data["configurable_product_en"]))
            print(str(product_url.format("en")))
            print(str(product_url.format("intl_en")))
            print(str(product_url.format("intl_uk")))
            print(str(product_url.format("pt_en")))
            print(str(json.dumps(data["configurable_product_en"])))
            print("---------------------")

        if data["configurable_product_fr"]:
            # self.send_request("post", url=product_url.format("fr"), data=json.dumps(data["configurable_product_fr"]))
            self.send_request("post", url=product_url.format("intl_fr"), data=json.dumps(data["configurable_product_fr"]))
            self.send_request("post", url=product_url.format("fr_fr"), data=json.dumps(data["configurable_product_fr"]))

            print(str(product_url.format("intl_fr")))
            print(str(product_url.format("fr_fr")))
            print(str(json.dumps(data["configurable_product_fr"])))
            print("---------------------")

        if data["configurable_product_de"]:
            self.send_request("post", url=product_url.format("intl_de"), data=json.dumps(data["configurable_product_de"]))
            print(str(product_url.format("intl_de")))
            print(str(json.dumps(data["configurable_product_de"])))
            print("---------------------")

        ''' Esto hay que mirarlo para portugués
        if data["configurable_product_pt"]:
            self.send_request("post", url=product_url.format("pt_pt"), data=json.dumps(data["configurable_product_pt"]))'''

        if self.sincronizarsimple:
            if data["simple_products_default"]:
                for simple_product in data["simple_products_default"]:
                    self.send_request("post", url=product_url.format("all"), data=json.dumps(simple_product))
                    print(str(product_url.format("all")))
                    print(str(json.dumps(simple_product)))
                    print("---------------------")

            '''if data["simple_products_es"]:
                for simple_product in data["simple_products_es"]:
                    self.send_request("post", url=product_url.format("es"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("es_cn"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("intl_es"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("pt_es"), data=json.dumps(simple_product))

                    print(str(product_url.format("es")))
                    print(str(product_url.format("es_cn")))
                    print(str(product_url.format("intl_es")))
                    print(str(product_url.format("pt_es")))
                    print(str(json.dumps(simple_product)))
                    print("---------------------")'''

            if data["simple_products_en"]:
                for simple_product in data["simple_products_en"]:
                    self.send_request("post", url=product_url.format("en"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("intl_en"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("intl_uk"), data=json.dumps(simple_product))
                    # self.send_request("post", url=product_url.format("pt_en"), data=json.dumps(simple_product))
                    print(str(product_url.format("en")))
                    print(str(product_url.format("intl_en")))
                    print(str(product_url.format("intl_uk")))
                    print(str(product_url.format("pt_en")))
                    print(str(json.dumps(simple_product)))
                    print("---------------------")

            if data["simple_products_fr"]:
                for simple_product in data["simple_products_fr"]:
                    # self.send_request("post", url=product_url.format("fr"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("intl_fr"), data=json.dumps(simple_product))
                    self.send_request("post", url=product_url.format("fr_fr"), data=json.dumps(simple_product))

                    print(str(product_url.format("intl_fr")))
                    print(str(product_url.format("fr_fr")))
                    print(str(json.dumps(simple_product)))
                    print("---------------------")

            if data["simple_products_de"]:
                for simple_product in data["simple_products_de"]:
                    self.send_request("post", url=product_url.format("intl_de"), data=json.dumps(simple_product))
                    print(str(product_url.format("intl_de")))
                    print(str(json.dumps(simple_product)))
                    print("---------------------")

            ''' Esto hay que mirarlo para portugués
            if data["simple_products_pt"]:
                for simple_product in data["simple_products_pt"]:
                    self.send_request("post", url=product_url.format("pt_pt"), data=json.dumps(simple_product))'''

        if data["product_links"]:
            for product_link in data["product_links"]:
                # print(str(link_url.format(data["configurable_product_default"]["product"]["sku"])))
                print(str(link_url.format(self.referencia)))                
                print(str(json.dumps(product_link)))
                print("---------------------")
                #self.send_request("post", url=link_url.format(data["configurable_product_default"]["product"]["sku"]), data=json.dumps(product_link))
                self.send_request("post", url=link_url.format(self.referencia), data=json.dumps(product_link))

        try:
            self.send_request("get", url=get_url.format(self.referencia))
        except Exception as e:
            return data

        return data

    def after_sync(self, response_data=None):
        qsatype.FLSqlQuery().execSql("UPDATE lineassincro_catalogo SET sincronizado = TRUE WHERE id = {}".format(self.idlinea))
        qsatype.FLSqlQuery().execSql("UPDATE articulostarifas SET horamod = CURRENT_TIME, fechamod = CURRENT_DATE, sincronizado = FALSE WHERE codtarifa in (select t.codtarifa from mg_websites w inner join mg_storeviews st on w.codwebsite = st.codwebsite inner join tarifas t on t.codtarifa = st.codtarifa group by t.codtarifa) AND referencia = '{}'".format(self.referencia))

        qsatype.FLSqlQuery().execSql("UPDATE eg_sincrostockwebcanalweb set sincronizado = false where sincronizado = true AND barcode in (select barcode from atributosarticulos where referencia = '" + self.referencia + "')")
        
        oCanales = json.loads(qsatype.FLUtil.sqlSelect("param_parametros", "valor", "nombre = 'CANALES_WEB'"))
        
        for canalweb in oCanales:
            print(str(canalweb))
            qsatype.FLSqlQuery().execSql("INSERT into eg_sincrostockwebcanalweb (fecha, hora, sincronizado, sincronizadoeci, barcode, codcanalweb) (SELECT CURRENT_DATE, CURRENT_TIME, false, true, aa.barcode, '" + str(canalweb) + "' from atributosarticulos aa left join eg_sincrostockwebcanalweb s on aa.barcode = s.barcode and s.codcanalweb = '" + str(canalweb) + "' where aa.referencia = '" + self.referencia + "' and s.idss is null)")

        lineas_no_sincro = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idsincro = '{}' AND NOT sincronizado LIMIT 1".format(self.idsincro))

        self.log("Exito", "Productos sincronizados correctamente (referencia: {})".format(self.referencia))

        return self.small_sleep
