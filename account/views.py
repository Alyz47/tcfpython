from django.contrib.auth import authenticate
# from django.contrib.sites.shortcuts import get_current_site
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from dj_rest_auth.views import LoginView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from rest_framework.authtoken.models import Token
from django.middleware.csrf import get_token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .permissions import IsUserAddressOwner
from .models import Profile, Address
from .serializers import (UserSerializer,
                          LoginSerializer,
                          ProfileSerializer,
                          ReadAddressSerializer,
                          WriteAddressSerializer,
                          EditProfileSerializer)
from listing.serializers import ReadListingSerializer
from listing.models import Listing


User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            user = User.objects.create_user(
                email=email, username=username, password=password)
            
            # Generate and save authentication token
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({'error': "Provide Invalid Details"}, status=400)
        except IntegrityError:
            return Response({'error': "User Already Exist"}, status=403)


# @api_view(['POST'])
# def register(request):
#     if request.method == 'POST':
#         serializer = RegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()  # This will call the create() method in RegistrationSerializer
#             # current_site = get_current_site(request)
#             # mail_subject = "Please activate your account"
#             # message = render_to_string('account/account_verification_email.html', {
#             #     'user': user,
#             #     'domain': current_site.domain,
#             #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#             #     'token': default_token_generator.make_token(user),
#             # })
#             # to_email = serializer.validated_data['email']
#             # send_email = EmailMessage(mail_subject, message, to=[to_email])
#             # send_email.send()
#             return Response({'detail': 'Account created. Please check your email for activation instructions.'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def login(request):
#     if request.method == 'POST':
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             username = serializer.validated_data['username']
#             password = serializer.validated_data['password']
#             user = authenticate(request, username=username, password=password)
#             print(f"User Login: {user}")
#             if user is not None:
#                 token, _ = Token.objects.get_or_create(user=user)
#                 return Response({'token': token.key}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginAPIView(LoginView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Get the validated user
            user = serializer.validated_data['user']

            # Manually log the user in
            from django.contrib.auth import login
            login(request, user)

            # Generate CSRF token
            csrf_token = get_token(request)

            # Customize your response data here
            response_data = serializer.to_representation({'user': user})

            # Create the response
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set the CSRF token in the response cookies
            response.set_cookie('csrftoken', csrf_token)

            return response
        else:
            # Handle invalid serializer data
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    # Optional to clear session
    request.session.flush()
    return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)


# def activate(request):
    return


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_user_profile(request, profile_pk=None):
    # View profile of other users
    if profile_pk:
        try:
            profile = Profile.objects.get(pk=profile_pk)
            serializer = ProfileSerializer(profile, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
    else:  # View current logged in user's profile if no PK is passed
        user = request.user
        print(user)

        if user.is_authenticated:
            try:
                profile = Profile.objects.get(user=user)
                serializer = ProfileSerializer(profile, context={"request": request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Profile.DoesNotExist:
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        else:   
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

# get User
@api_view(['GET'])
def get_user(request, user_pk=None):
    if user_pk:
        try:
            user = User.objects.get(pk=user_pk)
            serializer = UserSerializer(user)
            print("yo", serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# Edit Profile
class EditProfileView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = EditProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_user_listings(request, profile_pk=None):
    if profile_pk:
        try:
            user = User.objects.get(pk=profile_pk)
            listings = Listing.objects.filter(seller=user, is_sold=False).order_by('-created')
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user

        if user.is_authenticated:
            try:
                listings = Listing.objects.filter(seller=user, is_sold=False).order_by('-created')
            except User.DoesNotExist:
                return Response({"error": "You are not logged in."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReadListingSerializer(listings, context={"request": request}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    """
    List and Retrieve user addresses
    """
    queryset = Address.objects.all()
    permission_classes = (IsUserAddressOwner,)

    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        return res.filter(user=user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadAddressSerializer
        return WriteAddressSerializer



# class AddressListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = AddressSerializer
#     # permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # If user_id is provided in the URL, filter addresses by that user ID
#         user_id = self.kwargs.get('user_id')
#         if user_id:
#             return Address.objects.filter(user_id=user_id)
#         # Otherwise, default to the authenticated user's addresses
#         user = self.request.user
#         return Address.objects.filter(user=user)

#     def perform_create(self, serializer):
#         # If user_id is provided in the URL, use that user ID to save the address
#         user_id = self.kwargs.get('user_id')
#         if user_id:
#             serializer.save(user_id=user_id)
#         else:
#             serializer.save(user=self.request.user)


# class AddressRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     serializer_class = AddressSerializer
#     queryset = Address.objects.all()  # Set queryset to retrieve all addresses


# class UserAddressRetrieveAPIView(generics.ListAPIView):
#     serializer_class = AddressSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = Address.objects.all()
#     lookup_field = 'user_id'  # Specify the lookup field

#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id')
#         return Address.objects.filter(user_id=user_id)

#     def put(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def patch(self, request, *args, **kwargs):
#         return self.put(request, *args, **kwargs)