from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SimpleProductSerializer(DefaultSerializer):

    def get_data(self):

        if self.get_init_value("store_id") != "ES" and self.get_init_value("store_id") != "all":
            return self.get_serializador_store()
        elif self.get_init_value("store_id") == "ES":
            return self.get_serializador_store_es()

        talla = self.get_init_value("aa.talla")
        self.set_string_relation("product//name", "a.descripcion")
        self.set_string_relation("product//weight", "a.peso")

        self.set_string_value("product//sku", self.get_sku())
        self.set_string_value("product//attribute_set_id", "4")

        sincronizadoprevio = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idobjeto = '{}' and sincronizado and idsincro <> {} AND tiposincro = 'Enviar productos' and website = 'MG2'".format(self.get_init_value("lsc.idobjeto"),self.get_init_value("lsc.idsincro")))

        if str(sincronizadoprevio) == "None":
            self.set_string_value("product//status", "1")
            self.set_string_relation("product//price", "a.pvp")
            if talla == "TU":
                self.set_string_value("product//status", "2")

        is_visibility = "1"
        if talla == "TU":
            is_visibility = "4"

        self.set_string_value("product//visibility", is_visibility)
        self.set_string_value("product//type_id", "simple")

        cant_stock = self.get_stock()
        is_in_stock = True
        if cant_stock == 0:
            is_in_stock = False

        self.set_string_value("product//extension_attributes//stock_item//qty", cant_stock)
        self.set_string_value("product//extension_attributes//stock_item//is_in_stock", is_in_stock)

        large_description = self.get_init_value("a.mgdescripcion")
        if large_description is False or large_description == "" or large_description is None or str(large_description) == "None":
            large_description = self.get_init_value("a.descripcion")

        short_description = self.get_init_value("a.mgdescripcioncorta")

        if short_description is False or short_description == "" or short_description is None or str(short_description) == "None":
            short_description = self.get_init_value("a.descripcion")

        custom_attributes = [
            {"attribute_code": "description", "value": large_description},
            {"attribute_code": "short_description", "value": short_description},
            {"attribute_code": "tax_class_id", "value": "5"},
            {"attribute_code": "barcode", "value": self.get_init_value("aa.barcode")},
            {"attribute_code": "seller_id", "value": self.get_init_value("av.idvendedormagento")},
            {"attribute_code": "size", "value": self.get_init_value("t.indicecommunity")},
            {"attribute_code": "composicion_textil", "value": self.get_init_value("a.egcomposicion")},
            {"attribute_code": "lavado", "value": self.get_init_value("a.egsignoslavado")},
            {"attribute_code": "sexo", "value": self.get_init_value("gm.descripcion")},
            {"attribute_code": "gruporemarketing", "value": self.get_init_value("tp.gruporemarketing")},
            {"attribute_code": "color", "value": self.get_init_value("ic.indicecommunity")},
            {"attribute_code": "product_tag", "value": "98"},
            {"attribute_code": "season", "value": self.get_dametemporada()}
        ]

        talla_modelo = self.get_init_value("a.mgtallamodelo")
        if talla_modelo is not False and talla_modelo != "" and talla_modelo is not None and str(talla_modelo) != "None":
            custom_attributes.append({"attribute_code": "talla_modelo", "value": talla_modelo})

        mas_info = self.get_init_value("a.mgmasinfo")
        if mas_info is not False and mas_info != "" and mas_info is not None and str(mas_info) != "None":
            custom_attributes.append({"attribute_code": "mas_info", "value": mas_info})

        medidas_modelo = self.get_init_value("a.mgmedidasmodelo")
        if medidas_modelo is not False and medidas_modelo != "" and medidas_modelo is not None and str(medidas_modelo) != "None":
            custom_attributes.append({"attribute_code": "medidas_modelo", "value": medidas_modelo})

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_sku(self):
        referencia = self.get_init_value("aa.referencia")
        talla = self.get_init_value("aa.talla")

        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def get_stock(self):
        return 0
        '''disponible = self.get_init_value("s.disponible")

        if not disponible or isNaN(disponible) or disponible < 0:
            return 0

        return disponible '''

    def get_serializador_store(self):
        self.set_string_value("product//sku", self.get_sku())

        desc_store = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'descripcion' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("a.referencia")))

        large_description_store = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'mgdescripcion' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("a.referencia")))
        composicion_textil = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'egcomposicion' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("a.referencia")))
        lavado = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'egsignoslavado' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("a.referencia")))

        if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
            desc_store = self.get_init_value("a.mgdescripcioncorta")
            if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
                desc_store = self.get_init_value("a.descripcion")

        if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
            large_description_store = self.get_init_value("a.mgdescripcion")
            if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
                large_description_store = self.get_init_value("a.descripcion")

        self.set_string_value("product//name", desc_store)

        custom_attributes = [
            {"attribute_code": "description", "value": large_description_store},
            {"attribute_code": "short_description", "value": desc_store},
            {"attribute_code": "composicion_textil", "value": composicion_textil},
            {"attribute_code": "lavado", "value": lavado},
            {"attribute_code": "season", "value": self.get_dametemporada()}
        ]

        talla_modelo = self.get_init_value("a.mgtallamodelo")
        if talla_modelo is not False and talla_modelo != "" and talla_modelo is not None and str(talla_modelo) != "None":
            custom_attributes.append({"attribute_code": "talla_modelo", "value": talla_modelo})

        mas_info = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'mgmasinfo' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("a.referencia")))
        if mas_info is not False and mas_info != "" and mas_info is not None and str(mas_info) != "None":
            custom_attributes.append({"attribute_code": "mas_info", "value": mas_info})

        medidas_modelo = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'mgmedidasmodelo' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("a.referencia")))
        if medidas_modelo is not False and medidas_modelo != "" and medidas_modelo is not None and str(medidas_modelo) != "None":
            custom_attributes.append({"attribute_code": "medidas_modelo", "value": medidas_modelo})

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_serializador_store_es(self):
        self.set_string_value("product//sku", self.get_sku())

        desc_store = self.get_init_value("a.mgdescripcioncorta")
        if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
            desc_store = self.get_init_value("a.descripcion")

        large_description_store = self.get_init_value("a.mgdescripcion")
        if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
            large_description_store = self.get_init_value("a.descripcion")

        # self.set_string_value("product//name", desc_store)

        custom_attributes = [
            {"attribute_code": "description", "value": large_description_store},
            {"attribute_code": "short_description", "value": desc_store},
            {"attribute_code": "composicion_textil", "value": self.get_init_value("a.egcomposicion")},
            {"attribute_code": "lavado", "value": self.get_init_value("a.egsignoslavado")},
            {"attribute_code": "season", "value": self.get_dametemporada()}
        ]

        talla_modelo = self.get_init_value("a.mgtallamodelo")
        if talla_modelo is not False and talla_modelo != "" and talla_modelo is not None and str(talla_modelo) != "None":
            custom_attributes.append({"attribute_code": "talla_modelo", "value": talla_modelo})

        mas_info = self.get_init_value("a.mgmasinfo")
        if mas_info is not False and mas_info != "" and mas_info is not None and str(mas_info) != "None":
            custom_attributes.append({"attribute_code": "mas_info", "value": mas_info})

        medidas_modelo = self.get_init_value("a.mgmedidasmodelo")
        if medidas_modelo is not False and medidas_modelo != "" and medidas_modelo is not None and str(medidas_modelo) != "None":
            custom_attributes.append({"attribute_code": "medidas_modelo", "value": medidas_modelo})

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_dametemporada(self):
        temporada = self.get_init_value("a.codtemporada")
        if not temporada or temporada == "":
            temporada = ""

        if temporada == "ATEMP":
            return qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "indicecommunity", "tipo = 'temporadas' AND valor = 'Atemporal'")
        if temporada == "W":
            temporada = "OI"
        else:
            temporada = "PV"

        anno = str(self.get_init_value("a.anno"))
        if anno and anno != "":
            if len(anno) == 2:
                anno = "20" + anno

        temporada_anno = anno + "-" + temporada
        return qsatype.FLUtil.sqlSelect("indicessincrocatalogo", "indicecommunity", "tipo = 'temporadas' AND valor = '{}'".format(temporada_anno))