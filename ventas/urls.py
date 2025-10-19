from django.urls import path
from . import views
from django.contrib.auth.views import LoginView 
app_name = 'ventas'
urlpatterns = [
    path('', views.inicio, name="inicio"),
    path('productos/', views.productos, name="productos"),
    path('productos/categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('productos/detalle/<int:idarticulo>/', views.detalle_producto, name='detalle_producto'),
    path('agregar_al_carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('toggle_favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('estado_favorito/<int:idarticulo>/', views.estado_favorito, name='estado_favorito'),
    path("eliminar_item/", views.eliminar_item_carrito, name="eliminar_item"),
    path('login/',LoginView.as_view(template_name = 'registration/login.html') , name="login"),
    path('logout/', views.exit, name='exit'),
    path("checkout/", views.checkout, name="checkout"),
    path("pago-exitoso/", views.pago_exitoso, name="pago_exitoso"),
    path("pago-cancelado/", views.pago_cancelado, name="pago_cancelado"),
    path("factura/<int:factura_id>/pdf/", views.generar_factura_pdf, name="generar_factura_pdf"),
    path("favoritos/", views.ver_favoritos, name="ver_favoritos"),
    path('registro/', views.registrarse, name='registro'),
    
    path('dashboard/', views.inicioDashboard, name="inicio2"),
]