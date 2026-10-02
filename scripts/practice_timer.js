document.addEventListener('DOMContentLoaded', () => {
  const time = document.getElementById('practice-timer-time');
  const task = document.getElementById('practice-timer-task');
  const pause = document.getElementById('practice-timer-pause');
  const resume = document.getElementById('practice-timer-resume');
  const stop = document.getElementById('practice-timer-stop');
  if (!time || !task || !pause || !resume || !stop) return;

  let interval = null;
  let remaining = 0;
  let deadline = 0;

  function format(ms) {
    const seconds = Math.max(0, Math.ceil(ms / 1000));
    return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  }

  function controls(state) {
    pause.disabled = state !== 'running';
    resume.disabled = state !== 'paused';
    stop.disabled = state === 'idle';
  }

  function tick() {
    remaining = Math.max(0, deadline - Date.now());
    time.textContent = format(remaining);
    if (remaining === 0) {
      clearInterval(interval);
      interval = null;
      task.textContent += ' — время вышло';
      controls('idle');
    }
  }

  function start(minutes, label, fallback) {
    clearInterval(interval);
    remaining = minutes * 60 * 1000;
    deadline = Date.now() + remaining;
    task.textContent = `${label}${fallback ? ' · 5 мин по умолчанию' : ''}`;
    time.textContent = format(remaining);
    controls('running');
    interval = setInterval(tick, 250);
  }

  document.querySelectorAll('.questions-list .playground-btn').forEach(link => {
    link.addEventListener('click', () => {
      const card = link.closest('details');
      const badge = card?.querySelector('.answer-meta .badge')?.textContent || '';
      const match = badge.match(/⏱️\s*(\d+)\s*мин/);
      const label = card?.querySelector('.question-text strong')?.textContent || 'Задача';
      start(match ? Number(match[1]) : 5, label, !match);
    });
  });

  pause.addEventListener('click', () => {
    remaining = Math.max(0, deadline - Date.now());
    clearInterval(interval);
    interval = null;
    time.textContent = format(remaining);
    controls('paused');
  });

  resume.addEventListener('click', () => {
    deadline = Date.now() + remaining;
    controls('running');
    interval = setInterval(tick, 250);
  });

  stop.addEventListener('click', () => {
    clearInterval(interval);
    interval = null;
    remaining = 0;
    deadline = 0;
    time.textContent = '00:00';
    task.textContent = 'Таймер остановлен';
    controls('idle');
  });
});
