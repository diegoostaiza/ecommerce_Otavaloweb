from django.shortcuts import render , get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from .models import Articulos,Categoriaarticulos,SubcategoriaArticulos, Carrito,VarianteArticulo,ItemCarrito,Favorito,Clientes,Ventas,Detalle_ventas,Factura, DetalleFactura
from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required , permission_required
from django.contrib.auth import logout, update_session_auth_hash, get_user_model, authenticate
from .forms import  CustomUserCreationForm 

def inicio(request):
    categorias = Categoriaarticulos.objects.annotate(
        num_articulos=Count('subcategoriaarticulos__articulos')
    )
    contexto = {  
        'categorias': categorias,  
    }
    return render(request , 'venta_inicio/inicio.html',contexto)

def productos(request):
    # Filtra los artículos que tienen al menos una variante con stock > 5
    productos = Articulos.objects.annotate(
        total_stock=Sum('variantes__stock')  # Suma el stock de todas sus variantes
    ).filter(total_stock__gt=5, estado_articulo=1)  # Filtra solo los que tienen más de 5 en total

    # Contar cuántos artículos hay en cada categoría
    categorias = Categoriaarticulos.objects.annotate(
        num_articulos=Count('subcategoriaarticulos__articulos', filter=Q(subcategoriaarticulos__articulos__variantes__stock__gt=0))
    )

    paginator = Paginator(productos, 12)  # 12 productos por página
    numero_pag = request.GET.get('page')
    page_obj = paginator.get_page(numero_pag)
    print(productos)

    # Contexto para pasar a la plantilla
    contexto = {
        'productos': page_obj,  
        'categorias': categorias,
        'page_obj': page_obj  # Para paginación en la plantilla
    }

    return render(request, 'ventas_productos/productos.html', contexto)
   


def productos_por_categoria(request, categoria_id):
    categorias = Categoriaarticulos.objects.annotate(
        num_articulos=Count('subcategoriaarticulos__articulos')
    )
  
    categoria = get_object_or_404(Categoriaarticulos, idcategoriaarticulo=categoria_id)

    # Obtener las subcategorías de la categoría seleccionada
    subcategorias = SubcategoriaArticulos.objects.filter(idcategoriaarticulo=categoria)

    # Obtener los productos que pertenecen a esas subcategorías
    productos = Articulos.objects.filter(idsubcategoriaarticulo__in=subcategorias)

    # Paginar los productos
    paginator = Paginator(productos, 6)
    numero_pag = request.GET.get('page')
    page_obj = paginator.get_page(numero_pag)

    # Pasar la información al contexto
    contexto = {
        'categorias': categorias,
        'categoria': categoria,
        'productos': page_obj,  # Se pasa `page_obj` en lugar de `productos` para manejar la paginación
        'subcategorias': subcategorias,
        'page_obj': page_obj
    }
    return render(request, 'ventas_productos/productos_categoria.html', contexto)


@login_required
def detalle_producto(request, idarticulo):
    categorias = Categoriaarticulos.objects.annotate(
        num_articulos=Count('subcategoriaarticulos__articulos')
    )

    articulo = get_object_or_404(Articulos, idarticulo=idarticulo)
    variantes = articulo.variantes.all()  # Obtener las variantes (tallas disponibles)

    contexto = {
        'articulo': articulo,
        'variantes': variantes,
        'categorias': categorias
    }

    return render(request, 'ventas_productos/producto_detalle.html', contexto)


@login_required
def agregar_al_carrito(request):
    if request.method == "POST":
        idarticulo = request.POST.get("idarticulo")
        talla_id = request.POST.get("talla")
        cantidad = int(request.POST.get("cantidad", 1))  # Convertir a número

        articulo = get_object_or_404(Articulos, idarticulo=idarticulo)
        variante = get_object_or_404(VarianteArticulo, idvariante=talla_id)

        # Verificar si hay suficiente stock
        if cantidad > variante.stock:
            return JsonResponse({"error": "No hay suficiente stock disponible."}, status=400)

        # Obtener o crear el carrito del usuario
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

        # Buscar si la variante ya está en el carrito
        item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, variante=variante)

        if not creado:
            # 🔥 Si ya existe, sumamos la cantidad nueva a la actual
            item.cantidad += cantidad
        else:
            # 🔥 Si es nuevo, asignamos la cantidad seleccionada
            item.cantidad = cantidad

        item.save()

        # Calcular el total de productos en el carrito
        total_productos = sum(i.cantidad for i in carrito.itemcarrito_set.all())
        carrito.cantidad_productos = total_productos
        carrito.save()

        return JsonResponse({
            "mensaje": "Producto agregado",
            "total_carrito": total_productos
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)



@login_required
def ver_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()

    if not carrito:
        items = []
        total = 0
    else:
        items = ItemCarrito.objects.filter(carrito=carrito)
        total = sum(item.variante.precio_adicional * item.cantidad for item in items)

    # Si la petición es AJAX, enviamos JSON con los datos del carrito
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carrito_data = {
            "items": [
                {
                    
                    "id": item.ItemCarritoID,
                    "nombre": item.variante.articulo.nombre_articulo,
                    "talla": item.variante.talla_ropa,
                    "precio": item.variante.precio_adicional,
                    "cantidad": item.cantidad,
                }
                for item in items
            ],
            "total": total,
            "cantidad_productos": sum(item.cantidad for item in items)
        }
        return JsonResponse(carrito_data)

    # Para peticiones normales, renderizar una plantilla si fuera necesario
    return render(request, "carrito.html", {"items": items, "total": total})
 
 
@login_required
def eliminar_item_carrito(request):
    if request.method == "POST":
        try:
            item_id = request.POST.get("item_id")
            item = get_object_or_404(ItemCarrito, ItemCarritoID=item_id)  # ⬅️ Asegurar que usamos el campo correcto

            # Obtener el carrito del usuario
            carrito = item.carrito
            item.delete()  # ❌ Eliminar el producto del carrito

            # 🔥 Recalcular el total del carrito después de eliminar
            total_productos = sum(i.variante.precio_adicional * i.cantidad for i in carrito.itemcarrito_set.all())
            carrito.cantidad_productos = sum(i.cantidad for i in carrito.itemcarrito_set.all())
            carrito.save()

            return JsonResponse({
                "mensaje": "Producto eliminado",
                "total": total_productos,
                "total_carrito": carrito.cantidad_productos
            })

        except Exception as e:
            return JsonResponse({"error": f"Error eliminando producto: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

  
    
@login_required
def toggle_favorito(request):
    if request.method == "POST":
        idarticulo = request.POST.get("idarticulo")
        articulo = get_object_or_404(Articulos, idarticulo=idarticulo)

        favorito, creado = Favorito.objects.get_or_create(usuario=request.user, articulo=articulo)

        if creado:
            mensaje = "Añadido a favoritos"
        else:
            favorito.delete()
            mensaje = "Eliminado de favoritos"

        # Obtener la cantidad total de favoritos del usuario
        total_favoritos = Favorito.objects.filter(usuario=request.user).count()

        return JsonResponse({
            "mensaje": mensaje,
            "favorito": creado,
            "total_favoritos": total_favoritos
        })

    return JsonResponse({"error": "Método no permitido"}, status=405)

@login_required
def estado_favorito(request, idarticulo):
    articulo = get_object_or_404(Articulos, idarticulo=idarticulo)
    en_favoritos = Favorito.objects.filter(usuario=request.user, articulo=articulo).exists()
    return JsonResponse({"favorito": en_favoritos})

def exit(request):
    logout(request)
    return redirect('/accounts/login/?next=/ventas/inicio/')



import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from gestion_ventas import settings
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required

def checkout(request):
    if request.method == "POST":
        try:
            # Obtener el carrito del usuario
            carrito = Carrito.objects.filter(usuario=request.user).first()

            if not carrito or not carrito.itemcarrito_set.exists():
                return JsonResponse({"error": "Tu carrito está vacío"}, status=400)

            items_carrito = ItemCarrito.objects.filter(carrito=carrito)

            # Crear los productos para Stripe
            line_items = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": item.variante.articulo.nombre_articulo},
                        "unit_amount": int(item.variante.precio_adicional * 100),  # Convertir a centavos
                    },
                    "quantity": item.cantidad,
                }
                for item in items_carrito
            ]

            # Crear la sesión de pago en Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri("/pago-exitoso/") + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri("/pago-cancelado/"),
            )

            return JsonResponse({"id": session.id})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Carrito, Clientes, Ventas, Detalle_ventas, Factura, DetalleFactura
from django.utils import timezone

def generar_numero_autorizacion():
    return str(random.randint(100000000000, 999999999999))  # Simulación de número de autorización

from decimal import Decimal
def pago_exitoso(request):
    usuario = request.user  # Obtener el usuario autenticado
    session_id = request.GET.get("session_id")  # Obtener el ID de la sesión de pago

    if not session_id:
        return redirect("ventas:productos")  # Si no hay sesión, redirigir a productos

    # Verificar la sesión en Stripe
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status != "paid":
        return redirect("ventas:productos")  # Si no está pagado, redirigir

    # Obtener el carrito del usuario
    carrito = Carrito.objects.filter(usuario=usuario).first()
    if not carrito or not carrito.itemcarrito_set.exists():
        return redirect("ventas:productos")  # Si no hay productos, redirigir

    # Obtener o crear el cliente asociado al usuario
    cliente, _ = Clientes.objects.get_or_create(usuario=usuario)

    # Registrar la venta
    total_venta = sum(item.variante.precio_adicional * item.cantidad for item in carrito.itemcarrito_set.all())
    venta = Ventas.objects.create(idcliente=cliente, total=total_venta)

    # Crear la factura
    factura = Factura.objects.create(
        cliente=cliente,
        fecha_emision=timezone.now(),
        numero_autorizacion=generar_numero_autorizacion(),  # Definir esta función
        total=total_venta
    )

    # Guardar los detalles de la factura
    for item in carrito.itemcarrito_set.all():
        subtotal = item.variante.precio_adicional * item.cantidad  # Precio sin impuestos
        iva = subtotal * Decimal("0.12")  # Calcular IVA (12%)
        total = subtotal + iva  # Total con IVA

        DetalleFactura.objects.create(
            factura=factura,
            articulo=item.variante.articulo,
            cantidad=item.cantidad,
            precio_unitario=item.variante.precio_adicional,
            subtotal=subtotal,
            iva=iva,
            total=total  # Asegurar que total no sea NULL
        )

        # Restar el stock del artículo después de la compra
        item.variante.stock -= item.cantidad
        item.variante.save()

    # Vaciar el carrito después del pago
    carrito.itemcarrito_set.all().delete()
    carrito.cantidad_productos = 0
    carrito.save()

    return render(request, "ventas_productos/pago_exitoso.html", {"factura": factura})


def pago_cancelado(request):
    return render(request, "ventas_productos/pago_cancelado.html")


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def generar_factura_pdf(request, factura_id):
    # Obtener la factura
    factura = get_object_or_404(Factura, idfactura=factura_id)
    detalles = DetalleFactura.objects.filter(factura=factura)

    # Crear la respuesta HTTP con un tipo de contenido PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Factura_{factura.idfactura}.pdf"'

    # Crear el objeto PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle(f"Factura {factura.idfactura}")

    # Establecer posición inicial
    y_position = 750

    # Encabezado de la factura
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y_position, "FACTURA COMERCIAL")
    y_position -= 40
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, y_position, "OTAVALO")
    y_position -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y_position, f"Factura #: {factura.idfactura}")
    pdf.drawString(350, y_position, f"Fecha: {factura.fecha_emision.strftime('%d/%m/%Y')}")
    y_position -= 20
    pdf.drawString(50, y_position, f"Cliente: {factura.cliente.nombre_cliente}")
    pdf.drawString(350, y_position, f"Número de Autorización: {factura.numero_autorizacion}")
    y_position -= 20
 

    # Tabla de productos
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Producto")
    pdf.drawString(250, y_position, "Cantidad")
    pdf.drawString(350, y_position, "Precio Unitario")
    pdf.drawString(450, y_position, "Subtotal")
    y_position -= 20

    pdf.setFont("Helvetica", 12)
    total = 0

    for detalle in detalles:
        pdf.drawString(50, y_position, detalle.articulo.nombre_articulo)
        pdf.drawString(250, y_position, str(detalle.cantidad))
        pdf.drawString(350, y_position, f"${detalle.precio_unitario:.2f}")
        pdf.drawString(450, y_position, f"${detalle.subtotal:.2f}")
        total += detalle.total
        y_position -= 20

    # Línea separadora
    pdf.line(50, y_position, 550, y_position)
    y_position -= 20

    # Total
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(350, y_position, "Total:")
    pdf.drawString(450, y_position, f"${total:.2f}")

    # Cerrar el PDF
    pdf.showPage()
    pdf.save()

    return response



def ver_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user)
    categorias = Categoriaarticulos.objects.annotate(
        num_articulos=Count('subcategoriaarticulos__articulos')
    )
    
    contexto = {
        "favoritos": favoritos,
        'categorias': categorias,
    }

    return render(request, "ventas_productos/favoritos.html", contexto)

def registrarse(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Guardar el usuario
            user = form.save()

            # Crear el registro en Clientes
            Clientes.objects.create(
                usuario=user,
                nombre_cliente=form.cleaned_data['first_name'],
                correo_cliente=form.cleaned_data['email'],
                celular_cliente=form.cleaned_data['celular_cliente'],  # Nuevo campo
                direccion=form.cleaned_data['direccion'],  # Nuevo campo
            )

            return redirect('ventas:inicio')
        else:
            print('Error en el formulario:', form.errors)
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/registro.html', context)




from datetime import date
from django.shortcuts import render
from django.db import connection
from django.db.models import Sum
import json
from decimal import Decimal


def inicioDashboard(request):
    fecha_get = request.GET.get('fecha_get', 'Hoy')
    fecha_actual = date.today()

    # Determinar el rango de fechas en base a `fecha_get`
    if fecha_get.lower() == 'hoy':
        fecha_inicio = fecha_actual
    elif fecha_get.lower() == 'mes':
        fecha_inicio = fecha_actual.replace(day=1)
    elif fecha_get.lower() == 'año':
        fecha_inicio = fecha_actual.replace(month=1, day=1)
    else:
        fecha_inicio = fecha_actual
    
    mes_actual = fecha_actual.month
    año_actual = fecha_actual.year

    # Calcular las ganancias mensuales
    ganancias_mensuales = []
    for mes in range(1, 13):
        ventas_mes = Ventas.objects.filter(fecha_venta__year=año_actual, fecha_venta__month=mes).aggregate(total_ventas=Sum('total'))
        ganancias_mes = ventas_mes['total_ventas'] or Decimal('0')
        ganancias_mes_float = float(ganancias_mes)
        ganancias_mensuales.append(ganancias_mes_float)
    ganancias_mensuales_json = json.dumps(ganancias_mensuales)
    
    with connection.cursor() as cursor:
        # Procedimientos almacenados o consultas directas
        cursor.execute("SELECT retorna_total_usuarios()")
        resultado2_c = cursor.fetchone()[0]
        
        cursor.execute("SELECT retorna_total_ventas()")
        resultado5_ven = cursor.fetchone()[0]
        
        cursor.execute("SELECT retorna_total_articulos()")
        resultado3_art = cursor.fetchone()[0]
        
        cursor.execute("SELECT calcular_ganancias_mensuales(%s, %s)", [mes_actual, año_actual])
        ganancias_mensual = cursor.fetchone()[0]
        
        cursor.execute("SELECT calcular_ganancias_anuales(%s)", [año_actual])
        ganancias_anual = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM obtener_ultimas_10_ventas_con_cliente()")
        res_ultima10_ventas = cursor.fetchall()
        
        cursor.execute("SELECT retorna_existencia_actual()")
        resultado8_existe_act = cursor.fetchone()[0]

        cursor.execute("SELECT retorna_existencia_total()")
        resultado9_existe_tot = cursor.fetchone()[0]
        
    contexto = {
        'total_usuarios': resultado2_c,
        'total_ventas': resultado5_ven,
        'total_articulos': resultado3_art,
        'ganancias_m': ganancias_mensual,
        'ganancias_anual': ganancias_anual,
        'ultima10_ventas': res_ultima10_ventas,
        'total_existencia_actual': resultado8_existe_act,
        'total_existencia_total': resultado9_existe_tot,
        'des_fecha': fecha_get.capitalize(),
        'resumen_ganancias': ganancias_mensuales_json
    }
    
    return render(request, 'inventario_principal/inicioDashboard.html', contexto)


