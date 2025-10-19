from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Importa tus modelos
from .models import (
    Articulos,
    Categoriaarticulos,
    SubcategoriaArticulos,
    Clientes,
    VarianteArticulo,
   
)

# Registra los modelos en el panel de administración
admin.site.register(Articulos)
admin.site.register(VarianteArticulo)
admin.site.register(Categoriaarticulos)
admin.site.register(SubcategoriaArticulos)
admin.site.register(Clientes)


