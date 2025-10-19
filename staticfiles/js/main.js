function changeImage(event, src) {
  document.getElementById("mainImage").src = src;
  document
    .querySelectorAll(".thumbnail")
    .forEach((thumb) => thumb.classList.remove("active"));
  event.target.classList.add("active");
}
function getCSRFToken() {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith("csrftoken=")) {
            return cookie.substring("csrftoken=".length, cookie.length);
        }
    }
    return "";
}

document.addEventListener("DOMContentLoaded", function() {
    const btnAgregarCarrito = document.getElementById("btnAgregarCarrito");

    if (btnAgregarCarrito) {
        btnAgregarCarrito.addEventListener("click", function() {
            let urlAgregar = btnAgregarCarrito.getAttribute("data-url");
            let idarticulo = btnAgregarCarrito.getAttribute("data-articulo-id");
            let tallaSeleccionada = document.querySelector('input[name="talla"]:checked');
            let cantidad = document.getElementById("quantity").value;
           
            if (!tallaSeleccionada) {
                alert("Por favor, selecciona una talla antes de agregar al carrito.");
                return;
            }

            let tallaId = tallaSeleccionada.value;

            let formData = new FormData();
            formData.append("idarticulo", idarticulo);
            formData.append("talla", tallaId);
            formData.append("cantidad", cantidad);

            fetch(urlAgregar, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log("Respuesta del servidor:", data);
                if (data.mensaje) {
                    alert("Producto agregado al carrito");

                    // 🔥 ACTUALIZAR CONTADOR DEL CARRITO
                    let cartCount = document.querySelector(".cart-count");
                    if (cartCount) {
                        cartCount.textContent = `(${data.total_carrito})`;
                    }
                } else {
                    console.error("Error:", data);
                }
            })
            .catch(error => console.error("Error en la solicitud:", error));
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector('[data-bs-target="#offcanvasCart"]').addEventListener("click", function () {
        fetch("/carrito/", {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            const cartList = document.querySelector(".list-group");
            cartList.innerHTML = "";

            if (data.items.length > 0) {
                data.items.forEach(item => {
                    const listItem = document.createElement("li");
                    listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "lh-sm");
                    listItem.innerHTML = `
                        <div>
                            <h6 class="my-0">${item.nombre}</h6>
                            <small class="text-body-secondary">Talla: ${item.talla}</small>
                        </div>
                        <span class="text-body-secondary">$${item.precio} x ${item.cantidad}</span>
                        <button class="btn  btn-sm eliminar-item" data-id="${item.id}">
                            ❌
                        </button>
                    `;
                    cartList.appendChild(listItem);
                });

                const totalItem = document.createElement("li");
                totalItem.classList.add("list-group-item", "d-flex", "justify-content-between");
                totalItem.innerHTML = `
                    <span>Total (USD)</span>
                    <strong id="total-carrito">$${data.total}</strong>
                `;
                cartList.appendChild(totalItem);
            } else {
                cartList.innerHTML = `<li class="list-group-item text-center">Tu carrito está vacío.</li>`;
            }

            document.querySelector(".cart-count").textContent = `(${data.cantidad_productos})`;
        })
        .catch(error => console.error("Error al cargar el carrito:", error));
    });

});




document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".list-group").addEventListener("click", function (event) {
        if (event.target.classList.contains("eliminar-item")) {
            let itemId = event.target.getAttribute("data-id");

            fetch("/eliminar_item/", {
                method: "POST",
                body: new URLSearchParams({ "item_id": itemId }),
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.mensaje) {
                    // 🔥 Eliminar el producto del DOM
                    event.target.closest("li").remove();

                    // 🔥 Actualizar el total del carrito
                    let totalCarritoElement = document.getElementById("total-carrito");
                    if (totalCarritoElement) {
                        totalCarritoElement.textContent = `$${data.total.toFixed(2)}`;
                    }

                    // 🔥 Actualizar el contador del carrito
                    let contadorCarrito = document.querySelector(".cart-count");
                    if (contadorCarrito) {
                        contadorCarrito.textContent = `(${data.total_carrito})`;
                    }
                }
            })
            .catch(error => console.error("Error al eliminar producto:", error));
        }
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-favorito").forEach((boton) => {
        let idarticulo = boton.getAttribute("data-articulo-id");

        // Verificar si el artículo está en favoritos al cargar la página
        fetch(`/estado_favorito/${idarticulo}/`)
            .then(response => response.json())
            .then(data => {
                actualizarBotonFavorito(boton, data.favorito);
            })
            .catch(error => console.error("Error al verificar favorito:", error));

        // Agregar evento para alternar favorito
        boton.addEventListener("click", function () {
            let formData = new FormData();
            formData.append("idarticulo", idarticulo);

            fetch("/toggle_favorito/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.mensaje);
                actualizarBotonFavorito(boton, data.favorito);
                actualizarContadorFavoritos(data.total_favoritos); // <-- Actualizar el contador
            })
            .catch(error => console.error("Error:", error));
        });
    });
});

// Función para actualizar el botón correctamente
function actualizarBotonFavorito(boton, esFavorito) {
    if (esFavorito) {
        boton.classList.add("btn-danger");
        boton.classList.remove("btn-outline-secondary");
        boton.innerHTML = '<i class="bi bi-heart-fill"></i> Favorito';
    } else {
        boton.classList.remove("btn-danger");
        boton.classList.add("btn-outline-secondary");
        boton.innerHTML = '<i class="bi bi-heart"></i> Agregar a favorito';
    }
}

function actualizarContadorFavoritos(cantidad) {
    let contador = document.getElementById("favoritos-count");
    if (contador) {
        contador.textContent = `(${cantidad})`;
    }
}

// Evento cuando se agrega o elimina un favorito
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-favorito").forEach((boton) => {
        boton.addEventListener("click", function () {
            fetch("/toggle_favorito/", { 
                method: "POST",
                body: new FormData(),
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                actualizarContadorFavoritos(data.total_favoritos); // 🔄 Actualizar el contador
            })
            .catch(error => console.error("Error:", error));
        });
    });
});


