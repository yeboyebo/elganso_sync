from controllers.base.default.serializers.default_serializer import DefaultSerializer


class RelationshipSerializer(DefaultSerializer):

    def get_data(self):
        self.set_string_relation("MessageID", "messageId")
        self.set_string_value("OperationType", "Update")

        self.set_string_relation("Relationship//ParentSKU", "az.referencia")
        self.set_string_relation("Relationship//Relation//SKU", "aa.barcode")
        self.set_string_value("Relationship//Relation//Type", "Variation")

        return True
