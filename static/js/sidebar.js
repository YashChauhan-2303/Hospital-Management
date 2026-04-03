/* Sidebar JS — MediCare HMS */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const isOpen = !sidebar.classList.contains('-translate-x-full');

  if (isOpen) {
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
  } else {
    sidebar.classList.remove('-translate-x-full');
    overlay.classList.remove('hidden');
  }
}

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
  const flashContainer = document.getElementById('flash-messages');
  if (flashContainer) {
    setTimeout(() => {
      flashContainer.style.transition = 'opacity 0.5s ease';
      flashContainer.style.opacity = '0';
      setTimeout(() => flashContainer.remove(), 500);
    }, 5000);
  }
});
