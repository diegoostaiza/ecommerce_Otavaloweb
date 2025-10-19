from .models import Carrito , Favorito

def carrito_context(request):
    if request.user.is_authenticated:
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
        return {'carrito_count': carrito.cantidad_productos}
    return {'carrito_count': 0}

def favoritos_count(request):
    if request.user.is_authenticated:
        total_favoritos = Favorito.objects.filter(usuario=request.user).count()
    else:
        total_favoritos = 0

    return {"total_favoritos": total_favoritos}
