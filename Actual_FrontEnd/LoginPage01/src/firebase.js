import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAcSZArRVa3ltZA_yy4JFedDBBuDHpc6Gs",
  authDomain: "shadowuserauth.firebaseapp.com",
  projectId: "shadowuserauth",
  storageBucket: "shadowuserauth.firebasestorage.app",
  messagingSenderId: "667604545136",
  appId: "1:667604545136:web:a72e0d323974c36b638eb5"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
