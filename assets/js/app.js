const samplePets = [
  {
    id: "p1",
    name: "Bruna",
    animalType: "dog",
    breed: "golden retriver",
    color: "gold",
    location: "Maple Street, LA",
    dateMissing: "2026-03-15",
    contact: "+1 555-9844",
    reward: "150",
    description: "golden hair dog, shy around strangers.",
    image: "dog.jpg"
  },
  {
    id: "p2",
    name: "Luna",
    animalType: "Cat",
    breed: "Siamese",
    color: "Cream",
    location: "Maple Street, LA",
    dateMissing: "2026-03-15",
    contact: "+1 555-9844",
    reward: "150",
    description: "Blue-eyed cat, shy around strangers.",
    image: "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=900&q=80"
  },
  {
    id: "p3",
    name: "Coco",
    animalType: "Bird",
    breed: "Parrot",
    color: "Green",
    location: "Sunrise Avenue, Miami",
    dateMissing: "2026-03-19",
    contact: "+1 555-6632",
    reward: "200",
    description: "Responds to whistling, can say hello.",
    image: "parrot.jpg"
  }
];

function getPets() {
  const stored = localStorage.getItem("missingPets");
  if (!stored) {
    localStorage.setItem("missingPets", JSON.stringify(samplePets));
    return samplePets;
  }
  return JSON.parse(stored);
}

function savePets(data) {
  localStorage.setItem("missingPets", JSON.stringify(data));
}

function readImageAsDataUrl(file) {
  return new Promise((resolve) => {
    if (!file) return resolve("");
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.readAsDataURL(file);
  });
}

function formatPetCard(pet, withBadge = false) {
  return `
  <div class="col-md-6 col-lg-4 fade-in">
    <div class="card soft-card h-100">
      <img src="${pet.image || "https://images.unsplash.com/photo-1450778869180-41d0601e046e?auto=format&fit=crop&w=900&q=80"}" class="pet-card-img" alt="${pet.name}">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <h5 class="card-title mb-0">${pet.name}</h5>
          ${withBadge ? '<span class="alert-badge">New</span>' : ""}
        </div>
        <p class="text-muted small mb-2">${pet.animalType} • ${pet.breed}</p>
        <p class="mb-1"><i class="bi bi-geo-alt text-primary"></i> ${pet.location}</p>
        <p class="mb-1"><i class="bi bi-calendar-event text-primary"></i> ${pet.dateMissing}</p>
        <p class="mb-0"><i class="bi bi-award text-primary"></i> Reward: $${pet.reward || 0}</p>
      </div>
    </div>
  </div>
  `;
}

function initHomeSearch() {
  const input = document.getElementById("homeSearch");
  const output = document.getElementById("homePetCards");
  if (!input || !output) return;
  const pets = getPets();
  const render = (list) => {
    output.innerHTML = list.slice(0, 6).map((pet) => formatPetCard(pet)).join("");
  };
  render(pets);
  input.addEventListener("input", () => {
    const q = input.value.toLowerCase();
    const filtered = pets.filter((p) =>
      [p.name, p.animalType, p.breed, p.location].join(" ").toLowerCase().includes(q)
    );
    render(filtered);
  });
}

function initLoginSignupValidation() {
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPassword").value.trim();
      if (!email || !password || !email.includes("@")) {
        return alert("Please enter a valid email and password.");
      }
      alert("Login successful (demo).");
      loginForm.reset();
    });
  }
  if (signupForm) {
    signupForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const name = document.getElementById("signupName").value.trim();
      const email = document.getElementById("signupEmail").value.trim();
      const pass = document.getElementById("signupPassword").value.trim();
      const confirm = document.getElementById("signupConfirm").value.trim();
      if (!name || !email.includes("@") || pass.length < 6 || pass !== confirm) {
        return alert("Check signup details. Password must be 6+ chars and match.");
      }
      alert("Signup successful (demo).");
      signupForm.reset();
    });
  }
}

function initReportForm() {
  const form = document.getElementById("reportForm");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const imageFile = document.getElementById("petImage").files[0];
    const image = await readImageAsDataUrl(imageFile);
    const pet = {
      id: `p-${Date.now()}`,
      name: document.getElementById("petName").value.trim(),
      animalType: document.getElementById("animalType").value.trim(),
      breed: document.getElementById("breed").value.trim(),
      color: document.getElementById("color").value.trim(),
      location: document.getElementById("location").value.trim(),
      dateMissing: document.getElementById("dateMissing").value,
      contact: document.getElementById("ownerContact").value.trim(),
      reward: document.getElementById("reward").value.trim() || "0",
      description: document.getElementById("description").value.trim(),
      image
    };
    if (!pet.name || !pet.animalType || !pet.location || !pet.dateMissing || !pet.contact) {
      return alert("Please fill all required fields.");
    }
    const pets = getPets();
    pets.unshift(pet);
    savePets(pets);
    alert("Missing pet report submitted successfully!");
    form.reset();
  });
}

function initAlertsPage() {
  const grid = document.getElementById("alertsGrid");
  const search = document.getElementById("alertsSearch");
  const typeFilter = document.getElementById("animalFilter");
  if (!grid || !search || !typeFilter) return;
  const pets = getPets();
  const render = () => {
    const q = search.value.toLowerCase();
    const type = typeFilter.value;
    const list = pets.filter((pet) => {
      const matchType = type === "All" || pet.animalType === type;
      const matchQuery = [pet.name, pet.breed, pet.location, pet.animalType]
        .join(" ")
        .toLowerCase()
        .includes(q);
      return matchType && matchQuery;
    });
    grid.innerHTML = list.map((pet) => formatPetCard(pet, true)).join("");
  };
  render();
  search.addEventListener("input", render);
  typeFilter.addEventListener("change", render);
}

function initTrackingUI() {
  const statusEl = document.getElementById("trackingStatus");
  const btn = document.getElementById("reportSightingBtn");
  if (!statusEl || !btn) return;
  const statuses = [
    { label: "Searching", cls: "status-searching" },
    { label: "In Progress", cls: "status-progress" },
    { label: "Found", cls: "status-found" }
  ];
  let idx = 0;
  btn.addEventListener("click", () => {
    idx = (idx + 1) % statuses.length;
    statusEl.className = `status-pill ${statuses[idx].cls}`;
    statusEl.textContent = statuses[idx].label;
    alert("Sighting update recorded (demo).");
  });
}

function initRewardsPage() {
  const list = document.getElementById("rewardList");
  const form = document.getElementById("claimForm");
  if (list) {
    list.innerHTML = getPets()
      .slice(0, 6)
      .map((pet) => `
      <tr>
        <td>${pet.name}</td>
        <td>${pet.animalType}</td>
        <td>${pet.location}</td>
        <td class="fw-semibold text-success">$${pet.reward || 0}</td>
      </tr>
    `)
      .join("");
  }
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      alert("Reward claim submitted successfully!");
      form.reset();
    });
  }
}

function initFeedbackPage() {
  const stars = document.querySelectorAll(".rating-star");
  const ratingInput = document.getElementById("ratingValue");
  const form = document.getElementById("feedbackForm");
  if (stars.length) {
    stars.forEach((star) => {
      star.addEventListener("click", () => {
        const value = Number(star.dataset.value);
        ratingInput.value = value;
        stars.forEach((s) => s.classList.toggle("active", Number(s.dataset.value) <= value));
      });
    });
  }
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const rating = ratingInput.value;
      if (!rating) return alert("Please select a star rating first.");
      alert("Thank you for your feedback!");
      form.reset();
      stars.forEach((s) => s.classList.remove("active"));
      ratingInput.value = "";
    });
  }
}

function initContactForm() {
  const form = document.getElementById("contactForm");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Message sent successfully!");
    form.reset();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  getPets();
  initHomeSearch();
  initLoginSignupValidation();
  initReportForm();
  initAlertsPage();
  initTrackingUI();
  initRewardsPage();
  initFeedbackPage();
  initContactForm();
});
