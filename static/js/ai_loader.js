/* AI Doctor Loader — MediCare HMS */

function showLoader() {
  const btn = document.getElementById('submit-btn');
  const skeleton = document.getElementById('ai-skeleton');
  const report = document.getElementById('report-card');

  // Disable button and show loading state
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `
      <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      AI is analyzing...
    `;
    btn.style.opacity = '0.75';
    btn.style.cursor = 'not-allowed';
  }

  // Show skeleton, hide existing report
  if (skeleton) skeleton.classList.remove('hidden');
  if (report) report.style.display = 'none';
}

// On page load — if there's a report, scroll to it smoothly
document.addEventListener('DOMContentLoaded', () => {
  const report = document.getElementById('report-card');
  if (report) {
    setTimeout(() => {
      report.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
  }
});
