// Simple semi-dynamic renderer powered by /data/content.json

const STATE = {
  lang: localStorage.getItem('lang') || 'en',
  data: null
};

const qs = (s, el = document) => el.querySelector(s);
const qsa = (s, el = document) => [...el.querySelectorAll(s)];
const t = (obj) => (obj && (obj[STATE.lang] || obj.en)) || '';

// async function loadData() {
//   const res = await fetch('data/content.json', { cache: 'no-store' });
//   STATE.data = await res.json();
// }
async function loadData() {
  // Previously fetched JSON, now we already have CONTENT loaded
  STATE.data = contentData;
}

function setHtmlLang() {
  document.documentElement.lang = STATE.lang;
}

function saveLang() {
  localStorage.setItem('lang', STATE.lang);
}

function setLang(lang) {
  STATE.lang = lang;
  saveLang();
  setHtmlLang();
  renderAll();
}

function initLangDropdown() {
  const dd = qs('#langDropdown');
  const btn = qs('#langBtn');
  dd.innerHTML = '';
  Object.entries(STATE.data.languages).forEach(([code, label]) => {
    const li = document.createElement('li');
    li.innerHTML = `<a class="dropdown-item" href="#" data-lang="${code}">${label}</a>`;
    dd.appendChild(li);
  });
  btn.textContent = STATE.data.languages[STATE.lang] || 'English';

  dd.addEventListener('click', (e) => {
    const a = e.target.closest('[data-lang]');
    if (!a) return;
    e.preventDefault();
    const lang = a.getAttribute('data-lang');
    setLang(lang);
    qs('#langBtn').textContent = STATE.data.languages[lang];
  });
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
}

function renderMenu() {
  const ul = qs('#dynamicMenu');
  ul.innerHTML = '';
  STATE.data.menus.forEach((id) => {
    const title = t(STATE.data.texts[id]?.title) || id;
    const li = document.createElement('li');
    li.className = 'nav-item';
    li.innerHTML = `<a class="nav-link" href="#${id}" data-target="${id}">${title}</a>`;
    ul.appendChild(li);
  });
}

function sectionAbout(sec) {
  const title = t(sec.title);
  const body = t(sec.body);
  const img = sec.image;
  const cards = sec.ctaCards || [];

  return `
    <section id="About" class="section">
      <br/>
      <div class="container">
        <h2>${title}</h2>
        <div class="row align-items-center">
          <div class="col-lg-6 mb-3">
            <p class="lead">${body}</p>
          </div>
          <div class="col-lg-6 text-center mb-3">
            ${img ? `<img src="${img}" class="img-fluid" alt="About">` : ''}
          </div>
        </div>
        ${cards.length ? `
          <div class="row grid-gap-20 mt-3">
            ${cards.map(card => `
              <div class="col-md-6 col-lg-4">
                <a href="${card.href}" target="_blank" rel="noopener" class="text-decoration-none">
                  <div class="card text-center p-3 h-100">
                    <img class="card-img-top mx-auto" src="${card.img}" alt="">
                    <div class="card-body">
                      <p class="card-text">${t(card.text)}</p>
                    </div>
                  </div>
                </a>
              </div>
            `).join('')}
          </div>` : ''}
      </div>
    </section>
  `;
}

function sectionGeneric(id, sec) {
  const title = t(sec.title);
  const body = t(sec.body);
  const img = sec.image;
  const link = sec.link;

  return `
    <section id="${id}" class="section">
      <br/>
      <div class="container">
        <h2>${title}</h2>
        <div class="row align-items-center">
          ${img ? `
            <div class="col-lg-4 text-center mb-3">
              <img src="${img}" class="img-fluid" alt="${title}">
            </div>
            <div class="col-lg-8">
              ${body ? `<p class="lead">${body}</p>` : ''}
              <p class="lead">Read the <a href="${link}" target="_blank" rel="noopener" class="w-100 text-decoration-none">documentation</a></p>
            </div>
          ` : `
            <div class="col-12">
              ${body ? `<p class="lead">${body}</p>` : ''}
              <p class="lead">Read the <a href="${link}" target="_blank" rel="noopener" class="w-100 text-decoration-none">documentation</a></p>
            </div>
          `}
        </div>
      </div>
    </section>
  `;
}

function sectionResources(sec) {
  const title = t(sec.title);
  const cards = sec.cards || [];
  return `
    <section id="Resources" class="section">
      <br/>
      <div class="container">
        <h2>${title}</h2>
        <div class="row grid-gap-10" style="border:0px solid red;">
          ${cards.map(card => `
            <div class="col-sm-6 col-lg-3 d-flex">
              <a href="${card.href}" target="_blank" rel="noopener" class="w-100 text-decoration-none">
                <div class="card text-center p-3">
                  <img class="card-img-top mx-auto" src="${card.img}" alt="">
                  <div class="card-body">
                    <p class="card-text">${t(card.text)}</p>
                  </div>
                </div>
              </a>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}

function sectionContributors(sec) {
  const title = t(sec.title);
  const cards = sec.cards || [];
  return `
    <section id="Contributors" class="section">
      <br/>
      <div class="container">
        <h2>${title}</h2>
        <div class="row grid-gap-10" style="border:0px solid red;">
          ${cards.map(card => `
            <div class="col-sm-6 col-lg-3 d-flex">
              <a href="${card.project_link}" target="_blank" rel="noopener" class="w-100 text-decoration-none">
                <div class="card text-center p-3">
                  <img class="card-img-top mx-auto" src="${card.img}" alt="">
                  <div class="card-body">
                    <p class="card-text">${card.name}</p>
                    <p class="card-text">${card.year} ${t(card.sub_title)}</p>
                  </div>
                </div>
              </a>
            </div>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}


function sectionContact(sec) {
  const title = t(sec.title);
  const people = sec.people || [];
  const logos = sec.footerLogos || [];
  return `
    <section id="ContactUs" class="section">
      <div class="container">
        <h2>${title}</h2>
        <div class="card border-0 text-center">
          <div class="card-body">
            ${people.map(p => `<a href="${p.href}" class="card-link mx-2" target="_blank">${p.label}</a>`).join(' ')}
          </div>
        </div>
        ${logos.length ? `
          <div class="footer-logos d-flex justify-content-center align-items-center gap-4 mt-4">
            ${logos.map(l => `<img src="${l.src}" alt="${l.alt}">`).join('')}
          </div>` : ''}
      </div>
    </section>
  `;
}

function renderSections() {
  const app = qs('#app');
  const d = STATE.data.texts;
  let html = '';
  html += sectionAbout(d.About);
  html += sectionGeneric('Documentation', d.Documentation);
  html += sectionResources(d.Resources);
  html += sectionContributors(d.Contributors);
  html += sectionContact(d.ContactUs);
  app.innerHTML = html;
}

function initActiveLinkOnScroll() {
  const links = qsa('.nav-link');
  const map = new Map();
  links.forEach(link => {
    const id = link.getAttribute('href')?.slice(1);
    const el = id ? qs(`#${id}`) : null;
    if (id && el) map.set(id, { link, el });
  });

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const id = entry.target.id;
      const rec = map.get(id);
      if (!rec) return;
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        rec.link.classList.add('active');
      }
    });
  }, { root: null, rootMargin: '0px 0px -60% 0px', threshold: 0.1 });

  map.forEach(({ el }) => obs.observe(el));
}

function renderAll() {
  renderMenu();
  renderSections();
  initActiveLinkOnScroll();
}

async function bootstrap() {
  initTheme();
  await loadData();
  setHtmlLang();
  initLangDropdown();
  renderAll();

  // Theme toggle button
  qs('#themeToggle').addEventListener('click', toggleTheme);
}

document.addEventListener('DOMContentLoaded', bootstrap);
