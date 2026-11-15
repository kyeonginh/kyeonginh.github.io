(() => {
  // 기존 홈페이지의 Slides 앵커 주소도 새 페이지로 연결합니다.
  if (window.location.hash === '#seminar-slides' && document.getElementById('about')) {
    window.location.replace('slides.html#seminar-slides');
    return;
  }
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let observer;
  const targets = [...document.querySelectorAll('.section, .footer')];
  function setMotion() {
    if (observer) observer.disconnect();
    targets.forEach(item => item.classList.remove('reveal-ready', 'is-visible'));
    if (motion.matches || !('IntersectionObserver' in window)) return;
    observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.06 });
    targets.forEach(item => {
      // Content already in view stays visible; only later sections enter on scroll.
      if (item.getBoundingClientRect().top < window.innerHeight) return;
      item.classList.add('reveal-ready');
      observer.observe(item);
    });
  }
  // 트리에 없는 간선을 추가하고, 만들어진 유일한 cycle에서 다른 간선을 제거합니다.
  const exchange = document.querySelector('.tree-exchange');
  if (exchange) {
    const edges = [...exchange.querySelectorAll('.exchange-edge')];
    const endpoints = edges.map(edge => [Number(edge.dataset.from), Number(edge.dataset.to)]);
    let tree = new Set(edges.flatMap((edge, i) => edge.classList.contains('is-tree') ? [i] : []));
    const signature = selected => [...selected].sort((a, b) => a - b).join(',');
    const history = [signature(tree)];
    let timer = 0, inView = true, step = 0;
    let previousAdded = -1, previousRemoved = -1, seed = 173;
    function random() {
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      return seed / 4294967296;
    }
    function treePath(start, end) {
      const visited = new Set([start]), queue = [[start, []]];
      for (let q = 0; q < queue.length; q++) {
        const [vertex, path] = queue[q];
        if (vertex === end) return path;
        for (const index of tree) {
          const [a, b] = endpoints[index];
          const next = a === vertex ? b : b === vertex ? a : -1;
          if (next < 0 || visited.has(next)) continue;
          visited.add(next); queue.push([next, [...path, index]]);
        }
      }
      return [];
    }
    function chooseExchange() {
      const candidates = [];
      endpoints.forEach(([a, b], entering) => {
        if (tree.has(entering) || entering === previousRemoved) return;
        const path = treePath(a, b);
        for (const leaving of path) {
          if (leaving === previousAdded) continue;
          const result = new Set(tree);
          result.add(entering); result.delete(leaving);
          candidates.push({ entering, leaving, result });
        }
      });
      const fresh = candidates.filter(candidate => !history.includes(signature(candidate.result)));
      const choices = fresh.length ? fresh : candidates;
      return choices[Math.floor(random() * choices.length)];
    }
    function drawExchange() {
      exchange.dataset.step = String(step);
      edges.forEach((edge, i) => edge.classList.toggle('is-tree', tree.has(i)));
    }
    function advanceExchange() {
      timer = 0;
      const swap = chooseExchange();
      tree = swap.result; step++;
      previousAdded = swap.entering; previousRemoved = swap.leaving;
      history.push(signature(tree));
      if (history.length > 12) history.shift();
      // 추가와 제거를 동시에 반영하고 선의 농도만 부드럽게 전환합니다.
      drawExchange();
      timer = window.setTimeout(advanceExchange, 2000);
    }
    function updateExchange() {
      clearTimeout(timer); timer = 0;
      if (!motion.matches && !document.hidden && inView) {
        timer = window.setTimeout(advanceExchange, 2000);
      }
    }
    drawExchange();
    if ('IntersectionObserver' in window) {
      const exchangeObserver = new IntersectionObserver(entries => {
        inView = entries[0].isIntersecting; updateExchange();
      });
      exchangeObserver.observe(exchange);
    }
    document.addEventListener('visibilitychange', updateExchange);
    motion.addEventListener?.('change', updateExchange);
    updateExchange();
  }
  setMotion();
  motion.addEventListener?.('change', setMotion);
})();
