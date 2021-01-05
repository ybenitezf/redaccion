// Página para subir las fotos a PhotoStore
import { Application } from "stimulus";
import ChipsController from "./controllers/chips_controller";
import EditorExcerptController from "./controllers/excerptEditor";
import ImageUploader from "./controllers/image_uploader";
// import CoverageUploadController from "./controllers/newcov_controller";


// stimulus part
const application = Application.start();
application.register('chips', ChipsController);
application.register('editor', EditorExcerptController);
application.register('imageupload', ImageUploader);
