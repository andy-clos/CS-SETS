// Logout function to clear sessionStorage and redirect to login page

function logout() {
    sessionStorage.removeItem('userEmail'); // Clear sessionStorage
    window.location.href = '../login'; // Redirect to login page
}