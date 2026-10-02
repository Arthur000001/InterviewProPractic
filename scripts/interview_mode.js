document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-interview-btn');
  const modalRoot = document.getElementById('interview-modal-root');
  
  if (!startBtn || !modalRoot) return;

  // State
  let participants = [];
  let questions = [];
  let currentQuestionIndex = 0;
  let randomOrder = [];
  let globalScores = {}; // Key: "qIndex-pIndex", Value: "✅" | "❌" | "⚠️" | "🔲"
  let globalFlags = {}; // Key: "qIndex", Value: boolean
  let timerInterval = null;
  let timeLeft = 0;
  let groupedMode = false;

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }

  // Parse all questions from DOM
  function parseQuestions() {
    const parsed = [];
    let index = 0;

    if (groupedMode) {
      document.querySelectorAll('.questions-list > details').forEach((main) => {
        if (main.style.display === 'none') return;
        const summary = main.querySelector(':scope > summary.question-summary');
        const title = summary?.querySelector('.question-text')?.textContent.trim();
        const answer = main.querySelector(':scope > .answer-box');
        if (!title || !answer) return;

        const answerCopy = answer.cloneNode(true);
        answerCopy.querySelector('.theory-followups')?.remove();
        const followups = [];
        main.querySelectorAll(':scope > .answer-box > .theory-followups > details.secondary-question').forEach((followup) => {
          const text = followup.querySelector(':scope > summary .question-text')?.textContent.trim();
          const detailAnswer = followup.querySelector(':scope > .answer-box');
          if (text && detailAnswer) followups.push({ text, answerHtml: detailAnswer.outerHTML });
        });
        const badge = answer.querySelector('.answer-meta .badge');
        const minutesMatch = badge?.textContent.match(/⏱️\s*(\d+)\s*мин/);
        parsed.push({
          id: index++, text: title, answerHtml: answerCopy.outerHTML,
          followups, minutes: minutesMatch ? Number(minutesMatch[1]) : 5
        });
      });
      return parsed;
    }
    
    // First, try the new structure (after build_html_site.js DOM manipulation)
    const detailsElements = document.querySelectorAll('details');
    detailsElements.forEach((details) => {
      const summary = details.querySelector('summary.question-summary');
      if (summary) {
        const span = summary.querySelector('span.question-text');
        if (span) {
          const text = span.textContent.trim();
          let htmlContent = details.innerHTML;
          htmlContent = htmlContent.replace(summary.outerHTML, '');
          const badge = details.querySelector('.answer-meta .badge');
          const minutesMatch = badge?.textContent.match(/⏱️\s*(\d+)\s*мин/);
          parsed.push({
            id: index++,
            text: text,
            answerHtml: htmlContent,
            minutes: minutesMatch ? Number(minutesMatch[1]) : 5
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

  // Shuffle array (Fisher-Yates)
  function shuffle(array) {
    let currentIndex = array.length, randomIndex;
    while (currentIndex !== 0) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;
      [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }
    return array;
  }

  // Render Setup View
  function renderSetup() {
    modalRoot.innerHTML = `
      <div class="interview-overlay">
        <div class="interview-setup-box">
          <button class="interview-close-btn" id="close-interview-btn">✕</button>
          <h2 style="margin-top:0;">Настройка Собеседования</h2>
          <p style="color: var(--text-secondary); margin-bottom: 20px;">Введите имена участников через запятую:</p>
          <input type="text" id="participants-input" class="interview-input" placeholder="Иван, Анна, Алексей" />
          
          <p style="color: var(--text-secondary); margin-top: 20px;">${document.querySelector('.questions-list .theory-followups') ? 'Время на вопрос и все его уточнения берётся из карточки вопроса.' : 'Время для каждого вопроса берётся из его карточки.'} Если оно не указано, даётся 5 минут.</p>
          
          <button id="begin-interview-btn" class="hero-btn hero-btn-primary" style="margin-top: 24px; width: 100%; justify-content: center;">Начать</button>
        </div>
      </div>
    `;

    document.getElementById('close-interview-btn').addEventListener('click', closeInterview);
    document.getElementById('begin-interview-btn').addEventListener('click', () => {
      const input = document.getElementById('participants-input').value;
      if (!input.trim()) {
        alert('Пожалуйста, введите имена участников.');
        return;
      }
      participants = input.split(',').map(s => s.trim()).filter(s => s.length > 0);
      groupedMode = Boolean(document.querySelector('.questions-list .theory-followups'));
      questions = parseQuestions();
      randomOrder = shuffle([...Array(questions.length).keys()]);
      currentQuestionIndex = 0;
      globalScores = {};
      globalFlags = {};
      
      if (questions.length === 0) {
        alert('На этой странице не найдено вопросов.');
        return;
      }
      renderInterview();
    });
  }

  // Render Main Interview View (Quiz Mode)
  function renderInterview() {
    clearInterval(timerInterval);
    const isFinished = currentQuestionIndex >= randomOrder.length;
    
    if (isFinished) {
      renderResults();
      return;
    }

    const currQ = questions[randomOrder[currentQuestionIndex]];
    const timeLimit = currQ.minutes * 60;
    timeLeft = timeLimit;
    const answeringParticipant = participants[currentQuestionIndex % participants.length];
    const followups = groupedMode ? currQ.followups : [];
    const followupAnswers = followups.map((item, index) => `
      <div class="interview-followup-answer" style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.12);">
        <h4 style="margin: 0 0 10px; color: #93c5fd;">Уточнение ${index + 1}: ${escapeHtml(item.text)}</h4>
        ${item.answerHtml}
      </div>
    `).join('');

    let participantsCards = participants.map((p, pIdx) => {
      const scoreKey = `${currQ.id}-${pIdx}`;
      const currentScore = globalScores[scoreKey];
      return `
        <div class="participant-card" style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
          <div class="p-name" style="font-weight: bold; color: white;">${escapeHtml(p)}</div>
          <div class="p-score-controls" style="display: flex; gap: 8px;">
            <button class="score-btn ${currentScore === '✅' ? 'active-score' : ''}" data-key="${scoreKey}" data-val="✅" style="background: none; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; padding: 6px 12px; cursor: pointer; transition: 0.2s;">✅ Знаю</button>
            <button class="score-btn ${currentScore === '❌' ? 'active-score' : ''}" data-key="${scoreKey}" data-val="❌" style="background: none; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; padding: 6px 12px; cursor: pointer; transition: 0.2s;">❌ Не знаю</button>
          </div>
        </div>
      `;
    }).join('');

    modalRoot.innerHTML = `
      <div class="interview-overlay">
        <div class="interview-main-container quiz-mode" style="max-width: 800px;">
          <div class="interview-header">
            <h2>Режим Собеседования</h2>
            <button class="interview-close-btn" id="close-interview-btn">✕ Выход</button>
          </div>
          
          <div class="interview-content">
            <div class="quiz-card" style="padding: 20px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div class="q-counter" style="color: var(--text-secondary);">Вопрос ${currentQuestionIndex + 1} из ${questions.length}</div>
                <label style="display: inline-flex; align-items: center; gap: 8px; color: var(--text-secondary); cursor: pointer; font-size: 0.95rem;">
                  <input type="checkbox" id="flag-incorrect-checkbox" ${globalFlags[currQ.id] ? 'checked' : ''}>
                  ⚠️ Доработать
                </label>
              </div>
              
              ${timeLimit > 0 ? `<div id="q-timer" style="text-align: center; font-size: 1.75rem; font-weight: bold; color: var(--accent-success); margin-bottom: 8px;">⏳ ${formatTime(timeLeft)}</div>` : ''}
              <div style="text-align: center; color: var(--accent-primary); font-size: 1.1rem; font-weight: bold; margin-bottom: 16px;">🎙️ Отвечает: ${escapeHtml(answeringParticipant)}</div>
              <h3 class="q-title" style="margin-top: 0; line-height: 1.5; font-size: 1.5rem; text-align: center;">${escapeHtml(currQ.text)}</h3>

              ${followups.length ? `
                <div id="interview-followup-prompts" style="display: flex; flex-direction: column; gap: 12px; margin-top: 20px;"></div>
                <button id="reveal-followup-btn" class="hero-btn hero-btn-secondary" style="margin-top: 16px; width: 100%; justify-content: center; padding: 12px;">Следующее уточнение (1 из ${followups.length})</button>
              ` : ''}
              
              <button id="show-answer-btn" class="hero-btn hero-btn-secondary" style="margin-top: 24px; width: 100%; justify-content: center; padding: 12px;" ${followups.length ? 'disabled' : ''}>👁️ ${followups.length ? 'Показать разбор и оценить' : 'Показать ответ'}</button>
              
              <div id="answer-box" class="answer-box hidden" style="margin-top: 24px;">
                ${currQ.answerHtml}
                ${followupAnswers}
                
                <div class="grading-section" style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                  <h4 style="margin-top:0; margin-bottom: 16px;">Оценки участников:</h4>
                  <div class="participants-grid" style="display: flex; flex-direction: column; gap: 12px;">
                    ${participantsCards}
                  </div>
                </div>
              </div>
              
              <div class="quiz-footer" style="margin-top: 30px; display: flex; justify-content: flex-end;">
                 <button id="next-question-btn" class="hero-btn hero-btn-primary" style="padding: 12px 24px;" disabled>Следующий вопрос ➔</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Dynamic styles for active score button
    const styleEl = document.createElement('style');
    styleEl.innerHTML = `
      .score-btn:hover { background: rgba(255,255,255,0.1) !important; }
      .score-btn.active-score { background: rgba(99, 102, 241, 0.3) !important; border-color: var(--accent-primary) !important; }
    `;
    modalRoot.appendChild(styleEl);

    document.getElementById('close-interview-btn').addEventListener('click', closeInterview);
    
    const showAnsBtn = document.getElementById('show-answer-btn');
    const answerBox = document.getElementById('answer-box');
    const nextBtn = document.getElementById('next-question-btn');
    const flagCheckbox = document.getElementById('flag-incorrect-checkbox');
    const revealBtn = document.getElementById('reveal-followup-btn');
    const followupPrompts = document.getElementById('interview-followup-prompts');
    let revealedFollowups = 0;

    function revealNextFollowup() {
      if (revealedFollowups >= followups.length) return;
      const item = followups[revealedFollowups];
      const prompt = document.createElement('div');
      prompt.className = 'interview-followup-prompt';
      prompt.style.cssText = 'padding: 14px 16px; border-left: 4px solid #3b82f6; border-radius: 6px; background: rgba(59,130,246,0.1); color: #e2e8f0; line-height: 1.5;';
      prompt.textContent = item.text;
      followupPrompts.appendChild(prompt);
      revealedFollowups++;
      if (revealedFollowups === followups.length) {
        revealBtn.style.display = 'none';
        showAnsBtn.disabled = false;
      } else {
        revealBtn.textContent = `Следующее уточнение (${revealedFollowups + 1} из ${followups.length})`;
      }
    }

    revealBtn?.addEventListener('click', revealNextFollowup);

    if (timeLimit > 0) {
      const timerEl = document.getElementById('q-timer');
      const deadline = Date.now() + timeLimit * 1000;
      timerInterval = setInterval(() => {
        timeLeft = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
        if (timeLeft <= 0) {
          clearInterval(timerInterval);
          const expectedPIdx = currentQuestionIndex % participants.length;
          const key = `${currQ.id}-${expectedPIdx}`;
          if (!globalScores[key]) globalScores[key] = '❌';
          document.querySelector(`.score-btn[data-key="${key}"][data-val="❌"]`)?.classList.add('active-score');
          timerEl.textContent = '⏳ 00:00 — время вышло';
          while (revealedFollowups < followups.length) revealNextFollowup();
          showAnsBtn.click();
        } else {
          timerEl.innerText = `⏳ ${formatTime(timeLeft)}`;
          if (timeLeft <= 10) {
            timerEl.style.color = '#f59e0b'; // Warning orange
          }
        }
      }, 1000);
    }

    if (flagCheckbox) {
      flagCheckbox.addEventListener('change', (e) => {
        globalFlags[currQ.id] = e.target.checked;
      });
    }

    showAnsBtn.addEventListener('click', () => {
      clearInterval(timerInterval);
      answerBox.classList.remove('hidden');
      showAnsBtn.style.display = 'none'; // hide the button once opened
      checkNextButtonState();
    });

    nextBtn.addEventListener('click', () => {
      if (!nextBtn.disabled) {
        currentQuestionIndex++;
        renderInterview();
      }
    });

    // Score button logic
    document.querySelectorAll('.score-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const key = e.target.dataset.key;
        const val = e.target.dataset.val;
        globalScores[key] = val;
        
        // Remove active class from siblings
        e.target.parentElement.querySelectorAll('.score-btn').forEach(b => b.classList.remove('active-score'));
        // Add active class to clicked
        e.target.classList.add('active-score');
        
        // Auto-assign ❌ to the expected participant if someone ELSE gets graded
        const clickedPIdx = parseInt(key.split('-')[1]);
        const expectedPIdx = currentQuestionIndex % participants.length;
        if (clickedPIdx !== expectedPIdx) {
           const expectedKey = `${currQ.id}-${expectedPIdx}`;
           if (!globalScores[expectedKey]) {
               globalScores[expectedKey] = '❌';
               const expectedRow = document.querySelector(`.score-btn[data-key="${expectedKey}"][data-val="❌"]`);
               if (expectedRow) {
                   expectedRow.parentElement.querySelectorAll('.score-btn').forEach(b => b.classList.remove('active-score'));
                   expectedRow.classList.add('active-score');
               }
           }
        }
        
        checkNextButtonState();
      });
    });

    function checkNextButtonState() {
      let anyScored = false;
      for (let i = 0; i < participants.length; i++) {
        if (globalScores[`${currQ.id}-${i}`]) {
          anyScored = true;
          break;
        }
      }
      
      // Cannot go to next if answer is hidden
      if (answerBox.classList.contains('hidden')) {
          anyScored = false;
      }

      if (anyScored) {
        nextBtn.removeAttribute('disabled');
        nextBtn.style.opacity = '1';
        nextBtn.style.cursor = 'pointer';
      } else {
        nextBtn.setAttribute('disabled', 'true');
        nextBtn.style.opacity = '0.5';
        nextBtn.style.cursor = 'not-allowed';
      }
    }

    // Initialize button state
    checkNextButtonState();
  }

  // Render Final Results Summary
  function renderResults() {
    let thead = '<tr><th style="text-align: left;">Вопрос</th><th style="width: 100px; text-align: center;">Доработать</th>' + participants.map(p => `<th>${escapeHtml(p)}</th>`).join('') + '</tr>';
    let tbody = '';
    
    questions.forEach(q => {
      let row = `<tr><td><div class="truncate-text" title="${q.text}" style="max-width: 400px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${q.text}</div></td>`;
      const flagText = globalFlags[q.id] ? '<span style="color: var(--accent-warning);">Да</span>' : '';
      row += `<td style="text-align:center;">${flagText}</td>`;
      participants.forEach((p, pIdx) => {
        const score = globalScores[`${q.id}-${pIdx}`] || '🔲';
        row += `<td style="text-align:center;">${score}</td>`;
      });
      row += '</tr>';
      tbody += row;
    });

    modalRoot.innerHTML = `
      <div class="interview-overlay">
        <div class="interview-main-container">
          <div class="interview-header">
            <h2>Итоги Собеседования</h2>
            <button class="interview-close-btn" id="close-interview-btn">✕ Выход</button>
          </div>
          
          <div class="interview-content" style="flex-direction: column; display: flex;">
            <div class="table-container" style="max-height: 60vh; overflow-y: auto;">
              <table class="interview-table" style="width: 100%; border-collapse: collapse;">
                <thead>${thead}</thead>
                <tbody>${tbody}</tbody>
              </table>
            </div>
            
            <div style="margin-top: 30px; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
              <button id="restart-interview-btn" class="hero-btn hero-btn-primary" style="padding: 12px 24px; display: flex; align-items: center; gap: 8px;">
                🔄 Начать заново
              </button>
              <button id="export-csv-btn" class="hero-btn hero-btn-success" style="padding: 12px 24px; display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                Скачать CSV
              </button>
              <button id="copy-text-btn" class="hero-btn hero-btn-secondary" style="padding: 12px 24px; display: flex; align-items: center; gap: 8px;">
                📋 Скопировать как текст
              </button>
            </div>
          </div>
        </div>
      </div>
    `;

    document.getElementById('close-interview-btn').addEventListener('click', closeInterview);
    
    document.getElementById('restart-interview-btn').addEventListener('click', () => {
      renderSetup();
    });

    document.getElementById('export-csv-btn').addEventListener('click', () => {
      exportCSV();
    });

    document.getElementById('copy-text-btn').addEventListener('click', () => {
      let textContent = "🏆 ИТОГИ СОБЕСЕДОВАНИЯ\n";
      textContent += `👥 Участники: ${participants.join(', ')}\n`;
      textContent += "=========================================\n\n";

      let scoreCounts = {};
      participants.forEach(p => scoreCounts[p] = { correct: 0, incorrect: 0 });

      questions.forEach((q, index) => {
        let questionHeader = `❓ Вопрос ${index + 1}: ${q.text}`;
        if (globalFlags[q.id]) {
          questionHeader += ` [⚠️ Требует доработки]`;
        }
        textContent += questionHeader + "\n   ";
        
        let participantScores = [];
        participants.forEach((p, pIdx) => {
          const score = globalScores[`${q.id}-${pIdx}`];
          let scoreText = score;
          
          if (!scoreText) {
            const turnIndex = randomOrder.indexOf(q.id);
            const expectedPIdx = turnIndex % participants.length;
            scoreText = pIdx === expectedPIdx ? 'Не отвечен' : '...';
          } else {
            if (score === '✅') scoreCounts[p].correct++;
            if (score === '❌') scoreCounts[p].incorrect++;
          }
          
          participantScores.push(`👤 ${p}: ${scoreText}`);
        });
        
        textContent += participantScores.join(' ') + "\n";
      });

      textContent += "=========================================\n";
      textContent += "📊 ОБЩИЙ СЧЁТ:\n";
      participants.forEach(p => {
        textContent += `   ${p}: ${scoreCounts[p].correct} ✅ / ${scoreCounts[p].incorrect} ❌\n`;
      });

      navigator.clipboard.writeText(textContent).then(() => {
        const btn = document.getElementById('copy-text-btn');
        btn.innerHTML = '✅ Скопировано!';
        setTimeout(() => {
           btn.innerHTML = '📋 Скопировать как текст';
        }, 2000);
      }).catch(err => {
        console.error('Не удалось скопировать текст: ', err);
      });
    });
  }

  // Generate and Download CSV
  function exportCSV() {
    let csvContent = "Вопрос;Доработать;" + participants.join(';') + "\n";
    
    questions.forEach(q => {
      let safeText = '"' + q.text.replace(/"/g, '""') + '"';
      let row = [safeText, globalFlags[q.id] ? '⚠️' : '☑️'];
      participants.forEach((p, pIdx) => {
        const score = globalScores[`${q.id}-${pIdx}`];
        if (score) {
          row.push(score);
        } else {
          const turnIndex = randomOrder.indexOf(q.id);
          const expectedPIdx = turnIndex % participants.length;
          row.push(pIdx === expectedPIdx ? 'Не отвечен' : '...');
        }
      });
      csvContent += row.join(';') + "\n";
    });

    // Add BOM for Excel UTF-8 compatibility
    const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'interview_results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function closeInterview() {
    clearInterval(timerInterval);
    modalRoot.innerHTML = '';
    document.body.style.overflow = 'auto'; // Restore scroll
  }

  // Start
  startBtn.addEventListener('click', () => {
    document.body.style.overflow = 'hidden'; // Prevent body scroll
    renderSetup();
  });
});
