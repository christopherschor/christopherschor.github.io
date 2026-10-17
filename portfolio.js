// portfolio.json is the fixed vocabulary and project catalog.
(async () => {
  const section = document.querySelector('.selected');
  if (!section) return;
  const cloud = section.querySelector('.tag-cloud');
  const status = section.querySelector('.collection-status');
  const heading = section.querySelector('h2');
  try {
    const response = await fetch('portfolio.json');
    if (!response.ok) throw new Error('Catalog unavailable');
    const catalog = await response.json();
    const vocabulary = new Set(catalog.tags);
    if (vocabulary.size !== catalog.tags.length || vocabulary.size > catalog.tagLimit || catalog.tagLimit > 20) throw new Error('Invalid tag vocabulary');
    const projects = catalog.projects.map(project => {
      const card = document.getElementById(project.id);
      if (!card || !card.classList.contains('project') || !project.tags.every(tag => vocabulary.has(tag))) throw new Error('Invalid project tags');
      return {...project, card};
    }).sort((a, b) => b.addedOrder - a.addedOrder);
    if (new Set(projects.map(p => p.id)).size !== projects.length || section.querySelectorAll('.project').length !== projects.length) throw new Error('Project catalog does not match page');
    projects.forEach(project => section.append(project.card));
    const used = new Set(projects.flatMap(p => p.tags));
    for (const tag of catalog.tags.filter(tag => used.has(tag))) {
      const link = document.createElement('a');
      link.href = '#tag=' + encodeURIComponent(tag);
      link.dataset.tag = tag;
      link.textContent = '#' + tag;
      const count = projects.filter(p => p.tags.includes(tag)).length;
      link.className = count >= 4 ? 'tag-large' : count >= 2 ? 'tag-medium' : 'tag-small';
      link.setAttribute('aria-label', '#' + tag + ', ' + count + (count === 1 ? ' project' : ' projects'));
      cloud.append(link);
    }
    function applyCollection() {
      const match = location.hash.match(/^#tag=(.*)$/);
      let tag = null;
      try { tag = match ? decodeURIComponent(match[1]) : null; } catch (_) {}
      const valid = tag && used.has(tag);
      let visible = 0;
      for (const project of projects) {
        const show = !valid || project.tags.includes(tag);
        project.card.hidden = !show;
        if (show) visible++;
        else project.card.querySelectorAll('audio').forEach(player => player.pause());
      }
      cloud.querySelectorAll('a').forEach(link => {
        const active = link.dataset.tag === (valid ? tag : 'all');
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
      heading.textContent = valid ? '#' + tag : 'Selected work';
      status.textContent = (tag && !valid ? 'Unknown tag — showing all work. ' : '') + visible + (visible === 1 ? ' project' : ' projects') + ' · Newest first';
    }
    window.addEventListener('hashchange', applyCollection);
    applyCollection();
    cloud.addEventListener('click', event => {
      if (event.target.closest('a')) section.scrollIntoView({block: 'start'});
    });
  } catch (error) {
    // Every project remains readable if the catalog cannot load.
    status.textContent = 'All projects · Newest first';
    console.warn('Portfolio collections:', error.message);
  }
})();
