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
    const svg = exchange.querySelector('svg');
    const nodes = [...exchange.querySelectorAll('.exchange-node')];
    const halos = [...exchange.querySelectorAll('.exchange-node-halo')];
    const anchors = nodes.map(node => [Number(node.getAttribute('cx')), Number(node.getAttribute('cy'))]);
    const smallScreen = window.matchMedia('(max-width: 640px)');
    const originalAnchors = anchors.map(point => [...point]);
    const returning = new Map();
    let drag = null;
    const signature = selected => [...selected].sort((a, b) => a - b).join(',');
    const history = [signature(tree)];
    let frame = 0, inView = true, step = 0;
    let elapsed = 0, lastTime = 0, lastDraw = -Infinity, nextExchange = 1500, activeSwap = null;
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
    // 기본 그래프와 강조 간선을 분리해, 새 간선만 실선으로 그립니다.
    const activeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const activeEdges = edges.map(() => {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('class', 'exchange-active-edge');
      activeGroup.appendChild(line);
      return line;
    });
    svg.insertBefore(activeGroup, nodes[0]);
    exchange.classList.add('is-animated');
    exchange.dataset.step = '0';
    // 넓은 투명 영역으로 정점을 잡되, 나머지 그래프에서는 터치 스크롤을 허용합니다.
    const hitGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const hitTargets = nodes.map((node, index) => {
      const hit = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      hit.setAttribute('class', 'exchange-node-hit');
      hit.setAttribute('data-vertex', String(index));
      hit.setAttribute('tabindex', '0');
      hit.setAttribute('role', 'button');
      hit.setAttribute('aria-label', `Vertex ${index + 1}. Arrow keys move; Enter resets.`);
      hitGroup.appendChild(hit);
      return hit;
    });
    svg.appendChild(hitGroup);
    exchange.removeAttribute('role');
    svg.removeAttribute('aria-hidden');
    svg.setAttribute('role', 'group');
    svg.setAttribute('aria-label', 'Interactive graph. Drag vertices or move them with the arrow keys.');
    function sizeTargets() {
      hitTargets.forEach(hit => hit.setAttribute('r', smallScreen.matches ? '24' : '12'));
    }
    sizeTargets();
    function offsetFor(index) {
      if (motion.matches) return [0, 0];
      const time = elapsed / 1000, amplitude = smallScreen.matches ? .65 : 1;
      const phase = index * 2.399, speed = .48 + (index % 4) * .07;
      return [
        (2.4 + (index % 3) * .6) * amplitude * (Math.sin(time * speed + phase) - Math.sin(phase)),
        (2 + (index % 2) * .8) * amplitude * (Math.cos(time * .54 + phase) - Math.cos(phase)),
      ];
    }
    function bounded(point) {
      return [Math.max(18, Math.min(382, point[0])), Math.max(18, Math.min(202, point[1]))];
    }
    function pointerPosition(event) {
      const matrix = svg.getScreenCTM();
      if (!matrix) return null;
      const point = svg.createSVGPoint();
      point.x = event.clientX; point.y = event.clientY;
      const local = point.matrixTransform(matrix.inverse());
      return [local.x, local.y];
    }
    function requestDraw() {
      // Reduced-motion 설정에서는 입력이 있을 때만 한 프레임을 그립니다.
      if (!frame) frame = requestAnimationFrame(() => { frame = 0; drawScene(); });
    }
    function scheduleReturn(index) {
      returning.delete(index);
      const distance = Math.hypot(...anchors[index].map((value, axis) => value - originalAnchors[index][axis]));
      if (distance <= 40) return;
      if (motion.matches) anchors[index] = [...originalAnchors[index]];
      else returning.set(index, { from: [...anchors[index]], started: elapsed + 600 });
    }
    function updateReturns() {
      for (const [index, returningVertex] of returning) {
        const progress = Math.max(0, Math.min(1, (elapsed - returningVertex.started) / 4200));
        const eased = progress * progress * (3 - 2 * progress);
        anchors[index] = returningVertex.from.map((value, axis) => value + (originalAnchors[index][axis] - value) * eased);
        if (progress === 1) returning.delete(index);
      }
    }
    function finishDrag(event) {
      if (!drag || (event?.pointerId != null && event.pointerId !== drag.id)) return;
      const { index, id, target, point } = drag, offset = offsetFor(index);
      anchors[index] = point.map((value, axis) => value - offset[axis]);
      drag = null;
      scheduleReturn(index);
      target.classList.remove('is-dragging');
      if (target.hasPointerCapture(id)) target.releasePointerCapture(id);
      requestDraw();
    }
    hitGroup.addEventListener('pointerdown', event => {
      const target = event.target.closest('.exchange-node-hit');
      if (!target || drag || event.button !== 0 || event.isPrimary === false) return;
      const index = Number(target.dataset.vertex), pointer = pointerPosition(event);
      if (!pointer) return;
      returning.delete(index);
      const point = [Number(nodes[index].getAttribute('cx')), Number(nodes[index].getAttribute('cy'))];
      drag = { index, id: event.pointerId, target, point, offset: pointer.map((value, axis) => value - point[axis]) };
      target.setPointerCapture(event.pointerId);
      target.classList.add('is-dragging');
      event.preventDefault();
    });
    hitGroup.addEventListener('pointermove', event => {
      if (!drag || event.pointerId !== drag.id) return;
      const pointer = pointerPosition(event);
      if (!pointer) return;
      drag.point = bounded(pointer.map((value, axis) => value - drag.offset[axis]));
      event.preventDefault();
      requestDraw();
    });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(type => hitGroup.addEventListener(type, finishDrag));
    hitGroup.addEventListener('keydown', event => {
      if (drag) return;
      const target = event.target.closest('.exchange-node-hit');
      if (!target) return;
      const index = Number(target.dataset.vertex), offset = offsetFor(index);
      const delta = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key];
      if (delta) {
        const point = bounded(anchors[index].map((value, axis) => value + offset[axis] + delta[axis] * (event.shiftKey ? 10 : 4)));
        anchors[index] = point.map((value, axis) => value - offset[axis]);
      } else if (['Enter', ' ', 'Home'].includes(event.key)) anchors[index] = [...originalAnchors[index]];
      else return;
      scheduleReturn(index);
      event.preventDefault();
      nextExchange = elapsed + 1500;
      requestDraw();
    });
    window.addEventListener('blur', () => finishDrag());
    smallScreen.addEventListener?.('change', () => { sizeTargets(); updateExchange(); });
    function advanceExchange() {
      const swap = chooseExchange();
      tree = swap.result; step++;
      previousAdded = swap.entering; previousRemoved = swap.leaving;
      history.push(signature(tree));
      if (history.length > 12) history.shift();
      edges.forEach((edge, i) => edge.classList.toggle('is-tree', tree.has(i)));
      exchange.dataset.step = String(step);
      activeSwap = { ...swap, started: elapsed };
      nextExchange = elapsed + 1500;
    }
    function setLine(line, a, b) {
      line.setAttribute('x1', a[0].toFixed(2)); line.setAttribute('y1', a[1].toFixed(2));
      line.setAttribute('x2', b[0].toFixed(2)); line.setAttribute('y2', b[1].toFixed(2));
    }
    function drawScene() {
      updateReturns();
      const moving = !motion.matches;
      const raw = activeSwap ? Math.min(1, (elapsed - activeSwap.started) / 420) : 1;
      const progress = raw * raw * (3 - 2 * raw);
      const pulse = activeSwap && moving ? Math.sin(Math.PI * raw) ** 2 : 0;
      const ends = activeSwap ? endpoints[activeSwap.entering] : [];
      const points = anchors.map(([x, y], i) => {
        const offset = offsetFor(i);
        const point = drag?.index === i ? drag.point : [x + offset[0], y + offset[1]];
        nodes[i].setAttribute('cx', point[0].toFixed(2));
        nodes[i].setAttribute('cy', point[1].toFixed(2));
        halos[i].setAttribute('cx', point[0].toFixed(2));
        halos[i].setAttribute('cy', point[1].toFixed(2));
        hitTargets[i].setAttribute('cx', point[0].toFixed(2));
        hitTargets[i].setAttribute('cy', point[1].toFixed(2));
        nodes[i].setAttribute('r', (2.8 + (ends.includes(i) ? .55 * pulse : 0)).toFixed(2));
        return point;
      });
      edges.forEach((edge, i) => {
        const [from, to] = endpoints[i], a = points[from], b = points[to];
        setLine(edge, a, b);
        let end = b, opacity = tree.has(i) ? .72 : 0;
        if (activeSwap && i === activeSwap.entering) {
          end = [a[0] + (b[0] - a[0]) * progress, a[1] + (b[1] - a[1]) * progress];
        }
        if (activeSwap && i === activeSwap.leaving) opacity = .72 * (1 - progress);
        setLine(activeEdges[i], a, end);
        activeEdges[i].setAttribute('opacity', opacity.toFixed(3));
      });
      if (raw === 1) activeSwap = null;
    }
    function tick(time) {
      if (lastTime) elapsed += Math.min(time - lastTime, 100);
      lastTime = time;
      if (elapsed >= nextExchange) advanceExchange();
      if (time - lastDraw >= 1000 / 30) { drawScene(); lastDraw = time; }
      frame = requestAnimationFrame(tick);
    }
    function updateExchange() {
      cancelAnimationFrame(frame); frame = 0; lastTime = 0; lastDraw = -Infinity;
      if (motion.matches) {
        for (const index of returning.keys()) anchors[index] = [...originalAnchors[index]];
        returning.clear();
        activeSwap = null;
        drawScene();
      }
      else if (!document.hidden && inView) frame = requestAnimationFrame(tick);
    }
    drawScene();
    if ('IntersectionObserver' in window) {
      const exchangeObserver = new IntersectionObserver(entries => {
        inView = entries[0].isIntersecting; updateExchange();
      });
      exchangeObserver.observe(exchange);
    }
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) finishDrag();
      updateExchange();
    });
    motion.addEventListener?.('change', updateExchange);
    updateExchange();
  }
  setMotion();
  motion.addEventListener?.('change', setMotion);
})();
