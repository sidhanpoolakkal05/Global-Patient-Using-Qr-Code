/**
 * MediScan – Dashboard Sidebar Logic
 * Handles collapse/expand, active link highlighting
 */
document.addEventListener('DOMContentLoaded', () => {
  const sidebar    = document.getElementById('sidebar');
  const collapseBtn = document.getElementById('sidebar-collapse-btn');
  const collapseLabel = document.getElementById('collapse-label');
  const collapseIcon  = document.getElementById('collapse-icon');
  const logoText      = document.getElementById('sidebar-logo-text');
  const sectionLabel  = document.getElementById('sidebar-section-label');
  const navLabels     = document.querySelectorAll('.nav-label');

  // ── Restore collapsed state ──
  let collapsed = localStorage.getItem('sidebar-collapsed') === 'true';
  if (collapsed && sidebar) applySidebarState(true, false);

  if (collapseBtn) {
    collapseBtn.addEventListener('click', () => {
      collapsed = !collapsed;
      localStorage.setItem('sidebar-collapsed', collapsed);
      applySidebarState(collapsed, true);
    });
  }

  function applySidebarState(isCollapsed, animate) {
    if (!sidebar) return;
    if (isCollapsed) {
      sidebar.classList.add('collapsed');
    } else {
      sidebar.classList.remove('collapsed');
    }

    // Hide text elements when collapsed
    const hideEls = [logoText, sectionLabel, collapseLabel, ...navLabels];
    hideEls.forEach(el => {
      if (!el) return;
      el.style.opacity    = isCollapsed ? '0' : '1';
      el.style.width      = isCollapsed ? '0' : '';
      el.style.overflow   = isCollapsed ? 'hidden' : '';
      el.style.transition = animate ? 'opacity 0.25s, width 0.3s' : 'none';
    });
  }

  // ── Active nav link highlighting ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    // Exact match or (starts-with for non-overview links)
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href) && href.length > 1)) {
      link.classList.add('active');
    }
  });
});
