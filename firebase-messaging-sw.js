importScripts('https://www.gstatic.com/firebasejs/8.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.6.1/firebase-messaging.js');

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

messaging.onBackgroundMessage((payload) => {
    console.log('Received background message ', payload);
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: payload.notification.icon
    };

    self.registration.showNotification(notificationTitle,
        notificationOptions);
});
