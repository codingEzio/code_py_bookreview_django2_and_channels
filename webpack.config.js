const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

// About the `__dirname`:
// https://nodejs.org/docs/latest/api/modules.html#modules_dirname
module.exports = {
    mode: 'development',
    entry: {
        imageSwitcher: './frontend/imageswitcher.js',
    },
    plugins: [
        new BundleTracker({
            filename: './webpack-stats.json',
        }),
    ],
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'main/static/bundles'),
    },
};
