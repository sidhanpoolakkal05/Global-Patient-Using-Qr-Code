/**
 * MediScan – Auth Manager (JWT via localStorage)
 * Mirrors the React AuthContext logic
 */
const API_BASE = window.location.origin;

const Auth = {
  getToken()  { return localStorage.getItem('access'); },
  getUser()   { try { return JSON.parse(localStorage.getItem('ms_user') || 'null'); } catch { return null; } },

  setSession(access, user) {
    localStorage.setItem('access', access);
    localStorage.setItem('ms_user', JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem('access');
    localStorage.removeItem('ms_user');
  },

  isAuthenticated() { return !!this.getToken() && !!this.getUser(); },

  /** Fetch with auth header – returns parsed JSON or throws */
  async request(url, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    };
    const res = await fetch(API_BASE + url, { ...options, headers });
    if (res.status === 401) {
      this.clearSession();
      window.location.href = '/login/';
      return;
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw err;
    }
    const text = await res.text();
    return text ? JSON.parse(text) : null;
  },

  /** GET shorthand */
  get(url)       { return this.request(url, { method: 'GET' }); },

  /** POST shorthand */
  post(url, body){ return this.request(url, { method: 'POST', body: JSON.stringify(body) }); },

  /** PUT shorthand */
  put(url, body) { return this.request(url, { method: 'PUT',  body: JSON.stringify(body) }); },

  /** PATCH shorthand */
  patch(url, body){ return this.request(url, { method: 'PATCH', body: JSON.stringify(body) }); },

  /** DELETE shorthand */
  del(url)       { return this.request(url, { method: 'DELETE' }); },
};

/**
 * Login – called from login.html form submit
 */
async function handleLogin(e) {
  e.preventDefault();
  const form    = e.target;
  const errBox  = document.getElementById('login-error');
  const btnText = document.getElementById('login-btn-text');
  const spinner = document.getElementById('login-spinner');

  errBox.classList.remove('show');
  btnText.textContent = 'Signing In…';
  spinner.style.display = 'inline-block';

  try {
    const data = await Auth.post('/api/auth/login/', {
      username: form.username.value.trim(),
      password: form.password.value,
    });

    const profile = await Auth.request('/api/auth/profile/', {
      method: 'GET',
      headers: { Authorization: `Bearer ${data.access}` },
    });

    Auth.setSession(data.access, profile);
    redirectByRole(profile.role);
  } catch (err) {
    console.error('Login Error:', err);
    let msg = 'An unexpected error occurred. Please try again.';
    
    if (err && typeof err === 'object') {
      if (err.detail) {
        msg = err.detail;
        if (msg.includes('No active account found')) {
          msg = 'Invalid username or password.';
        }
      } else if (err.non_field_errors) {
        msg = err.non_field_errors.join(' ');
      } else {
        msg = Object.values(err).flat().join(' | ');
      }
    }
    
    errBox.textContent = msg;
    errBox.classList.add('show');
    btnText.textContent = 'Sign In';
    spinner.style.display = 'none';
  }
}

/**
 * Register – called from register.html form submit
 */
async function handleRegister(e) {
  e.preventDefault();
  const form    = e.target;
  const errBox  = document.getElementById('reg-error');
  const sucBox  = document.getElementById('reg-success');
  const btn     = document.getElementById('reg-btn');

  errBox.classList.remove('show');
  sucBox.classList.remove('show');
  btn.textContent = 'Creating Account…';
  btn.disabled    = true;

  const payload = {
    username:    form.username.value.trim(),
    email:       form.email.value.trim(),
    password:    form.password.value,
    full_name:   form.full_name.value.trim(),
    phone:       form.phone.value.trim(),
    age:         form.age.value,
    gender:      form.gender.value,
    blood_group: form.blood_group.value,
    role:        'patient',
  };

  try {
    await Auth.post('/api/auth/register/', payload);
    sucBox.textContent = 'Account created! Redirecting to login…';
    sucBox.classList.add('show');
    setTimeout(() => window.location.href = '/login/', 2000);
  } catch (err) {
    const msg = typeof err === 'object' ? Object.values(err).flat().join(' | ') : 'Registration failed.';
    errBox.textContent = msg;
    errBox.classList.add('show');
    btn.textContent = 'Create Account';
    btn.disabled    = false;
  }
}

/**
 * Logout
 */
function logout() {
  Auth.clearSession();
  window.location.href = '/login/';
}

/**
 * Role-based redirect
 */
function redirectByRole(role) {
  const map = {
    admin:          '/dashboard/admin/',
    hospital_admin: '/dashboard/hospital/',
    doctor:         '/dashboard/doctor/',
    receptionist:   '/dashboard/staff/',
    patient:        '/dashboard/patient/',
  };
  window.location.href = map[role] || '/login/';
}

/**
 * Guard: run on every protected page to check auth
 * Pass the required role(s) as an array, or empty for any authenticated user.
 */
function requireAuth(allowedRoles = []) {
  if (!Auth.isAuthenticated()) {
    window.location.href = '/login/';
    return null;
  }
  const user = Auth.getUser();
  if (allowedRoles.length && !allowedRoles.includes(user.role)) {
    redirectByRole(user.role);
    return null;
  }
  return user;
}

/**
 * Populate topbar with user info (call after DOM ready)
 */
function populateTopbar(user) {
  const nameEl   = document.getElementById('topbar-username');
  const roleEl   = document.getElementById('topbar-role');
  const avatarEl = document.getElementById('topbar-avatar');

  if (nameEl)   nameEl.textContent   = user.username;
  if (roleEl)   roleEl.textContent   = (user.hospital_name ? user.hospital_name + ' · ' : '') + user.role.replace('_', ' ') + (user.uhid ? ' · ' + user.uhid : '');
  if (avatarEl) avatarEl.textContent = user.username.charAt(0).toUpperCase();

  // Sidebar logo sub-text
  const logoSub = document.getElementById('sidebar-logo-sub');
  if (logoSub) logoSub.textContent = user.hospital_name || 'Global System';
}

/**
 * Simple toast notification
 */
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
