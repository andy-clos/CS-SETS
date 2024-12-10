
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