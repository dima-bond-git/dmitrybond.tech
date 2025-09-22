import { defineConfig } from 'astro/config';
import path from 'node:path';
export default defineConfig({
  trailingSlash: 'always',
  site: 'https://dmitrybond.tech',
  output: 'static',
  vite: {
    resolve: {
      alias: {
        hydrogen: path.resolve('./hydrogen'),
      },
    },
  },
});