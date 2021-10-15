import graphene

import img.schema


class Query(
    img.schema.Query,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query)
