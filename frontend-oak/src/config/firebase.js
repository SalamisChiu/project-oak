// Import Firebase functions
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCdjUq-2PMuUGE5dzHKJlbza3AX2jeUfSc",
  authDomain: "fulleroak1215-e4b09.firebaseapp.com",
  projectId: "fulleroak1215-e4b09",
  storageBucket: "fulleroak1215-e4b09.firebasestorage.app",
  messagingSenderId: "1051335128467",
  appId: "1:1051335128467:web:63817cd7559e824e002466",
  measurementId: "G-TLWSBWYJP3"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and export it
export const auth = getAuth(app);
export default app;


