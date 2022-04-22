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
            self.set_string_relation("Product//ProductData//Shoes//VariationData//Color", "a.egcolor")
            self.set_string_value("Product//ProductData//Shoes//VariationData//VariationTheme", "Size")
            self.set_string_value("Product//ProductData//Shoes//ClassificationData//CountryOfOrigin", "ES")
            self.set_string_relation("Product//ProductData//Shoes//ClassificationData//SizeMap", "aa.talla")
            self.set_string_value("Product//ProductData//Shoes//ClassificationData//TargetGender", self.get_target(self.init_data["a.codgrupomoda"]))

            edad = self.get_age_range_shoes(self.init_data["a.codgrupomoda"])
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//AgeRangeDescription", edad)
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//FootwearSizeSystem", "eu_footwear_size_system")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSizeAgeGroup", edad)
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSizeClass", "numeric")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSizeWidth", "medium")
            self.set_string_value("Product//ProductData//Shoes//ShoeSizeComplianceData//ShoeSize", "numeric_" + self.init_data['aa.talla'])
        else:
            self.set_string_value("Product//ProductData//Clothing//VariationData//Parentage", "child")
            self.set_string_value("Product//ProductData//Clothing//VariationData//VariationTheme", "Size")

            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//Size", "aa.talla")
            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//Color", "a.egcolor")
            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//ClothingType", "f.codfamiliaaz")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//Department", "casual")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//OuterMaterial", "material")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//CountryOfOrigin", "ES")
            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//SizeMap", "aa.talla")
            self.set_string_relation("Product//ProductData//Clothing//ClassificationData//FabricType", "a.egcomposicion")
            self.set_string_value("Product//ProductData//Clothing//ClassificationData//TargetGender", self.get_target(self.init_data["a.codgrupomoda"]))

            edad = self.get_age_range(self.init_data["a.codgrupomoda"])
            self.set_string_value("Product//ProductData//Clothing//AgeRangeDescription", edad)

            if self.init_data['f.codfamiliaaz'] == 'Socks' or self.init_data['f.codfamiliaaz'] == 'Dress' or self.init_data['f.codfamiliaaz'] == 'Sweater' or self.init_data['f.codfamiliaaz'] == 'Kurta' or self.init_data['f.codfamiliaaz'] == 'Coat' or self.init_data['f.codfamiliaaz'] == 'Tunic' or self.init_data['f.codfamiliaaz'] == 'Underpants' or self.init_data['f.codfamiliaaz'] == 'Sweatshirt' or self.init_data['f.codfamiliaaz'] == 'Pajamas' or self.init_data['f.codfamiliaaz'] == 'Suit' or self.init_data['f.codfamiliaaz'] == 'Robe' or self.init_data['f.codfamiliaaz'] == 'Tights' or self.init_data['f.codfamiliaaz'] == 'Blazer' or self.init_data['f.codfamiliaaz'] == 'TrackSuit' or self.init_data['f.codfamiliaaz'] == 'Vest' or self.init_data['f.codfamiliaaz'] == 'SalwarSuitSet':
                if edad != "Infantil" and self.init_data['f.codfamiliaaz'] != 'Socks' and self.init_data['f.codfamiliaaz'] != 'Vest' and self.init_data['f.codfamiliaaz'] != 'Coat':
                    self.set_string_value("Product//ProductData//Clothing//ApparelBodyType", "regular")
                    self.set_string_value("Product//ProductData//Clothing//ApparelHeightType", "regular")
                self.set_string_value("Product//ProductData//Clothing//ApparelSize", self.get_apparel_size(self.init_data["ta.codgrupotalla"], self.init_data["aa.talla"]))
                self.set_string_value("Product//ProductData//Clothing//ApparelSizeClass", self.get_apparel_size_class(self.init_data["ta.codgrupotalla"]))
                self.set_string_value("Product//ProductData//Clothing//ApparelSizeSystem", "as4")
            elif self.init_data['f.codfamiliaaz'] == 'Shirt':
                '''if edad != "Infantil":
                    self.set_string_value("Product//ProductData//Clothing//ShirtBodyType", "")
                    self.set_string_value("Product//ProductData//Clothing//ShirtHeightType", "")'''
                self.set_string_value("Product//ProductData//Clothing//ShirtSize", self.get_apparel_size(self.init_data["ta.codgrupotalla"], self.init_data["aa.talla"]))
                self.set_string_value("Product//ProductData//Clothing//ShirtSizeClass", self.get_apparel_size_class(self.init_data["ta.codgrupotalla"]))
                self.set_string_value("Product//ProductData//Clothing//ShirtSizeSystem", "as4")
            elif self.init_data['f.codfamiliaaz'] == 'Pants' or self.init_data['f.codfamiliaaz'] == 'Shorts' or self.init_data['f.codfamiliaaz'] == 'Overalls':
                self.set_string_value("Product//ProductData//Clothing//BottomsSize", self.get_apparel_size(self.init_data["ta.codgrupotalla"], self.init_data["aa.talla"]))
                self.set_string_value("Product//ProductData//Clothing//BottomsSizeClass", self.get_apparel_size_class(self.init_data["ta.codgrupotalla"]))
                self.set_string_value("Product//ProductData//Clothing//BottomsSizeSystem", "as4")
            elif self.init_data['f.codfamiliaaz'] == 'Swimwear' or self.init_data['f.codfamiliaaz'] == 'Bra' or self.init_data['f.codfamiliaaz'] == 'Corset' or self.init_data['f.codfamiliaaz'] == 'UndergarmentSlip':
                self.set_string_value("Product//ProductData//Clothing//ShapewearSize", self.get_apparel_size(self.init_data["ta.codgrupotalla"], self.init_data["aa.talla"]))
                self.set_string_value("Product//ProductData//Clothing//ShapewearSizeClass", self.get_apparel_size_class(self.init_data["ta.codgrupotalla"]))
                self.set_string_value("Product//ProductData//Clothing//ShapewearSizeSystem", "as4")
            elif self.init_data['f.codfamiliaaz'] == 'Hat':
                self.set_string_value("Product//ProductData//Clothing//HeadwearSize", self.get_apparel_size(self.init_data["ta.codgrupotalla"], self.init_data["aa.talla"]))
                self.set_string_value("Product//ProductData//Clothing//HeadwearSizeClass", self.get_apparel_size_class(self.init_data["ta.codgrupotalla"]))
                self.set_string_value("Product//ProductData//Clothing//HeadwearSizeSystem", "as4")
            elif self.init_data['f.codfamiliaaz'] == 'Skirt':
                self.set_string_value("Product//ProductData//Clothing//SkirtSize", self.get_apparel_size(self.init_data["ta.codgrupotalla"], self.init_data["aa.talla"]))
                self.set_string_value("Product//ProductData//Clothing//SkirtSizeClass", self.get_apparel_size_class(self.init_data["ta.codgrupotalla"]))
                self.set_string_value("Product//ProductData//Clothing//SkirtSizeSystem", "as4")

        return True

    def get_target(self, data):
        if data == "1":
            return "male"
        elif data == "2":
            return "female"
        else:
            return "unisex"

    def get_apparel_size_class(self, data):
        if data == "NUM":
            return "numeric"
        elif data == "ALF":
            return "alpha"
        else:
            return "age"

    def get_apparel_size(self, grupo, talla):
        if talla == "TU":
            return "one_size"
        if grupo == "NUM":
            return "numeric_" + talla
        elif grupo == "ALF":
            if talla == "XL":
                return "x_l"
            if talla == "XXL":
                return "xx_l"
            if talla == "XS":
                return "x_s"
            return talla.lower()
        else:
            return "one_size"

    def get_age_range(self, data):
        if data == "3" or data == "5":
            return "Infantil"
        else:
            return "adult"

    def get_age_range_shoes(self, data):
        if data == "3" or data == "5":
            return "toddler"
        else:
            return "adult"
