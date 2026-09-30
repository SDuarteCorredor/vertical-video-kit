// Run inside https://www.instagram.com/<account>/reels/ AFTER waiting ~6 s and doing one real mouse-wheel scroll.
// Read-only: scrolls the page a few times, reads each reel's view count from the grid,
// returns followers/bio, the median, and the top reels as multiples of the median.
// Never call /api/v1 endpoints from the person's session (rate limits, account risk).
(async () => {
  const W = (ms) => new Promise((r) => setTimeout(r, ms));
  const num = (s) => { if (!s) return 0; s = s.replace(/,/g, ""); const m = parseFloat(s);
    return /M$/i.test(s) ? m * 1e6 : /K$/i.test(s) ? m * 1e3 : m; };
  for (let i = 0; i < 4; i++) { window.scrollBy(0, 3000); await W(2500); }
  const head = document.querySelector("header")?.innerText.replace(/\n+/g, " | ").slice(0, 260);
  const rows = {};
  document.querySelectorAll('a[href*="/reel/"]').forEach((a) => {
    const code = a.getAttribute("href").split("/reel/")[1].split("/")[0];
    const v = num(a.innerText.trim().split("\n")[0]); if (v) rows[code] = v;
  });
  const vs = Object.values(rows).sort((a, b) => a - b);
  const median = vs[Math.floor(vs.length / 2)] || 1;
  return { account: location.pathname, header: head, reels_read: vs.length, median,
    top: Object.entries(rows).sort((a, b) => b[1] - a[1]).slice(0, 8)
      .map(([c, v]) => `${c}  ${Math.round(v / 1000)}K  x${(v / median).toFixed(0)}`) };
})();
