from YBLEGACY.constantes import *
from YBLEGACY import qsatype

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class SimpleProductSerializer(DefaultSerializer):

    def get_data(self):

        if self.get_init_value("store_id") != "ES" and self.get_init_value("store_id") != "all":
            return self.get_serializador_store()
        elif self.get_init_value("store_id") == "ES":
            return self.get_serializador_store_es()

        self.set_string_relation("product//name", "lsc.descripcion")
        self.set_string_relation("product//weight", "a.peso")
        self.set_string_relation("product//price", "a.pvp")

        self.set_string_value("product//sku", self.get_sku())
        self.set_string_value("product//attribute_set_id", "4")
        self.set_string_value("product//status", "1")

        is_visibility = "1"
        if self.get_init_value("aa.talla") == "TU":
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
            large_description = self.get_init_value("lsc.descripcion")

        short_description = self.get_init_value("a.mgdescripcioncorta")

        if short_description is False or short_description == "" or short_description is None or str(short_description) == "None":
            short_description = self.get_init_value("lsc.descripcion")

        custom_attributes = [
            {"attribute_code": "description", "value": large_description},
            {"attribute_code": "short_description", "value": short_description},
            {"attribute_code": "tax_class_id", "value": "2"},
            {"attribute_code": "barcode", "value": self.get_init_value("aa.barcode")},
            {"attribute_code": "seller_id", "value": self.get_init_value("av.idvendedormagento")},
            {"attribute_code": "size", "value": self.get_init_value("t.indicecommunity")}
        ]

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_sku(self):
        referencia = self.get_init_value("lsc.idobjeto")
        talla = self.get_init_value("aa.talla")

        if talla == "TU":
            return referencia

        return "{}-{}".format(referencia, talla)

    def get_stock(self):
        disponible = self.get_init_value("s.disponible")

        if not disponible or isNaN(disponible) or disponible < 0:
            return 0

        return disponible

    def get_serializador_store(self):
        self.set_string_value("product//sku", self.get_sku())

        desc_store = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'descripcion' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("lsc.idobjeto")))

        large_description_store = qsatype.FLUtil.sqlSelect("traducciones", "traduccion", "campo = 'mgdescripcion' AND codidioma = '" + self.get_init_value("store_id") + "' AND idcampo = '{}'".format(self.get_init_value("lsc.idobjeto")))

        if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
            desc_store = self.get_init_value("a.mgdescripcioncorta")
            if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
                desc_store = self.get_init_value("lsc.descripcion")

        if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
            large_description_store = self.get_init_value("a.mgdescripcion")
            if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
                large_description_store = self.get_init_value("lsc.descripcion")

        self.set_string_value("product//name", desc_store)

        custom_attributes = [
            {"attribute_code": "description", "value": large_description_store},
            {"attribute_code": "short_description", "value": desc_store}
        ]

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True

    def get_serializador_store_es(self):
        self.set_string_value("product//sku", self.get_sku())

        desc_store = self.get_init_value("a.mgdescripcioncorta")
        if not desc_store or desc_store == "" or str(desc_store) == "None" or desc_store is None:
            desc_store = self.get_init_value("lsc.descripcion")

        large_description_store = self.get_init_value("a.mgdescripcion")
        if large_description_store is False or large_description_store == "" or large_description_store is None or str(large_description_store) == "None":
            large_description_store = self.get_init_value("lsc.descripcion")

        self.set_string_value("product//name", desc_store)

        custom_attributes = [
            {"attribute_code": "description", "value": large_description_store},
            {"attribute_code": "short_description", "value": desc_store}
        ]

        self.set_data_value("product//custom_attributes", custom_attributes)

        return True
