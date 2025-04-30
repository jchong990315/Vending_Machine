from django.urls import path
from .views import (
    ProductListView, ProductSelectionView, PaymentView,
    CurrentSelectionView, UserProfileView, TransactionsView, PaymentConfirmationView
)
from .admin_views import (InventoryUpdateView, PriceUpdateView, ThresholdUpdateView,
                          ChannelUpdateView, WarningView)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('select-product/', ProductSelectionView.as_view(), name='select-product'),
    path('pay/', PaymentView.as_view(), name='payment'),
    path('current-selection/', CurrentSelectionView.as_view(), name='current-selection'),
    path('user-profile/', UserProfileView.as_view(), name='user-profile'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('confirm-payment/', PaymentConfirmationView.as_view(), name='confirm_payment'),
    path('update-inventory/', InventoryUpdateView.as_view(), name='update-inventory'),
    path('update-price/', PriceUpdateView.as_view(), name='update-price'),
    path('update-threshold/', ThresholdUpdateView.as_view(), name='update-threshold'),
    path('update-channel/', ChannelUpdateView.as_view(), name='update-channel'),
    path('warning/', WarningView.as_view(), name='warning'),
]
