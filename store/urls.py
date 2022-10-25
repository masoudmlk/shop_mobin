from store import views
from django.urls import path, include


urlpatterns = [

    path(r"product/get/<int:pk>/", views.ProductView.as_view({'get': 'retrieve'})),
    path(r"product/list/", views.ProductView.as_view({'get': 'list'})),

    path(r"opinion/add/<int:product_id>/", views.OpinionView.as_view({'post': 'add'})),
    path(r"opinion/list/<int:product_id>/", views.OpinionView.as_view({'get': 'list'})),

    path(r"score/add/<int:product_id>/", views.ScoreView.as_view({'post': 'add'})),
    path(r"score/get/<int:product_id>/", views.ScoreView.as_view({'get': 'avg_score'})),

    path(r"cart/add/", views.CartAction.as_view({'post': 'add_list'})),
    path(r"cart/remove/", views.CartAction.as_view({'delete': 'remove_list'})),

    path(r"track/list/", views.TrackViewSet.as_view({'get': 'list'})),
    path(r"track/get/<str:track>/", views.TrackViewSet.as_view({'get': 'retrieve'})),

    # path(r"track/get/<str:track>/", views.TrackViewSet.as_view({'get': 'retrieve'})),

    path(r"shop/", views.ShopView.as_view())

]
