from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Categoriaarticulos(models.Model):
    idcategoriaarticulo = models.AutoField(primary_key=True)
    descripcion_categoriaarticulo = models.CharField(max_length=100, verbose_name="Descripción ")

    def __str__(self):
        return self.descripcion_categoriaarticulo

    class Meta:
        db_table = "categoriaarticulos"
        verbose_name = "Categoría Artículo"
        verbose_name_plural = "Categoría Artículos"

class SubcategoriaArticulos(models.Model):
    idsubcategoriaarticulo = models.AutoField(primary_key=True)
    idcategoriaarticulo = models.ForeignKey(Categoriaarticulos, on_delete=models.PROTECT)
    descripcion_subcategoriaarticulo = models.CharField(max_length=100, verbose_name="Descripción ")

    def __str__(self):
        return self.descripcion_subcategoriaarticulo

    class Meta:
        db_table = "subcategoriaarticulos"
        verbose_name = "Subcategoría Artículo"
        verbose_name_plural = "Subcategoría Artículos"

# Artículos principales (sin talla ni número)
class Articulos(models.Model):
    idarticulo = models.AutoField(primary_key=True)
    codigoarticulo = models.CharField(max_length=10, unique=True, verbose_name="Código de Producto ")
    idsubcategoriaarticulo = models.ForeignKey(SubcategoriaArticulos, on_delete=models.CASCADE, related_name="articulos", verbose_name="Subcategoría")
    imagen = CloudinaryField('imagen', folder='productos/', null=True, blank=True)
    nombre_articulo = models.CharField(max_length=100, verbose_name="Nombre ")
    descripcion_articulo = models.CharField(max_length=255, verbose_name="Descripción ")
    precio_base = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio Base")  # Precio base sin considerar talla
    estado_articulo = models.IntegerField(default=1, verbose_name="Estado")

    def __str__(self):
        return self.nombre_articulo

    class Meta:
        db_table = "articulos"
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

# Modelo para variantes de un mismo artículo (Tallas, Números de calzado, Stock)
class VarianteArticulo(models.Model):
    idvariante = models.AutoField(primary_key=True)
    articulo = models.ForeignKey(Articulos, on_delete=models.CASCADE, related_name="variantes", verbose_name="Artículo")
    
    # Tallas y números de calzado
    TIPO_VARIANTE_CHOICES = [
        ('ropa', 'Talla de ropa'),
        ('calzado', 'Número de calzado'),
    ]
    tipo_variante = models.CharField(max_length=10, choices=TIPO_VARIANTE_CHOICES, verbose_name="Tipo de Variante")
    
    talla_ropa = models.CharField(max_length=5, null=True, blank=True, verbose_name="Talla de Ropa")  # S, M, L, XL, etc.
    numero_calzado = models.IntegerField(null=True, blank=True, verbose_name="Número de Calzado")  # 36, 37, 38, etc.

    stock = models.IntegerField(default=0, verbose_name="Stock")
    precio_adicional = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Precio Adicional")  # Si alguna variante es más cara

    def precio_final(self):
        return self.articulo.precio_base + self.precio_adicional

    def __str__(self):
        talla_o_numero = self.talla_ropa if self.talla_ropa else f"Número {self.numero_calzado}"
        return f"{self.articulo.nombre_articulo} - {talla_o_numero} ({self.stock} en stock)"

    class Meta:
        db_table = "variantes_articulo"
        verbose_name = "Variante de Artículo"
        verbose_name_plural = "Variantes de Artículos"
        
# Modelo de carrito de compras
class Carrito(models.Model):
    CarritoID = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad_productos = models.IntegerField(default=0)
    productos = models.ManyToManyField('Articulos')

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

# Item de carrito (relación con variantes de productos)
class ItemCarrito(models.Model):
    ItemCarritoID = models.AutoField(primary_key=True)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    variante = models.ForeignKey(VarianteArticulo, on_delete=models.CASCADE)  # Relación con la variante
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.variante} ({self.cantidad} unidades) en Carrito de {self.carrito.usuario.username}"

# Clientes y direcciones
class Clientes(models.Model):
    idcliente = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=30, verbose_name="Nombre ")
    correo_cliente = models.EmailField(max_length=80, verbose_name="Correo ")
    celular_cliente = models.CharField(max_length=10, verbose_name="Celular ")
    direccion = models.CharField(max_length=200, verbose_name="Dirección ")

    def __str__(self):
        return self.nombre_cliente

    class Meta:
        db_table = "clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

# Ventas y detalles de ventas
class Ventas(models.Model):
    idventa = models.AutoField(primary_key=True)
    idcliente = models.ForeignKey(Clientes, on_delete=models.PROTECT, verbose_name="Cliente")
    fecha_venta = models.DateField(auto_now_add=True, verbose_name="Fecha")
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total")
    
    def __str__(self):
        return f"Venta {self.idventa} - {self.idcliente.nombre_cliente}"

    class Meta:
        db_table = "ventas"
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

class Detalle_ventas(models.Model):
    iddetalle_venta = models.AutoField(primary_key=True)
    idventa = models.ForeignKey(Ventas, on_delete=models.RESTRICT, verbose_name="Venta")
   
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio Unitario")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total")

    def __str__(self):
        return f'{self.idventa.idventa} - {self.idvariantearticulo}'

    class Meta:
        db_table = "detalle_ventas"
        verbose_name = "Detalle Venta"
        verbose_name_plural = "Detalle Ventas"

class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulos, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'articulo')  # Para evitar duplicados

    def __str__(self):
        return f"{self.usuario.username} - {self.articulo.nombre_articulo}"
    
    
    
    

from datetime import datetime

class Factura(models.Model):
    idfactura = models.AutoField(primary_key=True)
    cliente = models.ForeignKey("Clientes", on_delete=models.PROTECT)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total")
    numero_autorizacion = models.CharField(max_length=50, unique=True, verbose_name="Número de Autorización")
    
    def __str__(self):
        return f"Factura {self.idfactura} - {self.cliente.nombre_cliente}"

    class Meta:
        db_table = "facturas"
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

class DetalleFactura(models.Model):
    iddetalle = models.AutoField(primary_key=True)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    articulo = models.ForeignKey("Articulos", on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    iva = models.DecimalField(max_digits=15, decimal_places=2, default=0.12)
    total = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Detalle de Factura {self.factura.idfactura} - {self.articulo.nombre_articulo}"

    class Meta:
        db_table = "detalles_factura"
        verbose_name = "Detalle Factura"
        verbose_name_plural = "Detalles Factura"

    
    
    