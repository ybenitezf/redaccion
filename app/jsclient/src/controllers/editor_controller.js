import { Controller } from "stimulus";
import ImageTool from '@editorjs/image';
import EditorJS from '@editorjs/editorjs';
import Quote from '@editorjs/quote';
import List from '@editorjs/list';
import Delimiter from '@editorjs/delimiter';
import Warning from '@editorjs/warning';
import Paragraph from '@editorjs/paragraph';
import Header from '@editorjs/header';
import LinkTool from '@editorjs/link'

const axios = require('axios').default;

export default class extends Controller {

  static targets = [ "content" ]

  initialize() {
    this.loadEditorJS.bind(this)
  }

  connect() {
    const apiUrl = this.data.get("apiendpoint");
    var tags = document.getElementById('keywords');
    M.Chips.init(tags, {
      placeholder: "Plabras clave"
    });
    this.loadEditorJS({})
    // cargar datos del editor desde remoto
    // axios.get(apiUrl).then(
    //   (response) => this.loadEditorJS(response.data)
    // ).catch((error) => {
    //     this.loadEditorJS({})
    //     console.log(error)
    //     console.log("No pude cargar " + apiUrl)
    // })
  }

  loadEditorJS(data) {
    $('.editor-tool-box').floatingActionButton();

    this.editor = new EditorJS({
      holder: this.contentTarget.id,

      tools: {
        paragraph: {
          class: Paragraph,
          inlineToolbar: true,
        },
        list: {
          class: List,
          inlineToolbar: true,
        },
        header: {
          class: Header,
          config: {
            levels: [2, 3],
            defaultLevel: 2,
            placeholder: 'Escribe un título'
          }
        },
        image: {
          class: ImageTool,
          types: "image/png,image/jpg",
          buttonContent: "Seleccionar una imágen",
          inlineToolbar: true,
          config: {
            captionPlaceholder: "Pie de foto",
            creditPlaceholder: "Creditos",
            endpoints: {
              byFile: this.data.get("imageupload"),
              byUrl: this.data.get("imagefetchurl"),
            }
          }
        },
        delimiter: Delimiter,
        quote: {
          class: Quote,
          inlineToolbar: true,
          shortcut: 'CMD+SHIFT+O',
          config: {
            quotePlaceholder: 'Entre la cita',
            captionPlaceholder: 'Autor de la cita',
          },
        },
        linkTool: {
          class: LinkTool,
          config: {
            endpoint: this.data.get("linkendpoint")
          }
        },
        warning: {
          class: Warning,
          inlineToolbar: true,
          shortcut: 'CMD+SHIFT+W',
          config: {
            titlePlaceholder: 'Title',
            messagePlaceholder: 'Message',
            author: this.data.get("author")
          },
        },
      },
      placeholder: 'Da clic aquí para comenzar a escribir',
      data: data,

      onReady: () => this.enableGuardar()
    });
  }

  disableGuardar() {
    var el = document.querySelector('*[data-action="editor#guardar"]')
    el.classList.add('disabled')
  }

  enableGuardar() {
    var el = document.querySelector('*[data-action="editor#guardar"]')
    el.classList.remove('disabled')
  }

  guardar(event) {
    // desactivar el boton un momento
    const apiUrl = this.data.get("apiendpoint");
    this.disableGuardar();

    this.editor.save().then( (outData) => {
      axios.put(apiUrl, outData).then(function (response) {
        M.toast({html: 'Tus cambios han sido guardados'})
      }).catch( function (error) {
        M.toast({html: 'No se pudo guardar, error en el servidor'})
        console.log('Saving failed: ', error)
      })
    });

    this.enableGuardar()
  }

  disconnect() {
    if (this.editor) {
      this.editor.destroy();
    }
  }

}
