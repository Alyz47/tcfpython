from django.urls import path

from . import views
# from listing.views import set_preferences, get_preferences
from listing.views import PreferenceView
# from account.views import AddressListCreateAPIView, AddressRetrieveUpdateAPIView, UserAddressRetrieveAPIView    

address_detail = views.AddressViewSet.as_view({
    # 'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update'
    # 'delete': 'destroy'
})


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    # path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/view/<slug:profile_pk>/', views.get_user_profile, name='user_profile'),
    path('profile/', views.get_user_profile, name='current_user_profile'),
    path('profile/<slug:profile_pk>/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('user/<slug:user_pk>/', views.get_user, name='user details'),
    path('profile/<slug:profile_pk>/listings/', views.get_user_listings, name='user_listings'),
    path('profile/listings/', views.get_user_listings, name='current_user_listings'),
    path('profile/address/', views.AddressViewSet.as_view({'get': 'list'}), name='get_user_addresses'),
    path('profile/address/create/', views.AddressViewSet.as_view({'post': 'create'}), name='create_user_address'),
    path('profile/address/update/<int:pk>/', address_detail, name='update_user_address'),

    # path('set-preferences/', set_preferences, name='set_preferences'),
    path('preferences/', PreferenceView.as_view(), name='preferences'),
    # path('address/', AddressListCreateAPIView.as_view(), name='address-list-create'),
    # path('address/<int:pk>/', AddressRetrieveUpdateAPIView.as_view(), name='address-retrieve-update'),
    # path('address/user/<int:user_id>/', UserAddressRetrieveAPIView.as_view(), name='user-address'),
]
