const path = require( 'path' );

module.exports = {
    context: __dirname,
    entry: {
      editorcomp: './src/editor.js',
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
            }
        ]
    },
    externals: {
      jquery: 'jQuery'
    }
};
