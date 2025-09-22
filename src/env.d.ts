/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly PUBLIC_BLOG_ENABLED?: string;
  readonly PUBLIC_CAL_ORIGIN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}