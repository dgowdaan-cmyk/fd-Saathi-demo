/**
 * FD Saathi 2.0 — Revenue Dashboard Component
 * Renders the monthly revenue projection chart using Chart.js.
 */

function initRevenueChart() {
  if (revChart) return; // Already initialized
  const ctx = document.getElementById('revenueChart').getContext('2d');
  revChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: 'SaaS MRR (₹L)',
          data: [1.2, 1.8, 2.1, 2.4, 2.9, 3.2, 3.8, 4.2, 4.9, 5.6, 6.3, 7.1],
          backgroundColor: 'rgba(26,86,219,.15)',
          borderColor: '#1a56db',
          borderWidth: 2, borderRadius: 4, borderSkipped: false
        },
        {
          label: 'API Revenue (₹L)',
          data: [0.3, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 1.8, 2.1, 2.4, 2.8, 3.2],
          backgroundColor: 'rgba(15,122,74,.15)',
          borderColor: '#0f7a4a',
          borderWidth: 2, borderRadius: 4, borderSkipped: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: 'rgba(0,0,0,.04)' }, ticks: { callback: v => '₹' + v + 'L', font: { size: 11 } } },
        x: { grid: { display: false }, ticks: { font: { size: 11 } } }
      }
    }
  });
}
