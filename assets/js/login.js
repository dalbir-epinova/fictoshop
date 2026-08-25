(function () {
  const form = document.getElementById('login-form');
  const usernameInput = document.getElementById('login-username');
  const passwordInput = document.getElementById('login-password');
  const message = document.getElementById('login-message');
  const submitButton = document.getElementById('login-submit');
  const nextInput = document.getElementById('login-next');

  function setMessage(text, type = 'info') {
    if (!message) return;
    message.textContent = text || '';
    message.dataset.type = type;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!usernameInput || !passwordInput) return;
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
      setMessage('Please provide both username and password.', 'error');
      return;
    }
    setMessage('Signing you in…');
    const originalText = submitButton ? submitButton.textContent : '';
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Logging in…';
    }
    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data?.detail || 'Unable to log in with those credentials.');
      }
      const fallback = nextInput?.value?.trim() || '/';
      const redirect = data?.redirect || fallback || '/';
      setMessage(data?.detail || 'Login successful. Redirecting…', 'success');
      window.location.href = redirect;
    } catch (error) {
      setMessage(error.message || 'Login failed. Try again.', 'error');
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalText || 'Log in';
      }
    }
  }

  if (form) {
    form.addEventListener('submit', handleSubmit);
  }
})();
