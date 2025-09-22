export default {
  nav: { about: 'About me', book: 'Book me', blog: 'My blog', cv: 'CV' },
  seo: {
    about: { title: 'About me • Dmitry Bond', desc: 'Cloud Consultant & Technical PM. 8+ years across AWS/Azure/GCP.' },
    book: { title: 'Book a meeting • Dmitry Bond', desc: 'Pick a slot for a consultation.' },
    cv: { title: 'CV • Dmitry Bond', desc: 'Resume: skills, experience, projects.' },
    blog: { title: 'Blog • Dmitry Bond', desc: 'Notes on cloud, product, engineering.' }
  },
  about: { title: 'Cloud Consultant & Technical PM', sub: '8+ years across AWS/Azure/GCP' },
  book: { title: 'Book a meeting', note: 'Pick a slot below.' },
  cv: {
    heroTitle: 'Resume / CV',
    download: 'Download PDF',
    skills: { cloud: ['AWS','Azure','GCP'], devops: ['CI/CD','Docker','K8s'] },
    experience: [ { company: 'Top Notch Technologies', role: 'Founder & CTO', period: '2021—Now', bullets: ['Built consulting practice','Delivered cloud migrations','Led cross‑functional teams'] } ],
    projects: [ { title: 'Wine Vault', text: 'Subscription app MVP', link: '#' } ]
  }
} as const;


