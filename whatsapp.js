/**
 * FD Saathi 2.0 — WhatsApp Bot Simulation Component
 * Simulates a multi-turn chatbot conversation for FD analysis.
 */

const waBotReplies = {
  default: [
    'Namaste! I am FD Saathi 🙏 Tell me your FD amount and I will help you decide.',
    'Please share your FD amount to get started. For example: "My FD is ₹5 lakhs"',
  ]
};

let waState = { step: 0, amt: 0, fdRate: 0, days: 0 };

function sendWa() {
  const inp = document.getElementById('waInput');
  const msg = inp.value.trim();
  if (!msg) return;
  inp.value = '';
  appendWaMsg(msg, 'user');
  setTimeout(() => processWaMsg(msg), 800 + Math.random() * 400);
}

function waQuick(msg) {
  document.getElementById('waInput').value = msg;
  sendWa();
}

function appendWaMsg(text, type) {
  const body = document.getElementById('waMessages');
  const t = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  body.insertAdjacentHTML('beforeend',
    `<div class="wa-msg ${type}">${text}<div class="wa-tick">${type === 'bot' ? '✓✓ ' : ''}${t}</div></div>`);
  body.scrollTop = body.scrollHeight;
}

function appendTyping() {
  const body = document.getElementById('waMessages');
  body.insertAdjacentHTML('beforeend',
    '<div class="wa-msg bot" id="waTyping"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>');
  body.scrollTop = body.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById('waTyping');
  if (t) t.remove();
}

function processWaMsg(msg) {
  appendTyping();
  const lower = msg.toLowerCase();
  let reply = '';

  if (lower.includes('loan against fd') || lower.includes('what is loan')) {
    reply = 'Loan Against FD is where the bank gives you money using your FD as security 🏦 Your FD stays intact and earns interest. The loan is usually 85% of FD value at a lower rate than personal loans!';
  } else if (lower.includes('break') || lower.includes('tod')) {
    reply = "Breaking FD early has a penalty — usually 0.5% + partial interest loss. Let me calculate if it's better to break or take a loan. Tell me your FD amount!";
  } else {
    const numMatch = msg.match(/[\d,]+/);
    if (numMatch && waState.step === 0) {
      waState.amt = parseInt(numMatch[0].replace(/,/g, ''));
      waState.step = 1;
      reply = `Got it! Your FD is ${fmt(waState.amt)} 📊 What is your FD interest rate? (e.g., "7.5%")`;
    } else if (numMatch && waState.step === 1) {
      waState.fdRate = parseFloat(numMatch[0]);
      waState.step = 2;
      reply = `FD rate: ${waState.fdRate}% ✓ How many days are left until maturity? (e.g., "180 days")`;
    } else if (numMatch && waState.step === 2) {
      waState.days = parseInt(numMatch[0]);
      waState.step = 3;
      const r = calcFD(waState.amt, waState.fdRate, waState.days, 11);
      const isLoan = r.rec === 'loan';
      reply = `✅ Analysis complete!\n\n*FD Amount:* ${fmt(waState.amt)}\n*FD Penalty if broken:* ${fmt(r.penalty)}\n*Loan Interest cost:* ${fmt(r.loanInt)}\n\n🤖 *Recommendation: ${isLoan ? 'Take a Loan!' : 'Break your FD'} *\n\n${isLoan
        ? `You save ${fmt(r.savings)} by taking a loan! Your FD stays safe. Confidence: ${r.conf}%.`
        : `Breaking FD is cheaper by ${fmt(Math.abs(r.savings))}. Loan would cost more here.`}\n\n${isLoan ? 'Reply "APPLY" to apply for loan instantly!' : ''}`;
      waState.step = 0;
    } else if (lower === 'apply' || lower.includes('apply')) {
      const approved = Math.round(waState.amt * 0.85) || 425000;
      reply = `🎉 *Loan APPROVED!*\n\n✅ Approved Amount: ${fmt(approved)}\n💰 EMI: ~${fmt(Math.round(approved * 0.01))}/month\n⏱ Disbursement: Within 24 hours\n🔒 FD Status: Safe & Earning\n\nA bank executive will call you shortly!`;
    } else {
      reply = waBotReplies.default[Math.floor(Math.random() * waBotReplies.default.length)];
    }
  }

  setTimeout(() => {
    removeTyping();
    appendWaMsg(reply.replace(/\n/g, '<br>'), 'bot');
  }, 1200 + Math.random() * 500);
}

function clearWa() {
  waState = { step: 0, amt: 0, fdRate: 0, days: 0 };
  document.getElementById('waMessages').innerHTML =
    '<div class="wa-msg bot">Namaste! 🙏 I\'m FD Saathi. I can help you decide whether to break your FD or take a loan against it. Just type your FD amount to get started!<div class="wa-tick">✓✓ 10:00 AM</div></div>';
}

function waDemo() {
  const steps = [
    { delay: 500, msg: 'My FD is 5 lakhs' },
    { delay: 2500, msg: '7.5' },
    { delay: 4500, msg: '180 days' },
    { delay: 7000, msg: 'APPLY' }
  ];
  steps.forEach(s => setTimeout(() => waQuick(s.msg), s.delay));
}
