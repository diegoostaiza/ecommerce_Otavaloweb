document.getElementById('botonModificar').addEventListener('click', function () {
    Swal.fire({
        title: "¿Estás seguro de modificar?",
        text: "Esta acción no se puede deshacer",
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Aceptar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#4169E1"
    }).then(function (result) {
        if (result.isConfirmed) {
            // Si el usuario confirma, enviar el formulario
            document.getElementById('miFormulario').submit();
        }
    });
});

function Eliminar_Elemento(id, url){
    Swal.fire({
        title: "¿Estás seguro de eliminar?",
        text: "Esta acción no se puede deshacer",
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Aceptar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#4169E1"
    })
    .then(function(result){
        if(result.isConfirmed){
            window.location.href = url + id + "/";
        }
    })
}
