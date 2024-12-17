import React from "react";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "../config/firebase";
import { API_BASE_URL } from "../config/api";
import "bootstrap/dist/css/bootstrap.min.css";

const GoogleLogin = ({ onSuccess }) => {
    const handleGoogleLogin = async () => {
        const provider = new GoogleAuthProvider();
        try {
            const result = await signInWithPopup(auth, provider);
            const user = result.user;
            const idToken = await user.getIdToken();

            // 驗證 Token
            const response = await fetch(`${API_BASE_URL}/verify-token/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ token: idToken }),
            });

            if (response.ok) {
                // 儲存用戶資訊到 localStorage
                localStorage.setItem("user", JSON.stringify(user));
                localStorage.setItem("token", idToken);

                onSuccess(user, idToken);
            } else {
                console.error("Token verification failed");
            }
        } catch (error) {
            console.error("Login failed:", error.message);
        }
    };

    return (
        <div className="d-flex align-items-center justify-content-center" style={{ height: "100vh", backgroundColor: "#f8f9fa" }}>
            <div className="card shadow p-5 text-center" style={{ maxWidth: "400px", borderRadius: "10px" }}>
                <h2 className="mb-4" style={{ color: "#007bff", fontWeight: "bold" }}>
                    Welcome to URL Shortener
                </h2>
                <p className="mb-4 text-muted">Sign in with Google to start shortening URLs.</p>
                <button
                    onClick={handleGoogleLogin}
                    className="btn btn-primary d-flex align-items-center justify-content-center"
                    style={{
                        fontSize: "16px",
                        padding: "10px 20px",
                        borderRadius: "5px",
                        fontWeight: "bold",
                    }}
                >
                    <span style={{ marginRight: "8px" }}>&#x1F310;</span> {/* Unicode 地球圖示 */}
                    Login with Google
                </button>
            </div>
        </div>
    );
};

export default GoogleLogin;