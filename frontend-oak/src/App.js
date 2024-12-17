import React, { useState, useEffect } from "react";
import GoogleLogin from "./components/GoogleLogin";
import ShortUrlApp from "./components/ShortUrlApp";

function App() {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState("");

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
        <div>
            {!user ? (
                <GoogleLogin onSuccess={handleLoginSuccess} />
            ) : (
                <ShortUrlApp token={token} onLogout={handleLogout} />
            )}
        </div>
    );
}

export default App;