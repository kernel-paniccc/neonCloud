document.addEventListener('DOMContentLoaded', function() {
            var popup = document.getElementById('popup');
            popup.style.display = 'block';
            setTimeout(function() {
                popup.style.display = 'none';
            }, 2000);
        });