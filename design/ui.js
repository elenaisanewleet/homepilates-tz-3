(() => {
  const menuButton = document.querySelector('.burger');
  const menu = document.querySelector('#sections');
  function showMenu(open, focusButton = false) {
    menuButton.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('open', open);
    if (focusButton) menuButton.focus();
  }
  menuButton.addEventListener('click', () => {
    const open = !menu.classList.contains('open');
    showMenu(open);
    if (open) menu.querySelector('a').focus();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && menu.classList.contains('open')) showMenu(false, true);
  });
  document.addEventListener('click', e => {
    if (!e.target.closest('.bar') || e.target.closest('.nav a')) showMenu(false);
  });
  const slides = Array.from(document.querySelectorAll('[data-slide]'));
  if (slides.length) {
    let active = 0;
    function move(step) {
      slides[active].hidden = true;
      active = (active + step + slides.length) % slides.length;
      slides[active].hidden = false;
      document.querySelector('[data-count]').textContent = '0' + (active + 1) + ' / 03';
    }
    document.querySelector('[data-prev]').addEventListener('click', () => move(-1));
    document.querySelector('[data-next]').addEventListener('click', () => move(1));
  }
  const cookie = document.querySelector('.cookie-box');
  const reopen = document.querySelector('[data-cookie-open]');
  const key = 'homepilates.opend.review.1';
  let stored;
  try { stored = JSON.parse(localStorage.getItem(key)); } catch {}
  cookie.hidden = !!stored;
  if (stored) {
    cookie.elements.analytics.checked = stored.analytics;
    cookie.elements.ads.checked = stored.ads;
  }
  reopen.addEventListener('click', () => {
    cookie.hidden = false;
    cookie.querySelector('details').open = true;
    cookie.querySelector('summary').focus();
  });
  cookie.addEventListener('submit', e => {
    e.preventDefault();
    if (e.submitter?.name === 'essential') cookie.elements.ads.checked = cookie.elements.analytics.checked = false;
    try {
      localStorage.setItem(key, JSON.stringify({analytics:cookie.elements.analytics.checked, ads:cookie.elements.ads.checked}));
    } catch {}
    cookie.hidden = true;
    if (reopen.getBoundingClientRect().top < innerHeight) reopen.focus({preventScroll:true});
  });
  document.querySelector('[data-feedback]')?.addEventListener('submit', e => {
    e.preventDefault();
    e.currentTarget.querySelector('[role=status]').textContent = 'Сообщение осталось в прототипе. Для отправки требуется подключить форму к студии.';
  });
  document.querySelectorAll('[data-view]').forEach(panel => {
    const button = panel.querySelector('button');
    const viewer = panel.querySelector('.viewer');
    const label = button.textContent;
    button.addEventListener('click', () => {
      const opening = viewer.hidden;
      viewer.hidden = !opening;
      button.setAttribute('aria-expanded', String(opening));
      button.textContent = opening ? 'Скрыть' : label;
      viewer.replaceChildren();
      if (!opening) return;
      const note = document.createElement('p');
      note.textContent = 'Если окно пустое, проверьте подключение к сервису.';
      const frame = document.createElement('iframe');
      frame.src = panel.dataset.view;
      frame.title = panel.querySelector('h3').textContent;
      frame.referrerPolicy = 'no-referrer';
      frame.setAttribute('sandbox','allow-scripts allow-same-origin');
      if (panel.hasAttribute('data-readonly')) {
        frame.inert = true;
        frame.tabIndex = -1;
      }
      viewer.append(note, frame);
    });
  });
})();
