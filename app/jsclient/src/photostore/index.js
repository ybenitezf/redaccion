import { Application } from "stimulus";
import { definitionsFromContext } from "stimulus/webpack-helpers";

const photostoreapp = Application.start();
const photostoreapp_ctx = require.context("./controllers", true, /\.js$/)
photostoreapp.load(definitionsFromContext(photostoreapp_ctx))
