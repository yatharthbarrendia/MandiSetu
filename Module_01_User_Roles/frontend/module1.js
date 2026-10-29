import { renderNav } from "/js/nav.js";
import { initI18n } from "/js/i18n.js";
import { getCurrentUser, requireAuth, saveSession } from "/js/auth.js";
import { api } from "/js/api.js";
import { showToast, formatDate } from "/js/utils.js";

document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuth()) return;
  await initI18n();
  renderNav("module-01");

  const user = getCurrentUser();
  setupTabs(user);
  loadProfileData();
  setupEventListeners(user);
});

function setupTabs(user) {
  const role = (user.role || "").toLowerCase();
  const btnFpo = document.getElementById("btn-tab-fpo");
  const btnBuyer = document.getElementById("btn-tab-buyer");

  if (role === "fpo" || role === "admin") {
    btnFpo.style.display = "inline-block";
  }
  if (role === "buyer" || role === "admin") {
    btnBuyer.style.display = "inline-block";
  }

  document.querySelectorAll(".m1-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".m1-tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.style.display = "none");

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.style.display = "block";

      // Lazy load tab data
      if (targetId === "tab-fpo") loadFpoMembers();
      if (targetId === "tab-buyer") loadBuyerKyc();
      if (targetId === "tab-directory") loadDirectory();
    });
  });
}

async function loadProfileData() {
  try {
    const user = await api.get("/api/users/me");
    document.getElementById("profile-name").textContent = user.full_name;
    document.getElementById("profile-email").textContent = user.email;
    document.getElementById("profile-district-val").textContent = user.district || "Maharashtra";
    document.getElementById("profile-lang-val").textContent = user.preferred_lang.toUpperCase();

    const roleBadge = document.getElementById("profile-role-badge");
    roleBadge.className = `badge badge-${user.role.toLowerCase()}`;
    roleBadge.textContent = user.role;

    const iconMap = {
      "Farmer": "👨‍🌾",
      "FPO": "🏢",
      "Buyer": "🛒",
      "Admin": "🏛️"
    };
    document.getElementById("user-avatar-icon").textContent = iconMap[user.role] || "👤";

    // Fill form
    document.getElementById("edit-name").value = user.full_name || "";
    document.getElementById("edit-phone").value = user.phone || "";
    document.getElementById("edit-district").value = user.district || "Nashik";
    document.getElementById("edit-taluka").value = user.taluka || "";
    document.getElementById("edit-lang").value = user.preferred_lang || "en";
  } catch (err) {
    showToast(err.message || "Failed to load user profile", "danger");
  }
}

function setupEventListeners(user) {
  // Update Profile
  document.getElementById("form-update-profile").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = {
        full_name: document.getElementById("edit-name").value.trim(),
        phone: document.getElementById("edit-phone").value.trim(),
        district: document.getElementById("edit-district").value,
        taluka: document.getElementById("edit-taluka").value.trim(),
        preferred_lang: document.getElementById("edit-lang").value
      };
      const updated = await api.put("/api/users/me", payload);
      saveSession(updated, {});
      showToast("Profile settings updated successfully!", "success");
      loadProfileData();
      renderNav("module-01");
    } catch (err) {
      showToast(err.message || "Could not update profile", "danger");
    }
  });

  // FPO Enroll Farmer
  const fpoForm = document.getElementById("form-add-farmer");
  if (fpoForm) {
    fpoForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const inputVal = document.getElementById("fpo-farmer-input").value.trim();
        const payload = {
          land_size_acres: parseFloat(document.getElementById("fpo-farmer-acres").value) || 2.0,
          primary_crop: document.getElementById("fpo-farmer-crop").value
        };
        if (inputVal.includes("@")) {
          payload.farmer_email = inputVal;
        } else {
          payload.farmer_id = parseInt(inputVal);
        }
        await api.post("/api/users/fpo/farmers", payload);
        showToast("Farmer enrolled into FPO cluster!", "success");
        fpoForm.reset();
        loadFpoMembers();
      } catch (err) {
        showToast(err.message || "Failed to enroll farmer", "danger");
      }
    });
  }

  // Buyer KYC Submit
  const buyerForm = document.getElementById("form-buyer-kyc");
  if (buyerForm) {
    buyerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const payload = {
          company_name: document.getElementById("buyer-company").value.trim(),
          gstin: document.getElementById("buyer-gstin").value.trim(),
          mandi_license_no: document.getElementById("buyer-license").value.trim()
        };
        const res = await api.post("/api/users/buyers/verification", payload);
        showToast("Buyer verification documents submitted!", "success");
        loadBuyerKyc();
      } catch (err) {
        showToast(err.message || "Failed to submit KYC documents", "danger");
      }
    });
  }

  // Filter Directory
  document.getElementById("btn-search-dir").addEventListener("click", () => {
    loadDirectory();
  });
}

async function loadFpoMembers() {
  const tbody = document.getElementById("fpo-members-tbody");
  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Loading FPO members...</td></tr>`;
  try {
    const list = await api.get("/api/users/fpo/farmers");
    document.getElementById("fpo-member-count").textContent = `${list.length} Farmers Enrolled`;
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No farmers enrolled yet in this FPO cluster.</td></tr>`;
      return;
    }
    tbody.innerHTML = list.map(m => `
      <tr>
        <td><strong>${m.farmer_name}</strong></td>
        <td>${m.farmer_email}</td>
        <td>${m.farmer_district}</td>
        <td>${m.land_size_acres} Acres</td>
        <td><span class="badge badge-farmer">${m.primary_crop}</span></td>
        <td><span class="badge badge-success">${m.status}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--status-danger);">Failed to load members: ${err.message}</td></tr>`;
  }
}

async function loadBuyerKyc() {
  const detailsBox = document.getElementById("buyer-kyc-details");
  const badge = document.getElementById("buyer-status-badge");
  try {
    const doc = await api.get("/api/users/buyers/verification");
    if (!doc) {
      detailsBox.innerHTML = `<p style="color:var(--text-muted); font-size:0.9rem;">No verification documents submitted yet. Please submit above.</p>`;
      badge.textContent = "Unregistered";
      badge.className = "badge badge-warning";
      return;
    }

    badge.textContent = doc.status.toUpperCase();
    badge.className = `badge badge-${doc.status === 'verified' ? 'success' : doc.status === 'rejected' ? 'danger' : 'warning'}`;

    document.getElementById("buyer-company").value = doc.company_name;
    document.getElementById("buyer-gstin").value = doc.gstin;
    document.getElementById("buyer-license").value = doc.mandi_license_no;

    detailsBox.innerHTML = `
      <div class="kyc-status-card">
        <p><strong>Company:</strong> ${doc.company_name}</p>
        <p><strong>GSTIN:</strong> ${doc.gstin}</p>
        <p><strong>Mandi License:</strong> ${doc.mandi_license_no}</p>
        <p><strong>Verification Status:</strong> <span class="badge badge-${doc.status === 'verified' ? 'success' : 'warning'}">${doc.status.toUpperCase()}</span></p>
        <p><strong>Officer Audit Remarks:</strong> ${doc.verification_remarks || 'Pending audit'}</p>
        <p><strong>Last Updated:</strong> ${formatDate(doc.verified_at || doc.created_at)}</p>
      </div>
    `;
  } catch (err) {
    detailsBox.innerHTML = `<p style="color:var(--status-danger);">Error fetching verification: ${err.message}</p>`;
  }
}

async function loadDirectory() {
  const tbody = document.getElementById("directory-tbody");
  tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Loading directory...</td></tr>`;
  const role = document.getElementById("dir-filter-role").value;
  const district = document.getElementById("dir-filter-district").value;

  try {
    const params = {};
    if (role) params.role = role;
    if (district) params.district = district;

    const users = await api.get("/api/users/directory", params);
    if (users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No users matching filters.</td></tr>`;
      return;
    }
    tbody.innerHTML = users.map(u => `
      <tr>
        <td><strong>${u.full_name}</strong> <small style="color:var(--text-muted);">(${u.email})</small></td>
        <td><span class="badge badge-${u.role.toLowerCase()}">${u.role}</span></td>
        <td>${u.district}, Maharashtra</td>
        <td>${u.preferred_lang.toUpperCase()}</td>
        <td><span class="badge badge-success">Active</span></td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--status-danger);">Error: ${err.message}</td></tr>`;
  }
}
