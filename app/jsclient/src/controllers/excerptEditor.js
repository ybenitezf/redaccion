import { Controller } from "stimulus"
import EditorJS from "@editorjs/editorjs";

export default class EditorExcerptController extends Controller {
    static values = { entrada: String }
    static targets = ["editor"]

    connect() {
        var data = JSON.parse(this.entradaValue)
        this.editor = new EditorJS({
            holder: this.editorTarget.id,
            minHeight: 20,
            data: data,
            placeholder: "Escribe aquí una descripción de la cobertura"
        })
    }

    disconnect() {
        if (this.editor) {
            this.editor.destroy()
        }
    }
}
