(function () {
  'use strict';

  async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }

    const input = document.createElement('textarea');
    input.value = value;
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.appendChild(input);
    input.select();
    const copied = document.execCommand('copy');
    input.remove();
    if (!copied) throw new Error('copy failed');
  }

  function addCopyButtons() {
    document.querySelectorAll('.questions-list pre > code').forEach((code) => {
      const pre = code.parentElement;
      if (pre.parentElement.classList.contains('ozon-code-copy')) return;

      const wrapper = document.createElement('div');
      wrapper.className = 'ozon-code-copy';
      pre.before(wrapper);
      wrapper.appendChild(pre);

      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'ozon-code-copy-button';
      button.textContent = '📋 Копировать';
      button.setAttribute('aria-label', 'Скопировать код');
      wrapper.appendChild(button);

      button.addEventListener('click', async (event) => {
        event.stopPropagation();
        try {
          await copyText(code.textContent);
          button.textContent = '✓ Скопировано';
        } catch (error) {
          button.textContent = 'Не удалось скопировать';
        }
        window.setTimeout(() => { button.textContent = '📋 Копировать'; }, 2000);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addCopyButtons);
  } else {
    addCopyButtons();
  }
})();
