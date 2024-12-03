from django.urls import path
from product import views
from product.views import PartListView, ProducePartView, AircraftProductionView, ListPartsView, DeletePartView

urlpatterns = [
    # path('api/parts/', PartListView.as_view(), name='part_list'),
    # path('api/produce-part/', ProducePartView.as_view(), name='produce_part'),
    # path('api/aircraft-production/', AircraftProductionView.as_view(), name='aircraft_production'),

    # path('parts/<int:team_id>/', ListPartsView.as_view(), name='list_parts'),
    # path('parts/delete/<int:part_id>/', DeletePartView.as_view(), name='delete_part'),

    # path('api/parts/<int:team_id>', ListPartsView.as_view(), name='list_parts'),
    # path('api/parts/<int:team_id>/<int:part_id>/', ListPartsView.as_view(), name='delete_part'),  # Silme işlemi için URL

    path('api/test', views.getData),
]
