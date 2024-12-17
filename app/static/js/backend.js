
function activateMenu(event) {
  const menuItems = document.querySelectorAll('.menu-item');
  menuItems.forEach(item => item.classList.remove('active'));

  if (event.currentTarget.classList.contains('logo-brand')) {
    const dashboardMenuItem = document.querySelector('.menu-item[href="/dashboard"]');
    if (dashboardMenuItem) {
      dashboardMenuItem.classList.add('active');
    }
    localStorage.setItem('activeLink', '/dashboard');
  } 
  else if (event.currentTarget.classList.contains('menu-item')) {
    event.currentTarget.classList.add('active');
    const activeLink = event.currentTarget.getAttribute('href');
    localStorage.setItem('activeLink', activeLink);
  }
}

function setDefaultActiveMenu() {
  const dashboardItem = document.querySelector('.menu-item[href="/dashboard"]');
  if (dashboardItem) {
    dashboardItem.classList.add('active');
  }
}

const storedActiveLink = localStorage.getItem('activeLink');
if (storedActiveLink) {
  const menuItems = document.querySelectorAll('.menu-item');
  menuItems.forEach(item => {
    if (item.getAttribute('href') === storedActiveLink) {
      item.classList.add('active');
    }
  });
} else {
  setDefaultActiveMenu();
}

const logoBrand = document.querySelector('.logo-brand');
if (logoBrand) {
  logoBrand.addEventListener('click', activateMenu);
}

const menuItems = document.querySelectorAll('.menu-item');
menuItems.forEach(item => {
  item.addEventListener('click', activateMenu);
});

function logout() {
  localStorage.removeItem('activeLink');
  setDefaultActiveMenu();
  sessionStorage.removeItem('userEmail');
  window.location.href = '../login';
}

function searchCourse() {
  let input = document.getElementById('searchbar').value.toLowerCase();
  let courseCards = document.getElementsByClassName('course-card');

  for (let i = 0; i < courseCards.length; i++) {
      let h2 = courseCards[i].querySelector('h2');
      if (h2 && !h2.innerHTML.toLowerCase().includes(input)) {
          courseCards[i].style.display = "none";
      } else {
          courseCards[i].style.display = "list-item";
      }
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const academicYearInput = document.getElementById('academic_year');
  if (academicYearInput) {
      academicYearInput.addEventListener('input', function (e) {
          let value = e.target.value.replace(/\D/g, ''); // Remove non-numeric characters
          if (value.length > 4) {
              value = value.slice(0, 4) + '/' + value.slice(4, 8); // Insert slash after the fourth digit
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
      const previousButton = document.querySelector(`#lecturer-container div:last-child button`);
      if (previousButton) {
          previousButton.remove();
      }
  }

  totalLecturers++;
  const container = document.getElementById('lecturer-container');
  const newField = document.createElement('div');
  newField.setAttribute('id', `lecturer${totalLecturers}`);
  newField.innerHTML = `
      <label>Lecturer Name ${totalLecturers}: </label>
      <input id="lecturer_name${totalLecturers}" type="text" name="lecturer_name${totalLecturers}" placeholder="Enter lecturer name" required>
      <br>
      <label>Lecturer Email ${totalLecturers}: </label>
      <input id="lecturer_email${totalLecturers}" type="text" name="lecturer_email${totalLecturers}" placeholder="Enter lecturer email" required>
      <button type="button" onclick="removeLecturerField(${totalLecturers})">-</button>
  `;
  container.appendChild(newField);
}

function removeLecturerField(id) {
  const field = document.getElementById(`lecturer${id}`);
  field.remove();
  totalLecturers--;

  // Add the minus button to the new last field, if there are still fields left
  if (totalLecturers > 1) {
      const lastField = document.querySelector(`#lecturer-container div:last-child`);
      if (lastField) {
          const newButton = document.createElement('button');
          newButton.type = 'button';
          newButton.textContent = '-';
          newButton.setAttribute('onclick', `removeLecturerField(${totalLecturers})`);
          lastField.appendChild(newButton);
      }
  }
}

function addVenueTimeField() {
// Remove the minus button from the previous field, if it exists
  if (totalClasses > 1) {
      const previousButton = document.querySelector(`#venue-time-container div:last-child button`);
      if (previousButton) {
          previousButton.remove();
      }
  }

  totalClasses++;
  const container = document.getElementById('venue-time-container');
  const newField = document.createElement('div');
  newField.setAttribute('id', `venue_time${totalClasses}`);
  newField.innerHTML = `
      <label>Class Venue ${totalClasses}: </label>
      <input id="class_venue${totalClasses}" type="text" name="class_venue${totalClasses}" placeholder="Enter class venue" required>
      <br>
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
      <br>
      <label>Class Start Time ${totalClasses}: </label>
      <input id="class_start_time${totalClasses}" type="time" name="class_start_time${totalClasses}" required>
      <br>
      <label>Class End Time ${totalClasses}: </label>
      <input id="class_end_time${totalClasses}" type="time" name="class_end_time${totalClasses}" required>
      <button type="button" onclick="removeVenueTimeField(${totalClasses})">-</button>
  `;
  container.appendChild(newField);
}

function removeVenueTimeField(id) {
  const field = document.getElementById(`venue_time${id}`);
  field.remove();
  totalClasses--;

    // Add the minus button to the new last field, if there are still fields left
    if (totalClasses > 1) {
        const lastField = document.querySelector(`#venue-time-container div:last-child`);
        if (lastField) {
            const newButton = document.createElement('button');
            newButton.type = 'button';
            newButton.textContent = '-';
            newButton.setAttribute('onclick', `removeVenueTimeField(${totalClasses})`);
            lastField.appendChild(newButton);
        }
    }
}

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    } 
  });
}
