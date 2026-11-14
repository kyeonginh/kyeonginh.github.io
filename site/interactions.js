(() => {
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
  setMotion();
  motion.addEventListener?.('change', setMotion);
})();
