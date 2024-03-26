from YBLEGACY.constantes import *
from YBLEGACY import qsatype
from controllers.base.default.serializers.default_serializer import DefaultSerializer


class ConfigurableProductSerializer(DefaultSerializer):

    def get_data(self):
        if self.get_init_value("aa.talla") == "TU":
            return False

        if self.get_init_value("store_id") != "ES" and self.get_init_value("store_id") != "all":
            return self.get_serializador_store()
        elif self.get_init_value("store_id") == "ES":
            return self.get_serializador_store_es()

        self.set_string_relation("product//name", "a.descripcion")
        self.set_string_relation("product//weight", "a.peso")
        self.set_string_relation("product//sku", "a.referencia")

        self.set_string_value("product//attribute_set_id", "4")
        self.set_string_value("product//visibility", "4")
        self.set_string_value("product//type_id", "configurable")

        sincronizadoprevio = qsatype.FLUtil.sqlSelect("lineassincro_catalogo", "id", "idobjeto = '{}' and sincronizado and idsincro <> {} AND tiposincro = 'Enviar productos' and website = 'MG2'".format(self.get_init_value("a.referencia"),self.get_init_value("lsc.idsincro")))

        if str(sincronizadoprevio) == "None":
            self.set_string_value("product//status", "2")
        self.set_string_relation("product//price", "a.pvp")

        large_description = self.get_init_value("a.mgdescripcion")
        if large_description is False or large_description == "" or large_description is None or str(large_description) == "None":
            large_description = self.get_init_value("a.descripcion")

        short_description = self.get_init_value("a.mgdescripcioncorta")

        if short_description is False or short_description == "" or short_description is None or str(short_description) == "None":
            short_description = self.get_init_value("a.descripcion")

        custom_attributes = [
            {"attribute_code": "description", "value": large_description},
            {"attribute_code": "short_description", "value": short_description},
            {"attribute_code": "seller_id", "value": self.get_init_value("av.idvendedormagento")},
            {"attribute_code": "tax_class_id", "value": "5"},
            {"attribute_code": "composicion_textil", "value": self.get_init_value("a.egcomposicion")},
            {"attribute_code": "lavado", "value": self.get_init_value("a.egsignoslavado")},
            {"attribute_code": "sexo", "value": self.get_init_value("gm.descripcion")},
            {"attribute_code": "gruporemarketing", "value": self.get_init_value("tp.gruporemarketing")},
            {"attribute_code": "color", "value": self.get_init_value("ic.indicecommunity")},
            {"attribute_code": "product_tag", "value": "98"},
            {"attribute_code": "season", "value": self.get_dametemporada()},
            {"attribute_code": "default_color", "value": self.get_init_value("ic.indicecommunity")},
            {"attribute_code": "producto_asociado", "value": self.get_init_value("a.referenciaportatraje")}
        ]

        talla_modelo = self.get_init_value("a.mgtallamodelo")
        if talla_modelo is not False and talla_modelo != "" and talla_modelo is not None and str(talla_modelo) != "None":
            custom_attributes.append({"attribute_code": "talla_modelo", "value": talla_modelo})

        mas_info = self.get_init_value("a.mgmasinfo")
        if mas_info is not False and mas_info != "" and mas_info is not None and str(mas_info) != "None":
            custom_attributes.append({"attribute_code": "mas_info", "value": talla_modelo})

        medidas_modelo = self.get_init_value("a.mgmedidasmodelo")
        if medidas_modelo is not False and medidas_modelo != "" and medidas_modelo is not None and str(medidas_modelo) != "None":
            custom_attributes.append({"attribute_code": "medidas_modelo", "value": talla_modelo})

        size_values = [{"value_index": size} for size in self.get_init_value("indice_tallas")]
        colores_values = [{"value_index": color} for color in self.get_init_value("indice_colores")]
        extension_attributes = {
            "configurable_product_options": [{
                "attribute_id": 118,
                "label": "Size",
                "values": size_values
            }, {
                "attribute_id": 80,
                "label": "Color",
                "values": colores_values
            }],
            "stock_item": {"is_in_stock": self.get_init_value("stock_disponible")}
        }
        refConfigurable = self.get_init_value("a3.referenciaconfigurable")
        print("refConfigurable: ", refConfigurable)
        
        if (refConfigurable is False or refConfigurable == "" or refConfigurable is None or str(refConfigurable) == "None"):
            print("///////////ENTRAAAAA")
            extension_attributes = {
                "configurable_product_options": [{
                    "attribute_id": 118,
                    "label": "Size",
                    "values": size_values
                }],
                "stock_item": {"is_in_stock": self.get_init_value("stock_disponible")}
            }

        self.set_data_value("product//custom_attributes", custom_attributes)
        self.set_data_value("product//extension_attributes", extension_attributes)

        return True

    def get_serializador_store(self):
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

        self.set_string_relation("product//sku", "a.referencia")
        self.set_string_value("product//type_id", "configurable")
        self.set_string_value("product//name", desc_store)
        # self.set_string_relation("product//price", "a.pvp")

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
        desc_store = self.get_init_value("a.mgdescripcioncorta")
        if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
            desc_store = self.get_init_value("a.descripcion")

        large_description_store = self.get_init_value("a.mgdescripcion")
        if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
            large_description_store = self.get_init_value("a.descripcion")

        self.set_string_relation("product//sku", "a.referencia")
        # self.set_string_value("product//name", desc_store)
        # self.set_string_relation("product//price", "a.pvp")

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