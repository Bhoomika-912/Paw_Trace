function getSharedNavbar() {
  return `
  <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm fixed-top">
    <div class="container">
      <a class="navbar-brand fw-bold text-primary" href="index.html">
        <i></i> 🐾 PawTrace
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="mainNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item"><a class="nav-link" href="index.html">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="about.html">About</a></li>
          <li class="nav-item"><a class="nav-link" href="alerts.html">Alerts</a></li>
          <li class="nav-item"><a class="nav-link" href="tracking.html">Tracking</a></li>
          <li class="nav-item"><a class="nav-link" href="report.html">Report</a></li>
          <li class="nav-item"><a class="nav-link" href="reward.html">Rewards</a></li>
          <li class="nav-item"><a class="nav-link" href="feedback.html">Feedback</a></li>
          <li class="nav-item"><a class="nav-link" href="contact.html">Contact</a></li>
          <li class="nav-item"><a class="nav-link" href="login.html">Login</a></li>
        </ul>
      </div>
    </div>
  </nav>
  `;
}

function getSharedFooter() {
  return `
  <footer class="footer mt-5 py-4">
    <div class="container">
      <div class="row g-3 align-items-center">
        <div class="col-md-6">
          <h6 class="mb-1">🐾 PawTrace</h6>
          <p class="mb-0 small">Helping families reunite with pets through quick reports and community alerts.</p>
        </div>
        <div class="col-md-6 text-md-end">
          <a class="social-icon" href="#"><i class="bi bi-facebook"></i></a>
          <a class="social-icon" href="#"><i class="bi bi-instagram"></i></a>
          <a class="social-icon" href="#"><i class="bi bi-twitter-x"></i></a>
          <a class="social-icon" href="#"><i class="bi bi-youtube"></i></a>
        </div>
      </div>
    </div>
  </footer>
  `;
}

function setActiveNav() {
  const path = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-link").forEach((link) => {
    const href = link.getAttribute("href");
    if (href === path) {
      link.classList.add("active", "fw-semibold", "text-primary");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const navMount = document.getElementById("navbar-placeholder");
  const footerMount = document.getElementById("footer-placeholder");
  if (navMount) navMount.innerHTML = getSharedNavbar();
  if (footerMount) footerMount.innerHTML = getSharedFooter();
  setActiveNav();
});
