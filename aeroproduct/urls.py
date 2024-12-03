from django.contrib import admin
from django.urls import path, include
from product import views
from product.views import PartListView, ProducePartView, AircraftProductionView, ListPartsView, DeletePartView
from aeroproduct import views as main
from django.contrib.auth.views import LogoutView



urlpatterns = [
    # Ana sayfa ve Kullanıcı işlemleri
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('login/', views.login, name='login'),
    path('', include('product.urls')), 

    # Dashboard 
    path('dashboard/', views.dashboard, name='dashboard'),

    # Parça işlemleri (HTML sayfaları için)
    path('api/parts/', PartListView.as_view(), name='part_list'),
    path('api/produce-part/', ProducePartView.as_view(), name='produce_part'),
    path('dashboard/api/aircraft-production/', AircraftProductionView.as_view(), name='aircraft_production'),

    # Parça API
    path('dashboard/api/parts/', ListPartsView.as_view(), name='list_parts'),
    path('dashboard/api/parts/<int:part_id>/', DeletePartView.as_view(), name='delete_part'),
    path('dashboard/api/aircraft/', views.AircraftListView.as_view(), name='aircraft_list'),
    path('dashboard/api/aircraft/<int:id>/list/', views.AircraftListView.as_view(), name='aircraft_list'),  # Uçakları listeleme
    path('dashboard/api/aircraft/<int:id>/remove/', views.AircraftRemoveView.as_view(), name='remove_aircraft'),  # Yayından kaldırma işlemi
    

    path('api/test', views.getData),
]
