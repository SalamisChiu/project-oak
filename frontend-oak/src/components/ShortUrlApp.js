import React, { useState } from "react";
import { API_BASE_URL } from "../config/api";
import "bootstrap/dist/css/bootstrap.min.css";

const ShortUrlApp = ({ token, onLogout }) => {
    const [originalUrl, setOriginalUrl] = useState("");
    const [shortUrl, setShortUrl] = useState("");
    const [stats, setStats] = useState(null);
    const [searchCode, setSearchCode] = useState("");
    const [error, setError] = useState("");

    // 生成短網址
    const handleShortenUrl = async () => {
        setError("");
        try {
            const response = await fetch(`${API_BASE_URL}/create/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ url: originalUrl }),
            });
            const data = await response.json();
            if (response.ok) {
                setShortUrl(data.short_url);
            } else {
                setError(data.error || "Failed to shorten URL");
            }
        } catch {
            setError("Network error occurred");
        }
    };

    // 查詢短網址統計數據
    const handleFetchStats = async (code) => {
        const shortCode = code || shortUrl.split("/").pop();
        setError("");
        try {
            const response = await fetch(`${API_BASE_URL}/${shortCode}/stats/`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            const data = await response.json();
            if (response.ok) {
                setStats(data);
            } else {
                setError(data.error || "Failed to fetch stats");
            }
        } catch {
            setError("Network error occurred");
        }
    };

    return (
        <div className="container mt-4">
            {/* 登出按鈕 */}
            <div className="d-flex justify-content-end">
                <button
                    onClick={onLogout}
                    className="btn btn-light text-danger d-flex align-items-center"
                    style={{ border: "1px solid #f8d7da" }}
                >
                    <span style={{ fontSize: "20px", marginRight: "5px" }}>↩</span> Logout
                </button>
            </div>

            {/* 標題 */}
            <h1 className="text-center mb-4">Short URL Generator</h1>

            {/* 生成短網址區塊 */}
            <div className="card p-4 mb-4 shadow-sm">
                <h5>Generate Short URL</h5>
                <div className="input-group mb-3">
                    <input
                        type="url"
                        className="form-control"
                        placeholder="Enter URL here..."
                        value={originalUrl}
                        onChange={(e) => setOriginalUrl(e.target.value)}
                    />
                    <button className="btn btn-primary" onClick={handleShortenUrl}>
                        Shorten
                    </button>
                </div>
                {shortUrl && (
                    <div className="alert alert-success d-flex justify-content-between">
                        <a href={shortUrl} target="_blank" rel="noopener noreferrer" className="text-success">
                            {shortUrl}
                        </a>
                        <button
                            className="btn btn-outline-secondary btn-sm"
                            onClick={() => navigator.clipboard.writeText(shortUrl)}
                        >
                            Copy
                        </button>
                        <button className="btn btn-info btn-sm" onClick={() => handleFetchStats(shortUrl.split("/").pop())}>
                            Fetch Stats
                        </button>
                    </div>
                )}
            </div>

            {/* 搜尋短碼區塊 */}
            <div className="card p-4 mb-4 shadow-sm">
                <h5>Search Short URL Stats</h5>
                <div className="input-group mb-3">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Enter short code..."
                        value={searchCode}
                        onChange={(e) => setSearchCode(e.target.value)}
                    />
                    <button
                        className="btn btn-info"
                        onClick={() => handleFetchStats(searchCode)}
                    >
                        Search
                    </button>
                </div>
            </div>

            {/* 統計數據展示 */}
            {stats && (
                <div className="card p-4 shadow-sm">
                    <h5>Statistics for: {stats.short_code}</h5>
                    <p><strong>Original URL:</strong> {stats.original_url}</p>
                    <p><strong>Click Count:</strong> {stats.click_count}</p>
                    <h6>Recent Clicks:</h6>
                    <ul className="list-group">
                        {stats.recent_clicks.map((click, index) => (
                            <li key={index} className="list-group-item">
                                <strong>IP:</strong> {click.ip_address} | <strong>Time:</strong> {click.clicked_at}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {error && <div className="alert alert-danger mt-3">{error}</div>}
        </div>
    );
};

export default ShortUrlApp;