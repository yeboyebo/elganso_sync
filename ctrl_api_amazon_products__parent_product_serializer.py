from controllers.api.amazon.products.serializers.product_serializer import ProductSerializer


class ParentProductSerializer(ProductSerializer):

    def get_data(self):
        super().get_data()

        self.set_string_relation("Product//SKU", "lsc.idobjeto")

        if self.init_data['f.codfamiliaaz'] == 'Shoes':
            self.set_string_value("Product//ProductData//Shoes//VariationData//Parentage", "parent")

            del self.data["Product"]["ProductData"]["Shoes"]["VariationData"]["Color"]
            del self.data["Product"]["ProductData"]["Shoes"]["ShoeSizeComplianceData"]
        else:
            self.set_string_value("Product//ProductData//Clothing//VariationData//Parentage", "parent")

            del self.data["Product"]["ProductData"]["Clothing"]["ClassificationData"]["Size"]
            del self.data["Product"]["ProductData"]["Clothing"]["ClassificationData"]["Color"]
            del self.data["Product"]["ProductData"]["Clothing"]["ClassificationData"]["Departament"]
            del self.data["Product"]["ProductData"]["Clothing"]["ClassificationData"]["OuterMaterial"]

        # del self.data["Product"]["StandardProductID"]
        del self.data["Product"]["DescriptionData"]["Brand"]

        return True
