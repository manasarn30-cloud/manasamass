/**
 * STREAMFLIX — MAIN JAVASCRIPT
 * Handles navigation, movie row scrolling, trailer modal, My List AJAX toggle,
 * password visibility, search interaction, and toast notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initUserMenu();
  initMovieRows();
  initMyListToggles();
  initTrailerModal();
  initPasswordToggles();
  initToastSystem();
});

/* ========================================================
   1. NAVBAR & SCROLL EFFECTS
   ======================================================== */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  const mobileToggle = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 40) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    }, { passive: true });
  }

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isExpanded = navLinks.classList.contains('open');
      mobileToggle.setAttribute('aria-expanded', isExpanded);
    });
  }
}

/* ========================================================
   2. USER DROPDOWN MENU
   ======================================================== */
function initUserMenu() {
  const userBtn = document.querySelector('.user-menu-btn');
  const dropdown = document.querySelector('.dropdown-menu');

  if (userBtn && dropdown) {
    userBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && !userBtn.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  }
}

/* ========================================================
   3. HORIZONTAL MOVIE ROWS SCROLLING
   ======================================================== */
function initMovieRows() {
  const rowWrappers = document.querySelectorAll('.movie-row-wrapper');

  rowWrappers.forEach((wrapper) => {
    const row = wrapper.querySelector('.movie-row');
    const leftBtn = wrapper.querySelector('.row-scroll-btn.left');
    const rightBtn = wrapper.querySelector('.row-scroll-btn.right');

    if (row && leftBtn && rightBtn) {
      const scrollAmount = () => row.clientWidth * 0.75;

      leftBtn.addEventListener('click', () => {
        row.scrollBy({ left: -scrollAmount(), behavior: 'smooth' });
      });

      rightBtn.addEventListener('click', () => {
        row.scrollBy({ left: scrollAmount(), behavior: 'smooth' });
      });
    }
  });
}

/* ========================================================
   4. AJAX MY LIST TOGGLE WITH TOAST NOTIFICATION
   ======================================================== */
function initMyListToggles() {
  document.addEventListener('click', async (e) => {
    const saveBtn = e.target.closest('.save-movie-btn, .btn-toggle-list');
    if (!saveBtn) return;

    e.preventDefault();
    e.stopPropagation();

    const movieId = saveBtn.dataset.movieId;
    if (!movieId) return;

    // Check if user is authenticated
    const isAuthenticated = document.body.dataset.authenticated === 'true';
    if (!isAuthenticated) {
      showToast('Please sign in to add movies to your personal list.', 'info');
      setTimeout(() => {
        window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
      }, 1200);
      return;
    }

    const csrfToken = getCsrfToken();
    try {
      saveBtn.disabled = true;
      const response = await fetch(`/my-list/toggle/${movieId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (data.success) {
        // Update all buttons for this movie on the page
        const allButtons = document.querySelectorAll(`[data-movie-id="${movieId}"]`);
        allButtons.forEach((btn) => {
          if (data.in_list) {
            btn.classList.add('saved');
            if (btn.classList.contains('btn-toggle-list')) {
              btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg> In My List`;
            } else {
              btn.title = "Remove from My List";
              btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
            }
          } else {
            btn.classList.remove('saved');
            if (btn.classList.contains('btn-toggle-list')) {
              btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg> Add to My List`;
            } else {
              btn.title = "Add to My List";
              btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`;
            }
          }
        });

        // Update list badge count if present
        const countBadges = document.querySelectorAll('.my-list-counter');
        countBadges.forEach(b => b.textContent = data.total_count);

        // If on My List page and removed, fade out card
        if (window.location.pathname.includes('/my-list/') && !data.in_list) {
          const card = saveBtn.closest('.movie-card');
          if (card) {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            setTimeout(() => card.remove(), 250);
          }
        }

        showToast(data.message, data.in_list ? 'success' : 'info');
      }
    } catch (err) {
      console.error("List toggle error:", err);
      showToast("Could not update My List. Please check connection.", "error");
    } finally {
      saveBtn.disabled = false;
    }
  });
}

/* ========================================================
   5. TRAILER VIDEO MODAL
   ======================================================== */
function initTrailerModal() {
  const modal = document.getElementById('trailer-modal');
  const iframe = document.getElementById('trailer-iframe');
  const closeBtn = document.getElementById('modal-close-btn');

  if (!modal || !iframe) return;

  document.addEventListener('click', (e) => {
    const playBtn = e.target.closest('[data-trailer-url]');
    if (!playBtn) return;

    e.preventDefault();
    const trailerUrl = playBtn.dataset.trailerUrl;
    if (!trailerUrl) {
      showToast("No official trailer link available for this title.", "info");
      return;
    }

    // Convert standard YouTube watch URL to embed URL
    let embedUrl = trailerUrl;
    if (trailerUrl.includes('watch?v=')) {
      const videoId = trailerUrl.split('watch?v=')[1].split('&')[0];
      embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    } else if (trailerUrl.includes('youtu.be/')) {
      const videoId = trailerUrl.split('youtu.be/')[1].split('?')[0];
      embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    }

    iframe.src = embedUrl;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  });

  const closeModal = () => {
    modal.classList.remove('active');
    iframe.src = '';
    document.body.style.overflow = '';
  };

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });
}

/* ========================================================
   6. PASSWORD SHOW/HIDE TOGGLE
   ======================================================== */
function initPasswordToggles() {
  const toggleBtns = document.querySelectorAll('.password-toggle-btn');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (!input || input.tagName !== 'INPUT') return;

      if (input.type === 'password') {
        input.type = 'text';
        btn.setAttribute('aria-label', 'Hide password');
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
      } else {
        input.type = 'password';
        btn.setAttribute('aria-label', 'Show password');
        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
      }
    });
  });
}

/* ========================================================
   7. TOAST NOTIFICATION SYSTEM
   ======================================================== */
function initToastSystem() {
  if (!document.querySelector('.toast-container')) {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
}

function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ========================================================
   UTILITIES
   ======================================================== */
function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  if (match) return match[1];
  const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return input ? input.value : '';
}
