const path = require( 'path' );

module.exports = {
    context: __dirname,
    entry: {
      editorcomp: './src/editorpage.js',
      photoupload: './src/photostoreupload.js'
    },
    output: {
        path: path.resolve( __dirname, '../application/static/js' ),
        filename: '[name].js',
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: 'babel-loader',
            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            }
        ]
    },
    externals: {
      jquery: 'jQuery'
    }
};
