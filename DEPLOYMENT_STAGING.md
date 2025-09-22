Staging deployment checklist

1. Caddy vhost (staging)

Add a new site block:

```
staging.dmitrybond.tech {
  encode zstd gzip
  root * /srv/dmb/site-staging
  file_server

  @html { path *.html }
  header @html Cache-Control "no-cache"

  @assets { path /_astro/* *.css *.js *.svg *.woff2 }
  header @assets Cache-Control "public, max-age=31536000, immutable"
}
```

2. Server directories

- Create directory: /opt/dmb/site-staging
- Ensure Caddy has read access to /srv/dmb/site-staging (bind mount or copy)

3. Build and ship

Run locally or in CI:
```
npm ci
npm run build
```
Copy build to staging host:
```
rsync -avz --delete dist/ user@host:/opt/dmb/site-staging/
```
Reload Caddy if needed:
```
sudo systemctl reload caddy
```

4. Smoke test

- https://staging.dmitrybond.tech/en/about/ renders Hydrogen styles
- https://staging.dmitrybond.tech/ru/about/ renders RU version
- https://staging.dmitrybond.tech/en/cv/ has buttons:
  - Download EN → /files/cv/dmitry-bondarenko-en.pdf
  - Download RU → /files/cv/dmitry-bondarenko-ru.pdf
- https://staging.dmitrybond.tech/en/bookme/ iframe uses PUBLIC_CAL_ORIGIN
- Redirects:
  - / → /en/about/
  - /en/ → /en/about/
  - /ru/ → /ru/about/

5. Environment

Add to .env (or CI env vars):
```
PUBLIC_CAL_ORIGIN=https://cal.dmitrybond.tech
PUBLIC_BLOG_ENABLED=false
```

6. Acceptance

- npm run build passes
- Dist contains localized pages with trailing slash directories
- No blog pages while PUBLIC_BLOG_ENABLED=false


