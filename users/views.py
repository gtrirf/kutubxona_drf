from rest_framework_simplejwt.tokens import RefreshToken
from .models import VerificationCode
from .serializers import VerificationCodeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import login, logout
from rest_framework import viewsets
from .models import CustomUser
from rest_framework import viewsets, permissions
from .models import CustomUser
from .serializers import UserRoleSerializer
from .permissions import IsAdmin, IsUser, IsStaff, IsDirector
from rest_framework import viewsets
from books.models import Book, Queue, Rental, Comment
from books.serializers import CommentBookSerializer, BookSerializer, QueueSerializer,RentalSerializer

class CustomLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['verification_code']
            verification_code = VerificationCode.objects.filter(code=code, is_active=True).first()
            if verification_code and verification_code.is_valid():
                user = verification_code.user
                login(request, user)
                verification_code.is_active = False
                verification_code.save()

                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'detail': 'Login successful.',
                    'success': True,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid or expired verification code.',
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRoleSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['list', 'retrieve', ]:
            permission_classes = [IsAdmin | IsStaff | IsDirector]
        elif self.action in ['update', 'partial_update', 'destroy', 'create']:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserRoleSerializer
#
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve', ]:
#             self.permission_classes = [IsAdmin | IsStaff | IsDirector]
#         elif self.action in ['update', 'partial_update', 'destroy', 'create']:
#             permission_classes = [IsAdmin]
#         return super().get_permissions()


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsStaff | IsDirector]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class CommentBookViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentBookSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'destroy', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class QueueViewSet(viewsets.ModelViewSet):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'destroy', 'partial_update', 'update']:
            permission_classes = [IsAdmin | IsStaff ]
        return [permission() for permission in permission_classes]

class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'destroy', 'partial_update', 'update']:
            permission_classes = [IsAdmin | IsStaff | IsDirector]
        return [permission() for permission in permission_classes]