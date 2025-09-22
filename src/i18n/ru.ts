export default {
  nav: { about: 'Обо мне', book: 'Записаться', blog: 'Мысли', cv: 'CV' },
  seo: {
    about: { title: 'Обо мне • Дмитрий Бонд', desc: 'Cloud‑консультант и технический PM. 8+ лет: AWS/Azure/GCP.' },
    book: { title: 'Запись на встречу • Дмитрий Бонд', desc: 'Выберите удобное время для консультации.' },
    cv: { title: 'CV • Дмитрий Бонд', desc: 'Резюме: навыки, опыт, проекты.' },
    blog: { title: 'Блог • Дмитрий Бонд', desc: 'Заметки о облаках, продукте, инженерии.' }
  },
  about: { title: 'Cloud‑консультант и технический PM', sub: '8+ лет: AWS/Azure/GCP' },
  book: { title: 'Запись на встречу', note: 'Выберите слот ниже.' },
  cv: {
    heroTitle: 'Резюме / CV',
    download: 'Скачать PDF',
    skills: { cloud: ['AWS','Azure','GCP'], devops: ['CI/CD','Docker','K8s'] },
    experience: [ { company: 'Top Notch Technologies', role: 'Основатель и CTO', period: '2021—н.в.', bullets: ['Построил консалтинговую практику','Руководил миграциями в облако','Вёл кросс‑функциональные команды'] } ],
    projects: [ { title: 'Wine Vault', text: 'MVP подписочного приложения', link: '#' } ]
  }
} as const;


