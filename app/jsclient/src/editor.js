import $ from 'jquery';
import { Application } from "stimulus";
import { definitionsFromContext } from "stimulus/webpack-helpers";

window.jQuery = $; window.$ = $;

// stimulus part
const stiapp = Application.start()
const sticontext = require.context("./controllers", true, /\.js$/)
stiapp.load(definitionsFromContext(sticontext))
