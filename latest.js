(() => {
  'use strict';
  const input = document.getElementById('journal-search');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('.j-card')];
  const fa = document.documentElement.lang === 'fa';
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase(fa ? 'fa' : 'tr').replace(/ي/g, 'ی').replace(/ك/g, 'ک').replace(/\u200c/g, ' ');
  if (input) {
    const params = new URLSearchParams(location.search);
    let category = ['all','dentistry','medicine','health'].includes(params.get('category')) ? params.get('category') : 'all';
    input.value = params.get('q') || '';
    function filter(updateUrl = true) {
      const q = normalize(input.value.trim());
      let count = 0;
      for (const card of cards) {
        card.hidden = !(category === 'all' || card.dataset.category === category) || !normalize(card.dataset.search).includes(q);
        if (!card.hidden) count++;
      }
      buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === category)));
      document.getElementById('journal-count').textContent = `${count.toLocaleString(fa ? 'fa' : 'tr')} ${fa ? 'مطلب' : 'yazı'}`;
      document.getElementById('journal-empty').hidden = count > 0;
      if (updateUrl) {
        const u = new URL(location.href);
        category === 'all' ? u.searchParams.delete('category') : u.searchParams.set('category', category);
        q ? u.searchParams.set('q', input.value.trim()) : u.searchParams.delete('q');
        history.replaceState(null, '', u);
      }
    }
    buttons.forEach(b => b.addEventListener('click', () => { category = b.dataset.filter; filter(); }));
    input.addEventListener('input', () => filter());
    filter(false);
  }
  const copy = document.getElementById('copy-link');
  if (copy) copy.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(document.querySelector('link[rel=canonical]').href); document.getElementById('copy-status').textContent = copy.dataset.done; }
    catch { document.getElementById('copy-status').textContent = copy.dataset.failed; }
  });
})();
