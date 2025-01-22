function updateActiveMenu() {
  const menuItems = document.querySelectorAll(".menu-item");
  const currentPath = window.location.pathname; // Get the current path

  // Remove active class from all items
  menuItems.forEach((item) => {
    item.classList.remove("active");
  });

  // Set active class for the current path
  menuItems.forEach((item) => {
    const itemPath = item.getAttribute("href");

    // Check if the current path includes the item path
    if (currentPath.includes(itemPath)) {
      item.classList.add("active"); // Add active class to the current menu item
    }

    const keywords = ["post", "quizz", "cgpa", "timetable", "resume", "forum"];
    const toolsMenuItem = document.querySelector('.menu-item[href="/tools"]');

    if (keywords.some((keyword) => currentPath.includes(keyword))) {
      if (toolsMenuItem) {
        toolsMenuItem.classList.add("active"); // Keep "Tools" active
      }
    }
  });
}

// Function to handle menu item clicks
function activateMenu(event) {
  const menuItems = document.querySelectorAll(".menu-item");

  // Remove active class from all items
  menuItems.forEach((item) => {
    item.classList.remove("active");
  });

  // Check if the logo is clicked
  if (event.currentTarget.classList.contains("logo-brand")) {
    const dashboardMenuItem = document.querySelector(
      '.menu-item[href="/dashboard"]'
    );
    if (dashboardMenuItem) {
      dashboardMenuItem.classList.add("active"); // Set active class for Dashboard
    }
    localStorage.setItem("activeLink", "/dashboard");
  } else if (event.currentTarget.classList.contains("menu-item")) {
    const activeLink = event.currentTarget.getAttribute("href");
    event.currentTarget.classList.add("active"); // Set active class for clicked menu item
    localStorage.setItem("activeLink", activeLink);

    // Redirect to the clicked link
    window.location.href = activeLink; // Redirect to the clicked link
  }
}

function setDefaultActiveMenu() {
  const dashboardItem = document.querySelector('.menu-item[href="/dashboard"]');
  if (dashboardItem) {
    dashboardItem.classList.add("active");
  }
}

const storedActiveLink = localStorage.getItem("activeLink");
if (storedActiveLink) {
  const menuItems = document.querySelectorAll(".menu-item");
  menuItems.forEach((item) => {
    if (item.getAttribute("href") === storedActiveLink) {
      item.classList.add("active");
    }
  });
} else {
  setDefaultActiveMenu();
}

const logoBrand = document.querySelector(".logo-brand");
if (logoBrand) {
  logoBrand.addEventListener("click", activateMenu);
}

document.querySelectorAll(".menu-item, .logo-brand").forEach((item) => {
  item.addEventListener("click", activateMenu);
});

async function logout() {
  try {
    // Make a GET request to the logout endpoint
    const response = await fetch("/logout", {
      // Remove trailing slash
      method: "GET",
      headers: {
        "Cache-Control": "no-cache",
        Pragma: "no-cache",
      },
      credentials: "same-origin", // Include credentials
    });

    if (response.ok) {
      // Clear all client-side storage
      localStorage.clear();
      sessionStorage.clear();

      // Clear cookies
      document.cookie.split(";").forEach(function (c) {
        document.cookie = c
          .replace(/^ +/, "")
          .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
      });

      // Force reload to clear any cached pages
      window.location.href = "/login";
    } else {
      console.error("Logout failed");
      window.location.href = "/login";
    }
  } catch (error) {
    console.error("Error during logout:", error);
    window.location.href = "/login";
  }
}

function searchCourse() {
  let input = document.getElementById("searchbar").value.toLowerCase();
  let courseCards = document.getElementsByClassName("course-card");

  for (let i = 0; i < courseCards.length; i++) {
    let h2 = courseCards[i].querySelector("h2");
    if (h2 && !h2.innerHTML.toLowerCase().includes(input)) {
      courseCards[i].style.display = "none";
    } else {
      courseCards[i].style.display = "list-item";
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const academicYearInput = document.getElementById("academic_year");
  if (academicYearInput) {
    academicYearInput.addEventListener("input", function (e) {
      let value = e.target.value.replace(/\D/g, ""); // Remove non-numeric characters
      if (value.length > 4) {
        value = value.slice(0, 4) + "/" + value.slice(4, 8); // Insert slash after the fourth digit
      }
      e.target.value = value;
    });
  }
});

let totalLecturers = 1;
let totalClasses = 1;

function addLecturerField() {
  // Remove the minus button from the previous field, if it exists
  if (totalLecturers > 1) {
    const previousButton = document.querySelector(
      `#lecturer-container div:last-child button`
    );
    if (previousButton) {
      previousButton.remove();
    }
  }

  totalLecturers++;
  const container = document.getElementById("lecturer-container");
  const newField = document.createElement("div");
  newField.setAttribute("id", `lecturer${totalLecturers}`);
  newField.innerHTML = `
      <div class="input-group">
          <label>Lecturer Name ${totalLecturers}: </label>
          <input id="lecturer_name${totalLecturers}" type="text" name="lecturer_name${totalLecturers}" placeholder="Enter lecturer name" required>
          <button type="button" onclick="removeLecturerField(${totalLecturers})">-</button>
      </div>
      <div class="input-group">
          <label>Lecturer Email ${totalLecturers}: </label>
          <input id="lecturer_email${totalLecturers}" type="text" name="lecturer_email${totalLecturers}" placeholder="Enter lecturer email" required>
      </div>
  `;
  container.appendChild(newField);
}

function removeLecturerField(id) {
  const field = document.getElementById(`lecturer${id}`);
  field.remove();
  totalLecturers--;

  // Add the minus button to the new last field, if there are still fields left
  if (totalLecturers > 1) {
    const lastField = document.querySelector(
      `#lecturer-container div:last-child`
    );
    if (lastField) {
      const newButton = document.createElement("button");
      newButton.type = "button";
      newButton.textContent = "-";
      newButton.setAttribute(
        "onclick",
        `removeLecturerField(${totalLecturers})`
      );
      lastField.appendChild(newButton);
    }
  }
}

function addVenueTimeField() {
  // Remove the minus button from the previous field, if it exists
  if (totalClasses > 1) {
    const previousButton = document.querySelector(
      `#venue-time-container div:last-child button`
    );
    if (previousButton) {
      previousButton.remove();
    }
  }

  totalClasses++;
  const container = document.getElementById("venue-time-container");
  const newField = document.createElement("div");
  newField.setAttribute("id", `venue_time${totalClasses}`);
  newField.innerHTML = `
      <div class="input-group">
          <label>Class Venue ${totalClasses}: </label>
          <input id="class_venue${totalClasses}" type="text" name="class_venue${totalClasses}" placeholder="Enter class venue" required>
          <button type="button" onclick="removeVenueTimeField(${totalClasses})">-</button>
      </div>
      <div class="input-group">
          <label>Class Day ${totalClasses}: </label>
          <select name="class_day${totalClasses}" id="class_day${totalClasses}" required>
              <option value="">Select day</option>
              <option value="Monday">Monday</option>
              <option value="Tuesday">Tuesday</option>
              <option value="Wednesday">Wednesday</option>
              <option value="Thursday">Thursday</option>
              <option value="Friday">Friday</option>
              <option value="Saturday">Saturday</option>
              <option value="Sunday">Sunday</option>
          </select>
      </div>
      <div class="input-group">
          <label>Class Start Time ${totalClasses}: </label>
          <input id="class_start_time${totalClasses}" type="time" name="class_start_time${totalClasses}" required>
      </div>
      <div class="input-group">
          <label>Class End Time ${totalClasses}: </label>
          <input id="class_end_time${totalClasses}" type="time" name="class_end_time${totalClasses}" required>
      </div>
  `;
  container.appendChild(newField);
}

function removeVenueTimeField(id) {
  const field = document.getElementById(`venue_time${id}`);
  field.remove();
  totalClasses--;

  // Add the minus button to the new last field, if there are still fields left
  if (totalClasses > 1) {
    const lastField = document.querySelector(
      `#venue-time-container div:last-child`
    );
    if (lastField) {
      const newButton = document.createElement("button");
      newButton.type = "button";
      newButton.textContent = "-";
      newButton.setAttribute(
        "onclick",
        `removeVenueTimeField(${totalClasses})`
      );
      lastField.appendChild(newButton);
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  var acc = document.getElementsByClassName("accordion");
  var i;

  for (i = 0; i < acc.length; i++) {
    acc[i].addEventListener("click", function () {
      this.classList.toggle("active");
      var panel = this.nextElementSibling;
      if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
      } else {
        panel.style.maxHeight = panel.scrollHeight + "px";
      }
    });
  }
});

let courseworkCount = 1;

function addCourseworkField() {
  //Remove the minus button from the previous field, if it exists
  if (courseworkCount > 1) {
    const previousButton = document.querySelector(
      `#coursework-container div:last-child button.remove-btn`
    );
    if (previousButton) {
      previousButton.remove();
    }
  }

  courseworkCount++;
  const container = document.getElementById("coursework-container");
  const newField = document.createElement("div");
  newField.setAttribute("id", `coursework${courseworkCount}`);
  newField.innerHTML = `
        <label>Coursework Type ${courseworkCount}: </label>
        <input type="text" id="coursework_type${courseworkCount}" 
               name="coursework_type${courseworkCount}" 
               placeholder="Enter coursework type" required>
        <br>
        <label>Total Mark ${courseworkCount}: </label>
        <input type="number" id="total_mark${courseworkCount}" 
               name="total_mark${courseworkCount}" 
               placeholder="Enter total mark" min="0" max="100" required>
        <button type="button" class="remove-btn" 
                onclick="removeCourseworkField(${courseworkCount})">-</button>
        <br>
    `;
  container.appendChild(newField);
}

function removeCourseworkField(id) {
  const field = document.getElementById(`coursework${id}`);
  field.remove();
  courseworkCount--;

  // Add the minus button to the new last field, if there are still fields left
  if (courseworkCount > 1) {
    const lastField = document.querySelector(
      `#coursework-container div:last-child`
    );
    if (lastField) {
      // Remove any existing remove button first
      const existingRemoveBtn = lastField.querySelector(".remove-btn");
      if (existingRemoveBtn) {
        existingRemoveBtn.remove();
      }
      const newButton = document.createElement("button");
      newButton.type = "button";
      newButton.textContent = "-";
      newButton.className = "remove-btn";
      newButton.setAttribute(
        "onclick",
        `removeCourseworkField(${courseworkCount})`
      );
      // Insert the button after the total mark input
      const totalMarkInput = lastField.querySelector(
        `input[name="total_mark${courseworkCount}"]`
      );
      if (totalMarkInput) {
        totalMarkInput.insertAdjacentElement("afterend", newButton);
      }
    }
  }
}

function openAnnouncement(
  title,
  content,
  author,
  timestamp,
  authorProfilePhoto
) {
  // Populate the form with the announcement details
  document.getElementById("form-title").innerText = title;
  document.getElementById("form-content").innerText = content;
  document.getElementById("form-author").innerText = "Author: " + author;
  document.getElementById("form-timestamp").innerText =
    "Timestamp: " + timestamp;
  document.getElementById("form-author-photo").src = authorProfilePhoto;

  // Show the form
  document.getElementById("announcement-form").style.display = "block";
}

// Add event listeners to menu items
document.addEventListener("DOMContentLoaded", () => {
  // Set the active menu item on page load
  updateActiveMenu();

  document.querySelectorAll(".menu-item, .logo-brand").forEach((item) => {
    item.addEventListener("click", activateMenu);
  });
});

function closePredictionModal() {
    const modal = document.getElementById('predictionResultsModal');
    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    
    // Remove modal-specific styles and classes
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
    document.body.classList.remove('modal-open');
    
    // Hide the modal
    bootstrapModal.hide();
}
