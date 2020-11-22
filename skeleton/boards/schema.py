from skeleton.utils.jwt_utils import get_user_by_context
import graphene
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
from graphene import relay
from django.core import exceptions
from skeleton.boards.model import BoardModel
from skeleton.users.model import UserModel


class BoardType(DjangoObjectType):

    maker = graphene.Field('skeleton.users.schema.UserType')
    users = graphene.List('skeleton.users.schema.UserType')
    admins = graphene.List('skeleton.users.schema.UserType')

    lists = graphene.List('skeleton.lists.schema.ListType')

    @graphene.resolve_only_args
    def resolve_maker(self):
        return self.maker

    @graphene.resolve_only_args
    def resolve_users(self):
        return self.users.all()

    @graphene.resolve_only_args
    def resolve_admins(self):
        return self.admins.all()

    @graphene.resolve_only_args
    def resolve_lists(self):
        return self.lists.all()


    class Meta:
        model = BoardModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    board = graphene.Field(BoardType)
    boards = graphene.List(BoardType, id=graphene.String())

    def resolve_boards(self, info: ResolveInfo, **kwargs):
        return BoardModel.objects.all()

    def resolve_boards(self, info: ResolveInfo, id: str, **kwargs):
        return BoardModel.objects.filter(id=id).get()


class CreateNewBoard(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()


    class Arguments:
        title = graphene.String(required=True)
        #email = graphene.String(required=True)

    #maker_email is not required, since we obtain all info 'bout user from authentication header (our well-known JWT)
    def mutate(self, info: ResolveInfo, title: str):
        success = False
        user = None
        board = None

        user = get_user_by_context(info.context)
        board = BoardModel(title=title, background="", maker=user)
        board.admins.add(user)
        board.save()
        success = True

        return CreateNewBoard(board=board, success=success)


class CloseBoard(graphene.Mutation):
    board = graphene.Field(BoardType)


    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, board_id:str):
        board = None

        user = get_user_by_context(info.context)

        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)

            if(user not in board.admins):
                raise exceptions.PermissionDenied('User has no permissions to close the board')

            board.close()
            board.save()
            return CloseBoard(board=board)
        else:
            raise exceptions.ObjectDoesNotExist('Cannot close board that does not exist')


class ReopenBoard(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()


    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, board_id:str):
        board = None
        
        user = get_user_by_context(info.context)

        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)

            if(user not in board.admins):
                raise exceptions.PermissionDenied('User has no permissions to reopen the board')

            board.reopen()
            board.save()
            return ReopenBoard(board=board)
        else:
            raise exceptions.ObjectDoesNotExist('Cannot reopen board that does not exist')


class PermanentlyDelete(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()


    class Arguments:
        board_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, board_id:str):
        success = False
        
        user = get_user_by_context(info.context)

        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)

            if(user not in board.admins):
                raise exceptions.PermissionDenied('User has no permissions to permanently delete the board')

            board.delete()
            success = True
            return PermanentlyDelete(board=board, success=success)
        else:
            raise exceptions.ObjectDoesNotExist('Cannot delete board that does not exist')


class AddUser(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()
    

    class Arguments:
        user_id = graphene.String(required=True)
        board_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, user_id:str, board_id:str):
        success = False

        user = get_user_by_context(info.context)

        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            
            if not UserModel.objects.filter(id=user_id).exists():
                raise exceptions.ObjectDoesNotExist('Cannot add user, that does not exist')

            would_be_user = UserModel.objects.get(id=user_id)

            if(user not in board.admins):
                raise exceptions.PermissionDenied('User has no permissions to give somebody access to board')
            
            if(would_be_user in board.admins or would_be_user in board.users or would_be_user is board.maker):
                raise exceptions.SuspiciousOperation('User is already board member, it\'s kinda sus')

            board.users.add(would_be_user)
            board.save()
            success = True

            return AddUser(board=board, success=success)
        else:
            raise exceptions.ObjectDoesNotExist('Cannot add user to board that does not exist')


class AddAdmin(graphene.Mutation):
    board = graphene.Field(BoardType)
    success = graphene.Boolean()
    

    class Arguments:
        admin_id = graphene.String(required=True)
        board_id = graphene.String(required=True)

    def mutate(self, info: ResolveInfo, admin_id:str, board_id:str):
        success = False

        user = get_user_by_context(info.context)

        if BoardModel.objects.filter(id=board_id).exists():
            board = BoardModel.objects.get(id=board_id)
            
            if not UserModel.objects.filter(id=admin_id).exists():
                raise exceptions.ObjectDoesNotExist('Cannot entitle user to become admin, that does not exist')

            would_be_admin = UserModel.objects.get(id=admin_id)

            if(user not in board.admins):
                raise exceptions.PermissionDenied('User has no permissions to give somebody administrative privileges')
            
            if(would_be_admin in board.admins or would_be_admin is board.maker):
                raise exceptions.SuspiciousOperation('User is already board admin, it\'s kinda sus')

            board.admins.add(would_be_admin)
            board.save()
            success = True

            return AddAdmin(board=board, success=success)
        else:
            raise exceptions.ObjectDoesNotExist('Cannot add admin to board that does not exist')


class Mutation(graphene.ObjectType):
    createnewboard = CreateNewBoard.Field()
    closeBoard = CloseBoard.Field()
    reopenBoard = ReopenBoard.Field()
    permanentlydelete = PermanentlyDelete.Field()
    addadmin = AddAdmin.Field()
    adduser = AddUser.Field()
