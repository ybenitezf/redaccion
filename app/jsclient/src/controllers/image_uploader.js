/* Cargador de imagenes para photostore
*  
*  Este es para usar con un formulario que debe incluir los datos generales
*  de la foto + el archivo que se va a subir, por ejemplo:
*  <form action="..." method="POST">
*    <input type="hidden" name="healine" value="...">
*    <input type="hidden" name="creditline" value="...">
*    <input type="hidden" name="keywords" value="...">
*    <input type="hidden" name="excerpt" value="...">
*    <input type="hidden" name="taken_by" value="...">
*    <input type="hidden" name="photo_coverage" value='...'>
*    <input type="file" name="image" accept="image/*" />
*  </form>
*  
*  Si se da el valor de photo_coverage, debe ser el id de una cobertura, en 
*  cuyo caso el resto de los parametros es ignorados y se toman los valores
*  de la cobertura.
*  
*  healine: titular
*  creditline: credito de la foto
*  keywords: lista de palabras claves
*  excerpt: resumen en formato de editorjs
*  taken_by: autor de la foto
*  photo_coverage: id de la cobertura
*/
import { Controller } from "stimulus";


export default class ImageUploader extends Controller {
    static targets = [ "file", "btn" ]

    connect() {
        this.fileTarget.addEventListener('change', (e) => {
            this.sendData()
        });
    }

    sendData(e) {
        // enviar la foto aqui
        const formData = new FormData(this.element)
        const boton = this.btnTarget
        boton.classList.add('disabled')
        fetch(
            this.element.getAttribute('action'),
            {
                method: 'POST',
                body: formData
            }
        ).then( function(r) {
            if (r.ok) {
                r.json().then( function(data) {
                    // esperar antes de redireccionar para que se vea el 
                    // mensaje
                    M.toast({html: 'Foto agregada', classes: 'rounded'})
                    setTimeout(function() {
                        window.location.replace(window.location.href);
                    }, 1500);
                })
            } else {
                M.toast({
                    html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
                    classes: 'rounded red darken-4'
                })
                boton.classList.remove('disabled')
                console.log("Error en la peticion")
            }
        }).catch( function(error) {
            M.toast({
                html: '<b>ERROR</b>: No se pudo guardar, error en el servidor',
                classes: 'rounded red darken-4'
            })
            boton.classList.remove('disabled')
            console.log(error)
        });
    }

}
