import { Controller } from "stimulus"

export default class ChipsController extends Controller {
    // controlador simple para los chips de materializecss
    static values = { tags: String }
    static targets = ["vista"]

    initialize() {
        const valores_iniciales = JSON.parse(this.tagsValue)
        M.Chips.init(
            this.vistaTarget, {
                placeholder: "Plabras clave",
                secondaryPlaceholder: "+Palabra",
                data: valores_iniciales
            }
        )
    }

}
