import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: '../static/js/bundled',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: 'main.js',
      },
      output: {
        // Disable Cache Busting here, as it will be Done by Django via the whitenoise
        // CompressedManifestStaticFilesStorage
        entryFileNames: '[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
});
