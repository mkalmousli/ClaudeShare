"""The single GraphQL schema, assembled from per-resource resolver classes."""
import strawberry

from .resolvers.auth import AuthMutation, AuthQuery
from .resolvers.files import FileMutation, FileQuery
from .resolvers.terminal import TerminalMutation, TerminalQuery, TerminalSubscription
from .resolvers.usage import UsageQuery, UsageSubscription


@strawberry.type
class Query(AuthQuery, TerminalQuery, FileQuery, UsageQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, TerminalMutation, FileMutation):
    pass


@strawberry.type
class Subscription(TerminalSubscription, UsageSubscription):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
