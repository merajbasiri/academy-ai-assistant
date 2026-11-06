const $ = (id) => document.getElementById(id);
const toman = (amount) => new Intl.NumberFormat('en-US').format(amount);

async function readJSON(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function fillSummary(summary) {
  $('student-count').textContent = String(summary.student_count).padStart(2, '0');
  $('active-count').textContent = String(summary.active_count).padStart(2, '0');
  $('outstanding-total').textContent = `${(summary.total_outstanding / 1_000_000).toFixed(1)}M`;
}

function setText(id, value) { $(id).textContent = value; }

async function showStudent(studentId) {
  try {
    const [student, balance] = await Promise.all([
      readJSON(`/students/${encodeURIComponent(studentId)}`),
      readJSON(`/students/${encodeURIComponent(studentId)}/balance`),
    ]);
    setText('student-avatar', student.student_id.slice(-2));
    setText('student-name', student.name);
    setText('student-course', `${student.course} · ${student.student_id}`);
    setText('student-status', student.enrollment_status);
    $('student-status').classList.toggle('pending', student.enrollment_status !== 'active');
    setText('student-tuition', toman(balance.tuition));
    setText('student-paid', toman(balance.paid));
    setText('student-balance', toman(balance.balance));
    const progress = balance.tuition ? Math.min(100, Math.round(balance.paid / balance.tuition * 100)) : 100;
    setText('progress-label', `${progress}%`);
    $('progress-fill').style.width = `${progress}%`;
    $('student-credit').hidden = balance.credit === 0;
    setText('student-credit', `Extra credit: ${toman(balance.credit)} toman`);
    const count = student.payments.length;
    setText('payment-count', `${count} transaction${count === 1 ? '' : 's'}`);
    const list = $('payment-list');
    list.replaceChildren();
    if (!count) {
      const note = document.createElement('p');
      note.className = 'empty-note';
      note.textContent = 'No payments recorded for this student.';
      list.append(note);
      return;
    }
    student.payments.forEach((payment, index) => {
      const row = document.createElement('div');
      row.className = 'payment-item';
      const left = document.createElement('div');
      left.className = 'payment-label';
      const icon = document.createElement('span');
      icon.className = 'payment-icon';
      icon.textContent = '↓';
      const label = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = `Tuition payment #${index + 1}`;
      const date = document.createElement('small');
      date.textContent = payment.date;
      label.append(title, date);
      left.append(icon, label);
      const amount = document.createElement('strong');
      amount.className = 'payment-amount';
      amount.textContent = `+ ${toman(payment.amount)}`;
      row.append(left, amount);
      list.append(row);
    });
  } catch (error) {
    setText('student-name', `Could not load student: ${error.message}`);
  }
}

async function initialize() {
  try {
    const [summary, students, config] = await Promise.all([
      readJSON('/summary'), readJSON('/students'), readJSON('/config'),
    ]);
    fillSummary(summary);
    const picker = $('student-picker');
    picker.replaceChildren();
    students.forEach((student) => {
      const option = document.createElement('option');
      option.value = student.student_id;
      option.textContent = `${student.student_id} — ${student.course}`;
      picker.append(option);
    });
    picker.addEventListener('change', () => showStudent(picker.value));
    if (students.length) await showStudent(students[0].student_id);
    $('chat-indicator').textContent = config.chat_enabled ? 'AVAILABLE' : 'API KEY NEEDED';
    $('chat-indicator').classList.toggle('ready', config.chat_enabled);
  } catch (error) {
    setText('student-name', 'Demo data unavailable');
    setText('chat-result', `Could not connect to the API: ${error.message}`);
  }
}

$('chat-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = $('chat-message').value.trim();
  if (message.length < 3) {
    setText('chat-result', 'Please enter a question with at least 3 characters.');
    return;
  }
  const submit = $('chat-submit');
  submit.disabled = true;
  setText('chat-result', 'Sending question to the agent…');
  try {
    const result = await readJSON('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message}),
    });
    setText('chat-result', `${result.answer}\n\nTools selected: ${result.tools_used.join(', ') || 'none'}`);
    $('chat-result').classList.add('has-answer');
  } catch (error) {
    setText('chat-result', error.message);
    $('chat-result').classList.remove('has-answer');
  } finally {
    submit.disabled = false;
  }
});

initialize();