(function () {
  const picker = document.querySelector('.star-picker');
  if (!picker) return;

  const buttons = Array.from(picker.querySelectorAll('.star-picker-button'));
  const hiddenInput = document.getElementById('review-rating-value');
  const selectedLabel = document.getElementById('star-picker-selected');
  const max = Number(picker.dataset.max) || 5;
  let current = Number(picker.dataset.currentRating || 0);

  function formatLabel(value) {
    if (!selectedLabel) return;
    if (value > 0) {
      selectedLabel.textContent = `${value.toFixed(1)}/${max}`;
    } else {
      selectedLabel.textContent = selectedLabel.dataset.default || 'Tap a star';
    }
  }

  function updateDisplay() {
    buttons.forEach((button) => {
      const index = Number(button.dataset.index);
      const fill = Math.min(Math.max(current - (index - 1), 0), 1);
      button.style.setProperty('--fill-level', fill);
      button.setAttribute('aria-checked', fill >= 1 ? 'true' : 'false');
    });
  }

  function setRating(value) {
    current = Math.min(Math.max(value, 0), max);
    if (hiddenInput) hiddenInput.value = current > 0 ? current.toFixed(1) : '';
    formatLabel(current);
    updateDisplay();
  }

  function calculateValue(button, event) {
    const index = Number(button.dataset.index);
    const rect = button.getBoundingClientRect();
    const relative = (event.clientX - rect.left) / rect.width;
    const clamped = Math.min(Math.max(relative, 0), 1);
    const fraction = clamped <= 0.5 ? 0.5 : 1;
    return Math.min(index - 1 + fraction, max);
  }

  buttons.forEach((button) => {
    button.setAttribute('role', 'radio');
    button.setAttribute('tabindex', '0');

    button.addEventListener('click', (event) => {
      const value = calculateValue(button, event);
      setRating(value);
    });

    button.addEventListener('keydown', (event) => {
      switch (event.key) {
        case 'ArrowRight':
        case 'ArrowUp':
          event.preventDefault();
          setRating(Math.min(current + 0.5, max));
          break;
        case 'ArrowLeft':
        case 'ArrowDown':
          event.preventDefault();
          setRating(Math.max(current - 0.5, 0.5));
          break;
        case 'Home':
          event.preventDefault();
          setRating(0.5);
          break;
        case 'End':
          event.preventDefault();
          setRating(max);
          break;
        default:
          break;
      }
    });
  });

  updateDisplay();
  if (current > 0) {
    setRating(current);
  } else {
    formatLabel(0);
  }
})();
