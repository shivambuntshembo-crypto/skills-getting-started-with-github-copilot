document.addEventListener("DOMContentLoaded", () => {
  const registrationForm = document.getElementById("registration-form");
  const messageDiv = document.getElementById("message");
  const roleSelect = document.getElementById("role");
  const collegeSelect = document.getElementById("college");
  const activitySelect = document.getElementById("activity");
  const activitiesList = document.getElementById("activities-list");
  const registrationsList = document.getElementById("registrations-list");

  let colleges = [];

  function showMessage(text, kind = "success") {
    messageDiv.textContent = text;
    messageDiv.className = `message ${kind}`;
    messageDiv.classList.remove("hidden");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function populateCollegeOptions() {
    collegeSelect.innerHTML = '<option value="">Select a college</option>';
    colleges.forEach((college) => {
      const option = document.createElement("option");
      option.value = college.id;
      option.textContent = `${college.name} (${college.city})`;
      collegeSelect.appendChild(option);
    });
  }

  function renderActivities(activities) {
    if (!activities.length) {
      activitiesList.innerHTML = '<p class="loading-state">No activities for this college.</p>';
      return;
    }

    activitiesList.innerHTML = "";
    activities.forEach((activity) => {
      const spotsLeft = activity.max_participants - activity.participants.length;
      const participants = activity.participants.length
        ? activity.participants.join(", ")
        : "No participants yet";

      const card = document.createElement("article");
      card.className = "data-card";
      card.innerHTML = `
        <h3>${activity.title}</h3>
        <p>${activity.description}</p>
        <p><strong>Schedule:</strong> ${activity.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <p><strong>Participants:</strong> ${participants}</p>
      `;
      activitiesList.appendChild(card);
    });
  }

  function renderRegistrations(registrations) {
    if (!registrations.length) {
      registrationsList.innerHTML = '<p class="loading-state">No registrations yet for this college.</p>';
      return;
    }

    registrationsList.innerHTML = "";
    registrations.forEach((registration) => {
      const card = document.createElement("article");
      card.className = "registration-card";
      card.innerHTML = `
        <div class="registration-head">
          <h3>${registration.name}</h3>
          <span class="role-pill">${registration.role}</span>
        </div>
        <p><strong>Email:</strong> ${registration.email}</p>
        <p><strong>College:</strong> ${registration.college_name}</p>
        <p><strong>Activity:</strong> ${registration.activity_title}</p>
        <p class="feedback-box">${registration.dummy_feedback}</p>
        <button
          class="danger-btn"
          type="button"
          data-registration-id="${registration.id}"
        >Remove</button>
      `;
      registrationsList.appendChild(card);
    });
  }

  async function fetchActivities(collegeId) {
    if (!collegeId) {
      activitiesList.innerHTML = '<p class="loading-state">Select a college to view activities.</p>';
      activitySelect.innerHTML = '<option value="">Select an activity</option>';
      return;
    }

    try {
      const response = await fetch(`/activities?college_id=${encodeURIComponent(collegeId)}`, {
        cache: "no-store",
      });
      const payload = await response.json();
      const activities = payload.activities || [];

      renderActivities(activities);
      activitySelect.innerHTML = '<option value="">Select an activity</option>';
      activities.forEach((activity) => {
        const option = document.createElement("option");
        option.value = activity.id;
        option.textContent = activity.title;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = '<p class="loading-state">Failed to load activities.</p>';
      console.error("Error loading activities", error);
    }
  }

  async function fetchRegistrations(collegeId) {
    if (!collegeId) {
      registrationsList.innerHTML = '<p class="loading-state">No registrations yet for this college.</p>';
      return;
    }

    try {
      const response = await fetch(`/registrations?college_id=${encodeURIComponent(collegeId)}`, {
        cache: "no-store",
      });
      const payload = await response.json();
      renderRegistrations(payload.registrations || []);
    } catch (error) {
      registrationsList.innerHTML = '<p class="loading-state">Failed to load registrations.</p>';
      console.error("Error loading registrations", error);
    }
  }

  async function initialize() {
    try {
      const response = await fetch("/colleges", { cache: "no-store" });
      const payload = await response.json();
      colleges = payload.colleges || [];
      populateCollegeOptions();
    } catch (error) {
      showMessage("Unable to load colleges right now.", "error");
      console.error("Error loading colleges", error);
    }
  }

  collegeSelect.addEventListener("change", async () => {
    const collegeId = collegeSelect.value;
    await fetchActivities(collegeId);
    await fetchRegistrations(collegeId);
  });

  registrationForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      role: roleSelect.value,
      college_id: collegeSelect.value,
      activity_id: activitySelect.value,
    };

    try {
      const response = await fetch("/registrations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok) {
        showMessage(result.detail || "Registration failed", "error");
        return;
      }

      showMessage(`${result.message}. ${result.registration.dummy_feedback}`, "success");
      registrationForm.reset();
      roleSelect.value = "student";
      collegeSelect.value = payload.college_id;
      await fetchActivities(payload.college_id);
      await fetchRegistrations(payload.college_id);
    } catch (error) {
      showMessage("Failed to create registration. Try again.", "error");
      console.error("Error creating registration", error);
    }
  });

  registrationsList.addEventListener("click", async (event) => {
    const removeButton = event.target.closest(".danger-btn");
    if (!removeButton) {
      return;
    }

    const registrationId = removeButton.dataset.registrationId;
    const selectedCollegeId = collegeSelect.value;

    try {
      const response = await fetch(`/registrations/${encodeURIComponent(registrationId)}`, {
        method: "DELETE",
      });
      const result = await response.json();

      if (!response.ok) {
        showMessage(result.detail || "Failed to remove registration", "error");
        return;
      }

      showMessage(result.message, "success");
      await fetchActivities(selectedCollegeId);
      await fetchRegistrations(selectedCollegeId);
    } catch (error) {
      showMessage("Failed to remove registration. Try again.", "error");
      console.error("Error removing registration", error);
    }
  });

  initialize();
});
