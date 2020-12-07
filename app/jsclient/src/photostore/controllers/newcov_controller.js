import { Controller } from "stimulus";
import EditorJS from "@editorjs/editorjs";
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
            message: "no puede estar vacio"
        }
    }
}

export default class extends Controller {

    static targets = [
        "resumen", "tags", "headline", "creditline", "photos"
    ]

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
            endpoint: 'http://no.existe.com'
        })
    }

    disconnect() {
        if (this.editor) {
            this.editor.destroy()
        }
    }

    isValid() {
        // validar el formulario
        var values = {
            headline: this.headlineTarget.value
        }

        const results = Validator(values, restricciones)

        if (results) {
            // aqui hay un error
            console.log(results)
            return false
        }
        
        return true
    }

    save(event) {
        event.preventDefault();
        event.stopPropagation();
        this.disableGuardar();

        if (this.isValid()) {
            console.log("Todo correcto")
        } else {
            console.log("Faltan datos")
        }
        this.enableGuardar();
    }

}
