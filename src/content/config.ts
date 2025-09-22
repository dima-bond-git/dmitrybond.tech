import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    lang: z.enum(['en','ru']),
    excerpt: z.string().optional(),
    cover: z.string().optional(),
    draft: z.boolean().default(true),
  })
});

export const collections = { blog };


