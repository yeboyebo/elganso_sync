from controllers.api.amazon.products.serializers.product_serializer import ProductSerializer


class ParentProductSerializer(ProductSerializer):

    def get_data(self):
        super().get_data()

        self.set_string_relation("Product//SKU", "lsc.idobjeto")

        self.set_string_value("Product//ProductData//Clothing//VariationData//Parentage", "parent")
        # self.set_string_value("Product//ProductData//Clothing//ClassificationData//ClothingType", "Pants")

        if "Size" in self.data["Product"]["ProductData"]["Clothing"]["VariationData"]:
            del self.data["Product"]["ProductData"]["Clothing"]["VariationData"]["Size"]
        if "Size" in self.data["Product"]["ProductData"]["Clothing"]["ClassificationData"]:
            del self.data["Product"]["ProductData"]["Clothing"]["ClassificationData"]["Size"]

        return True
