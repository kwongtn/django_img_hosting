import graphene

import img.schema


class Query(
    img.schema.Query,
    graphene.ObjectType
):
    pass

class Mutation(
    img.schema.Mutation,
    graphene.ObjectType
):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
