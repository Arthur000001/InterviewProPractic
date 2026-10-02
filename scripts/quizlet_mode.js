document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-quizlet-btn');
  const startKeyBtn = document.getElementById('start-key-quizlet-btn');
  const modalRoot = document.getElementById('quizlet-modal-root');
  
  if (!modalRoot) return;

  let questions = [];
  let queue = [];
  let results = {}; // key: question id, value: { text, attempts, status }
  let globalFlags = {}; // Key: "qIndex", Value: boolean
  let currentQuestion = null;
  let currentOnlyKey = false;
  let groupedMode = false;

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));
  }

  function parseQuestions(onlyKey = false) {
    const parsed = [];
    let index = 0;

    if (groupedMode) {
      document.querySelectorAll('.questions-list > details').forEach((main) => {
        if (main.style.display === 'none') return;
        const isKey = main.classList.contains('key-question');
        if (onlyKey && !isKey) return;
        const summary = main.querySelector(':scope > summary.question-summary');
        const answer = main.querySelector(':scope > .answer-box');
        const title = summary?.querySelector('.question-text')?.textContent.trim();
        if (!title || !answer) return;

        const answerCopy = answer.cloneNode(true);
        answerCopy.querySelector('.theory-followups')?.remove();
        const steps = [{ text: title, answerHtml: answerCopy.outerHTML }];
        if (!onlyKey) {
          main.querySelectorAll(':scope > .answer-box > .theory-followups > details.secondary-question').forEach((followup) => {
            const followupTitle = followup.querySelector(':scope > summary .question-text')?.textContent.trim();
            const followupAnswer = followup.querySelector(':scope > .answer-box');
            if (followupTitle && followupAnswer) {
              steps.push({ text: followupTitle, answerHtml: followupAnswer.outerHTML });
            }
          });
        }
        parsed.push({ id: index++, text: title, steps, stepIndex: 0, isKey });
      });
      return parsed;
    }
    
    // First, try the new structure (after build_html_site.js DOM manipulation)
    const detailsElements = document.querySelectorAll('details');
    detailsElements.forEach((details) => {
      if (details.closest('.sidebar')) {
        return;
      }
      if (details.style.display === 'none') {
        return;
      }
      if (onlyKey && !details.classList.contains('key-question')) {
        return;
      }
      const summary = details.querySelector('summary.question-summary');
      if (summary) {
        const span = summary.querySelector('span.question-text');
        if (span) {
          const text = span.textContent.trim();
          let htmlContent = details.innerHTML;
          htmlContent = htmlContent.replace(summary.outerHTML, '');
          parsed.push({
            id: index++,
            text: text,
            answerHtml: htmlContent
          });
        }
      }
    });
    
    // Fallback: If no questions found via new structure, try the old structure
    if (parsed.length === 0) {
      const items = document.querySelectorAll('.checklist-item');
      items.forEach((item) => {
        const span = item.querySelector('span');
        const text = span ? span.textContent.trim() : item.textContent.trim();
        let answerHtml = '';
        
        let next = item.nextElementSibling;
        if (next && next.tagName === 'DETAILS') {
          const summary = next.querySelector('summary');
          let htmlContent = next.innerHTML;
          if (summary) {
            htmlContent = htmlContent.replace(summary.outerHTML, '');
          }
          answerHtml = htmlContent;
        }
        
        parsed.push({
          id: index++,
          text: text,
          answerHtml: answerHtml
        });
      });
    }
    
    return parsed;
  }

  function shuffle(array) {
    let currentIndex = array.length, randomIndex;
    while (currentIndex !== 0) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;
      [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }
    return array;
  }

  function renderCard() {
    if (queue.length === 0) {
      renderResults();
      return;
    }

    currentQuestion = queue[0];
    const step = groupedMode ? currentQuestion.steps[currentQuestion.stepIndex] : currentQuestion;
    const progress = groupedMode && currentQuestion.steps.length > 1
      ? (currentQuestion.stepIndex === 0
        ? `${currentQuestion.isKey ? 'Основной вопрос' : 'Вопрос'} · затем ${currentQuestion.steps.length - 1} уточнений`
        : `Уточнение ${currentQuestion.stepIndex} из ${currentQuestion.steps.length - 1}`)
      : '';
    const historyHtml = groupedMode
      ? currentQuestion.steps.slice(0, currentQuestion.stepIndex).map((previous, index) => `
          <section class="quizlet-thread-step quizlet-thread-done">
            <div class="q-counter">${index === 0 ? (currentQuestion.isKey ? 'Основной вопрос' : 'Вопрос') : `Уточнение ${index} из ${currentQuestion.steps.length - 1}`}</div>
            <h3 class="quizlet-question">${escapeHtml(previous.text)}</h3>
            <div class="quizlet-answer">${previous.answerHtml}</div>
          </section>
        `).join('')
      : '';
    
    // Initialize results tracker
    if (!results[currentQuestion.id]) {
      results[currentQuestion.id] = { text: currentQuestion.text, attempts: 0, status: 'В процессе' };
    }

    modalRoot.innerHTML = `
      <div class="interview-overlay">
        <div class="interview-main-container quizlet-container">
          <div class="interview-header">
            <h2>🧠 Квизлет (Осталось ${groupedMode ? (currentOnlyKey ? 'основных вопросов' : 'вопросов') : 'карточек'}: ${queue.length})</h2>
            <button class="interview-close-btn" id="close-quizlet-btn">✕ Выход</button>
          </div>
          
          <div class="interview-content quizlet-content">
            <div class="quizlet-card ${groupedMode ? 'quizlet-chain-card' : ''}">
              ${groupedMode ? '<div id="quizlet-thread" class="quizlet-thread">' : ''}
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div class="q-counter" style="color: var(--text-secondary);">Осталось ${groupedMode ? (currentOnlyKey ? 'основных вопросов' : 'вопросов') : 'карточек'}: ${queue.length}</div>
                <label style="display: inline-flex; align-items: center; gap: 8px; color: var(--text-secondary); cursor: pointer; font-size: 0.95rem;">
                  <input type="checkbox" id="quizlet-flag-checkbox" ${globalFlags[currentQuestion.id] ? 'checked' : ''}>
                  ⚠️ Доработать
                </label>
              </div>
              ${historyHtml}
              ${groupedMode ? '<section id="quizlet-current-step" class="quizlet-thread-step quizlet-thread-active">' : ''}
              ${progress ? `<div class="q-counter" style="text-align: center; margin-bottom: 10px;">${progress}</div>` : ''}
              <h3 class="quizlet-question">${escapeHtml(step.text)}</h3>
              
              <div id="quizlet-answer-box" class="quizlet-answer hidden">
                ${step.answerHtml}
              </div>
              
              <div class="quizlet-actions" style="margin-top: 30px;">
                <button id="quizlet-show-btn" class="hero-btn hero-btn-primary" style="width: 100%; padding: 16px; font-size: 1.2rem; justify-content: center;">👀 Показать ответ</button>
                
                <div id="quizlet-rate-buttons" class="hidden" style="display: flex; gap: 10px; width: 100%;">
                  <button id="rate-know" class="quizlet-rate-btn know">✅ Знаю</button>
                  <button id="rate-unsure" class="quizlet-rate-btn unsure">🤔 Сомневаюсь</button>
                  <button id="rate-dknow" class="quizlet-rate-btn dknow">❌ Не знаю</button>
                </div>
              </div>
              ${groupedMode ? '</section></div>' : ''}
            </div>
          </div>
        </div>
      </div>
    `;

    function scrollToCurrentStep() {
      if (!groupedMode) return;
      const thread = document.getElementById('quizlet-thread');
      if (thread) thread.scrollTop = thread.scrollHeight;
    }
    scrollToCurrentStep();

    document.getElementById('close-quizlet-btn').addEventListener('click', closeQuizlet);
    
    const showBtn = document.getElementById('quizlet-show-btn');
    const answerBox = document.getElementById('quizlet-answer-box');
    const rateButtons = document.getElementById('quizlet-rate-buttons');
    
    if (showBtn) {
      showBtn.addEventListener('click', () => {
        showBtn.style.display = 'none';
        answerBox.classList.remove('hidden');
        rateButtons.classList.remove('hidden');
        scrollToCurrentStep();
      });
    }

    const flagCheckbox = document.getElementById('quizlet-flag-checkbox');
    if (flagCheckbox) {
      flagCheckbox.addEventListener('change', (e) => {
        globalFlags[currentQuestion.id] = e.target.checked;
      });
    }

    document.getElementById('rate-know').addEventListener('click', () => handleRate('know'));
    document.getElementById('rate-unsure').addEventListener('click', () => handleRate('unsure'));
    document.getElementById('rate-dknow').addEventListener('click', () => handleRate('dknow'));
  }

  function handleRate(rating) {
    const q = queue.shift();
    const result = results[q.id];
    result.attempts++;
    
    if (rating === 'know') {
      if (groupedMode && q.stepIndex < q.steps.length - 1) {
        q.stepIndex++;
        result.status = `В процессе (${q.stepIndex}/${q.steps.length})`;
        queue.unshift(q);
      } else {
        result.status = 'Выучено';
      }
    } else if (rating === 'unsure') {
      // Put back 5 spots later (or at the end)
      const insertIndex = Math.min(queue.length, 5);
      queue.splice(insertIndex, 0, q);
    } else if (rating === 'dknow') {
      // Put back 10 spots later (or at the end)
      const insertIndex = Math.min(queue.length, 10);
      queue.splice(insertIndex, 0, q);
    }
    
    renderCard();
  }

  function renderResults() {
    let tbody = '';
    
    questions.forEach(q => {
      const res = results[q.id];
      if (!res) return;
      
      let statusColor = 'var(--text-secondary)';
      let textDecoration = 'none';
      if (res.status === 'Выучено') {
        if (res.attempts === 1) statusColor = 'var(--accent-success)';
        else if (res.attempts > 1 && res.attempts <= 3) statusColor = '#eab308';
        else statusColor = 'var(--accent-error)';
        textDecoration = 'line-through';
      }

      let flagHtml = globalFlags[q.id] ? '<span style="color: var(--accent-warning);">Да</span>' : '';

      tbody += `
        <tr>
          <td><div class="truncate-text" title="${res.text}" style="text-decoration: ${textDecoration}">${res.text}</div></td>
          <td style="text-align: center;">${flagHtml}</td>
          <td style="text-align: center;">${res.attempts}</td>
          <td style="text-align: center; color: ${statusColor}; font-weight: 500;">${res.status}</td>
        </tr>
      `;
    });

    modalRoot.innerHTML = `
      <div class="interview-overlay">
        <div class="interview-main-container quizlet-container" style="max-width: 900px;">
          <div class="interview-header">
            <h2>🏆 Результаты Квизлета</h2>
            <button class="interview-close-btn" id="close-quizlet-btn">✕ Закрыть</button>
          </div>
          
          <div class="interview-content" style="flex-direction: column; display: flex;">
            <div class="table-container" style="max-height: 60vh; overflow-y: auto;">
              <table class="interview-table">
                <thead>
                  <tr>
                    <th>Вопрос</th>
                    <th style="width: 100px; text-align: center;">Доработать</th>
                    <th style="width: 100px; text-align: center;">Попыток</th>
                    <th style="width: 120px; text-align: center;">Статус</th>
                  </tr>
                </thead>
                <tbody>
                  ${tbody}
                </tbody>
              </table>
            </div>
            
            <div style="margin-top: 24px; text-align: center; display: flex; flex-direction: row; gap: 16px; justify-content: center;">
              <button id="restart-quizlet-btn" class="hero-btn hero-btn-primary" style="padding: 12px 24px;">🔄 Начать заново</button>
              <button id="export-quizlet-csv-btn" class="hero-btn hero-btn-success" style="padding: 12px 24px;">📥 Выгрузить CSV</button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.getElementById('close-quizlet-btn').addEventListener('click', closeQuizlet);
    document.getElementById('restart-quizlet-btn').addEventListener('click', () => startQuizlet(currentOnlyKey));
    document.getElementById('export-quizlet-csv-btn').addEventListener('click', exportCSV);
  }

  function exportCSV() {
    let csvContent = "Вопрос;Доработать;Попыток;Статус\n";
    questions.forEach(q => {
      const res = results[q.id];
      if (!res) return;
      let safeText = '"' + res.text.replace(/"/g, '""') + '"';
      let flag = globalFlags[q.id] ? '⚠️' : '☑️';
      csvContent += `${safeText};${flag};${res.attempts};${res.status}\n`;
    });
    const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'quizlet_results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function closeQuizlet() {
    modalRoot.innerHTML = '';
    document.body.style.overflow = 'auto'; // Restore scroll
  }

  function startQuizlet(onlyKey = false) {
    document.body.style.overflow = 'hidden'; // Prevent body scroll
    currentOnlyKey = onlyKey;
    groupedMode = Boolean(document.querySelector('.questions-list .theory-followups'));
    questions = parseQuestions(onlyKey);
    
    if (questions.length === 0) {
      alert(onlyKey ? 'На этой странице нет ключевых вопросов.' : 'На этой странице не найдено вопросов.');
      document.body.style.overflow = 'auto';
      return;
    }

    queue = shuffle([...questions]);
    results = {};
    globalFlags = {};
    renderCard();
  }

  if (startBtn) {
    startBtn.addEventListener('click', () => startQuizlet(false));
  }
  if (startKeyBtn) {
    startKeyBtn.addEventListener('click', () => startQuizlet(true));
  }
});
