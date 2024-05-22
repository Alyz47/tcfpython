from django.urls import path

# from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
     # path('', views.get_listings, name='listings'),
     path('main-category/<slug:main_category_slug>/sizes/', views.get_sizes_for_category, name='sizes_for_main_category'),
     path('main-category/', views.get_main_categories, name='main_categories'),
     path('sub-category/<str:sub_category_gender>/', views.get_sub_categories, name='sub_categories_list_by_gender'),
     path('category/<str:sub_category_gender>/',
          views.get_all_listings_by_gender, name='listings_by_gender'),
     path('category/<str:sub_category_gender>/<slug:main_category_slug>/<slug:sub_category_slug>/',
          views.get_all_listings_by_gender, name='listings_by_gender_and_subcat'),
     path('listing-details/<slug:listing_pk>/', views.get_listing_details, name='listing_details'),
     path('listing-details/similar-listings/<slug:listing_pk>/', views.get_similar_listings, name='similar_listings'),
     path('listing-details/mixnmatch-listings/<slug:listing_pk>/', views.get_mixnmatch_listings, name='mixnmatch_listings'),
     path('search/', views.search, name='search'),
     path('create/', views.create_listing, name='create_listing'),
     path('update/<int:pk>/', views.update_listing, name='update_listing'),
     path('subcategory-classif/', views.upload_listing_image, name='upload_subcat_classif_img'),
     path('subcategory-classif/<int:pk>', views.update_listing_image, name='edit_subcat_classif_img'),     
]
