document.addEventListener('DOMContentLoaded', () => {
  const preElements = document.querySelectorAll('pre');
  preElements.forEach(pre => {
    const codeBlock = pre.querySelector('code');
    if (!codeBlock) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.innerHTML = 'Скопировать';

    copyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      const text = codeBlock.innerText;
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.innerHTML = 'Скопировано!';
        copyBtn.classList.add('copied');
        
        setTimeout(() => {
          copyBtn.innerHTML = 'Скопировать';
          copyBtn.classList.remove('copied');
        }, 2000);
      }).catch(err => {
        console.error('Copy failed', err);
      });
    });

    pre.appendChild(copyBtn);
  });
});
