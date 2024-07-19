(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();

    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/firebase-messaging-sw.js')
        .then(function(registration) {
            console.log('Service Worker registered with scope:', registration.scope);
        }).catch(function(err) {
            console.log('Service Worker registration failed:', err);
        });
    }
    
// Inisialisasi Firebase
var firebaseConfig = {
    apiKey: "AIzaSyBay3ZbusFQelScGRnM7IHrr8C3MT-PWbA",
            authDomain: "glorysalon-6d464.firebaseapp.com",
            databaseURL: "https://glorysalon-6d464-default-rtdb.asia-southeast1.firebasedatabase.app",
            projectId: "glorysalon-6d464",
            storageBucket: "glorysalon-6d464.appspot.com",
            messagingSenderId: "907021096187",
            appId: "1:907021096187:web:3923e0b0dd669afb9fcc5e",
            measurementId: "G-TKZK87J1PS"
};
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

function requestAndSaveToken() {
    messaging.requestPermission()
    .then(function() {
        console.log('Notification permission granted.');
        return messaging.getToken();
    })
    .then(function(token) {
        console.log('FCM Token:', token);
        // Kirim token ini ke server Anda untuk menyimpan atau menggunakannya untuk pengiriman notifikasi
        saveFcmToken(token);
    })
    .catch(function(err) {
        console.log('Unable to get permission to notify.', err);
    });
}

function saveFcmToken(token) {
    fetch('/save-fcm-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token for security
        },
        body: JSON.stringify({'fcm_token': token})
    })
    .then(response => response.json())
    .then(data => {
        console.log('Token saved successfully:', data);
    })
    .catch((error) => {
        console.error('Error saving token:', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Panggil fungsi requestAndSaveToken setelah user berhasil login
document.addEventListener('DOMContentLoaded', function() {
    if (userJustLoggedIn) {
        requestAndSaveToken();
    }
});


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.sticky-top').addClass('shadow-sm').css('top', '0px');
        } else {
            $('.sticky-top').removeClass('shadow-sm').css('top', '-100px');
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Testimonials carousel
    $('.testimonial-carousel').owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        loop: true,
        nav: false,
        dots: true,
        items: 1,
        dotsData: true,
    });

    
})(jQuery);

