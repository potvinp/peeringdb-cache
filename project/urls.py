from django.urls import path
from manage import metrics, sync_start, find_by_args, resource

urlpatterns = [
    path('api/org', lambda request: find_by_args(request, resource.Organization), name='get_org'),
    path('api/fac', lambda request: find_by_args(request, resource.Facility), name='get_fac'),
    path('api/net', lambda request: find_by_args(request, resource.Network), name='get_net'),
    path('api/ix', lambda request: find_by_args(request, resource.InternetExchange), name='get_ix'),
    path('api/campus', lambda request: find_by_args(request, resource.Campus), name='get_campus'),
    path('api/carrier', lambda request: find_by_args(request, resource.Carrier), name='get_carrier'),
    path('api/carrierfac', lambda request: find_by_args(request, resource.CarrierFacility), name='get_carrierfac'),
    path('api/ixfac', lambda request: find_by_args(request, resource.InternetExchangeFacility), name='get_ixfac'),
    path('api/ixlan', lambda request: find_by_args(request, resource.InternetExchangeLan), name='get_ixlan'),
    path('api/ixpfx', lambda request: find_by_args(request, resource.InternetExchangeLanPrefix), name='get_ixpfx'),
    path('api/netfac', lambda request: find_by_args(request, resource.NetworkFacility), name='get_netfac'),
    path('api/netixlan', lambda request: find_by_args(request, resource.NetworkIXLan), name='get_netixlan'),
    path('api/poc', lambda request: find_by_args(request, resource.NetworkContact), name='get_poc'),
    path('metrics', metrics, name='metrics'),
    path('sync', sync_start, name='sync_start'),
]
