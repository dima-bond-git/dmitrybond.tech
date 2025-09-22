/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_CAL_ORIGIN: string;
  readonly PUBLIC_BLOG_ENABLED: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}