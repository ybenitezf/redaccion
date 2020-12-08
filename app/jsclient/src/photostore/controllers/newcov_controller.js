import { Controller } from "stimulus";
import EditorJS from "@editorjs/editorjs";
import validate, { async } from "validate.js";
const Validator = require('validate.js');
const Uppy = require("@uppy/core");
const XHRUpload = require("@uppy/xhr-upload");
const Dashboard = require("@uppy/dashboard");
const SpanishUppy = require("@uppy/locales/lib/es_ES");

require('@uppy/core/dist/style.css')
require('@uppy/dashboard/dist/style.css')

const restricciones = {
    headline: {
        presence: {
            allowEmpty: false,
            message: "^Título no puede estar vacio"
        }
    },
    keywords: {
        presence: {
            allowEmpty: false,
            message: "^Debes incluir palabras clave"
        }
    },
    excerpt: {
        presence: {
            allowEmpty: false,
            message: "^Describe estas imágenes"
        },
        length: function (value, attributes, attributeName, options, constraints) {
            if ( value ) {
                if ( validate.isEmpty(value.blocks) ) {
                    return {message: "^Describe estas imágenes"}
                } else {
                    return null
                }
            }

            return false
        }
    }
}

export default class extends Controller {

    static targets = [
        "resumen", "tags", "headline", "creditline", "photos"
    ]

    static values = {
        uploadendpoint: String
    }

    initialize() {
        console.log("Inicializando newcov")
    }

    disableGuardar() {
        var el = document.querySelector('*[data-action="click->newcov#save"]')
        el.classList.add('disabled')
    }
    
    enableGuardar() {
        var el = document.querySelector('*[data-action="click->newcov#save"]')
        el.classList.remove('disabled')
    }

    connect() {
        this.editor = new EditorJS({
            holder: this.resumenTarget.id,
            minHeight: 20,
            placeholder: "Escribe aquí una descripción de la cobertura"
        })
        M.Chips.init(this.tagsTarget, {
            placeholder: "Plabras clave",
            secondaryPlaceholder: "+Palabra"
        });

        this.uppy = new Uppy({
            autoProceed: false,
            locale: SpanishUppy,
            restrictions: {
                allowedFileTypes: ['image/*']
            }
        }).use(Dashboard, {
            inline: true,
            hideUploadButton: true,
            target: this.photosTarget,
            height: 480
        }).use(XHRUpload, {
            fieldName: 'image',
            endpoint: this.uploadendpointValue
        })
    }

    disconnect() {
        if (this.editor) {
            this.editor.destroy()
        }
    }

    isValid(values) {
        // validar el formulario
        const results = Validator(values, restricciones)

        if (results) {
            // aqui hay errores
            for (const [field, msg] of Object.entries(results) ) {
                M.toast({
                    html: msg,
                    classes: 'red rounded'
                });
            }
            return false
        }
        
        return true
    }

    save(event) {
        event.preventDefault();
        event.stopPropagation();
        this.disableGuardar();

        // recopilar los datos, el editor tiene prioridad
        var tags = [];
        M.Chips.getInstance(this.tagsTarget).chipsData.forEach((tagData) => {
          tags.push(tagData.tag);
        })
        this.editor.save().then((description) => {

            var values = {
                headline: this.headlineTarget.value,
                keywords: tags,
                excerpt: description
            }

            console.log(values)
            if (this.isValid(values)) {
                console.log("Todo correcto de momento ...")
                // agregar información a los metas de las imagenes
                // values.excerpt debe ser convertido a string
                values.excerpt = JSON.stringify(description)
                this.uppy.setMeta(values)

                // intentar mandar las fotos 
                this.uppy.upload().then((result) => {
                    console.info('Successful uploads:', result.successful)
                  
                    if (result.failed.length > 0) {
                      console.error('Errors:')
                      result.failed.forEach((file) => {
                        console.error(file.error)
                      })
                    }
                })
                // enviar la información al servidor
            } else {
                console.log("Faltan datos")
            }

        })

        this.enableGuardar();
    }

}
