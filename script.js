// Function to show/hide translation
function showTranslation(lessonId) {
    const translation = document.getElementById('translation' + lessonId);
    if (translation.style.display === 'none') {
        translation.style.display = 'block';
    } else {
        translation.style.display = 'none';
    }
}

// Add event listeners if needed
document.addEventListener('DOMContentLoaded', function() {
    // Any initialization code here
    console.log('NCE Learning Platform loaded');
});