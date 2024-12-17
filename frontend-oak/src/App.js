import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GoogleLogin from "./components/GoogleLogin";
import ShortUrlApp from "./components/ShortUrlApp";

function App() {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState("");
    console.log("API BASE URL:", process.env.REACT_APP_API_BASE_URL);
    // 初始化時檢查 localStorage
    useEffect(() => {
        const storedUser = localStorage.getItem("user");
        const storedToken = localStorage.getItem("token");

        if (storedUser && storedToken) {
            setUser(JSON.parse(storedUser));
            setToken(storedToken);
        }
    }, []);

    const handleLoginSuccess = (userInfo, idToken) => {
        setUser(userInfo);
        setToken(idToken);

        // 儲存到 localStorage
        localStorage.setItem("user", JSON.stringify(userInfo));
        localStorage.setItem("token", idToken);
    };

    const handleLogout = () => {
        setUser(null);
        setToken("");

        // 清除 localStorage
        localStorage.removeItem("user");
        localStorage.removeItem("token");
    };

    return (
        <BrowserRouter>  {/* 添加這個包裹 */}
            <div>
                {!user ? (
                    <GoogleLogin onSuccess={handleLoginSuccess} />
                ) : (
                    <ShortUrlApp token={token} onLogout={handleLogout} />
                )}
            </div>
        </BrowserRouter>
    );
}

export default App;