from controllers.base.default.serializers.default_serializer import DefaultSerializer


class ProductSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("Product//SKU", "aa.barcode")
        self.set_string_value("Product//StandardProductID//Type", "EAN")
        self.set_string_relation("Product//StandardProductID//Value", "aa.barcode")
        self.set_string_value("Product//ProductTaxCode", "A_GEN_TAX")

        self.set_string_relation("Product//DescriptionData//Title", "lsc.descripcion")
        self.set_string_value("Product//DescriptionData//Brand", "El Ganso")
        self.set_string_relation("Product//DescriptionData//Description", "a.mgdescripcion", max_characters=None)

        self.set_string_value("Product//DescriptionData//Manufacturer", "El Ganso (ELGBO)")
        self.set_string_value("Product//DescriptionData//ItemType", "flat-sheets")
        self.set_string_value("Product//DescriptionData//IsGiftWrapAvailable", "false")
        self.set_string_value("Product//DescriptionData//IsGiftMessageAvailable", "false")

        if self.init_data['f.codfamiliaaz'] == 'Shoes':
            self.set_string_value("Product//ProductData//Shoes//ClothingType", "Shoes")
            self.set_string_value("Product//ProductData//Shoes//VariationData//Parentage", "child")
            # self.set_string_relation("Product//ProductData//Shoes//VariationData//Color", "a.egcolor")
            self.set_string_value("Product//ProductData//Shoes//VariationData//VariationTheme", "Size")
            self.set_string_value("Product//ProductData//Shoes//ClassificationData//TargetGender", self.get_target(self.init_data["a.codgrupomoda"]))

            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//AgeRangeDescription", "adult")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//FootwearSizeSystem", "eu_footwear_size_system")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSizeAgeGroup", "adult")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSizeClass", "numeric")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSizeWidth", "narrow")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSize", "numeric_" + self.init_data['aa.talla'])
        else:
            self.set_string_value("Product//ProductData//Clothing//VariationData//Parentage", "child")
            self.set_string_value("Product//ProductData//Clothing//VariationData//VariationTheme", "Size")

            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//Size", "aa.talla")
            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//Color", "a.egcolor")
            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//ClothingType", "f.codfamiliaaz")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//Department", "casual")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//OuterMaterial", "material")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//TargetGender", self.get_target(self.init_data["a.codgrupomoda"]))

        return True

    def get_target(self, data):
        if data == "1":
            return "male"
        elif data == "2":
            return "female"
        else:
            return "unisex"
