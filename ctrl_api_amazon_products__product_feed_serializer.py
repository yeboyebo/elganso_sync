from controllers.api.amazon.feeds.serializers.feed_serializer import FeedSerializer


class ProductFeedSerializer(FeedSerializer):

    def get_children_data(self):
        children = []

        message_id = 0

        ultima_referencia = None

        for data in self.init_data:
            if ultima_referencia != data["lsc.idobjeto"]:
                message_id += 1
                data['messageId'] = message_id

                child_data = self.parent_serializer.serialize(data)
                del child_data['children']
                children.append(child_data)
                ultima_referencia = data["lsc.idobjeto"]

            message_id += 1
            data['messageId'] = message_id

            child_data = self.child_serializer.serialize(data)
            del child_data['children']
            children.append(child_data)

        return children
