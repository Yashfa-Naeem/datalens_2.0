import { useState, useRef } from "react";
import axios from "axios";

export default function UploadSection({ onUploadSuccess }) {
    const [dragging, setDragging] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const inputRef = useRef();

    const handleFile = async (file) => {
        if (!file) return;
        if (!file.name.endsWith(".csv")) { setError("Please upload a CSV file."); return; }
        if (file.size > 50 * 1024 * 1024) { setError("File too large (max 50MB)."); return; }
        setError(""); setLoading(true);
        const form = new FormData();
        form.append("file", file);
        try {
            const res = await axios.post("http://localhost:8000/api/upload", form);
            onUploadSuccess(res.data.dataset_id, file.name);
        } catch (e) {
            setError(e.response?.data?.detail || "Upload failed. Make sure the backend is running.");
        } finally { setLoading(false); }
    };

    return (
        <div className="upload-wrapper">
            <div
                className={`upload-box${dragging ? " dragging" : ""}`}
                onClick={() => inputRef.current.click()}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
            >
                <div className="upload-icon">📂</div>
                <div className="upload-title">Drop your CSV here</div>
                <div className="upload-sub">or click to browse — max 50MB</div>
                <button className="upload-btn" onClick={(e) => { e.stopPropagation(); inputRef.current.click(); }}>
                    Choose File
                </button>
                <input ref={inputRef} type="file" accept=".csv" style={{ display: "none" }}
                    onChange={(e) => handleFile(e.target.files[0])} />
            </div>
            {error && <div className="error-msg">⚠ {error}</div>}
            {loading && <div className="loading-msg">⏳ Uploading and profiling data...</div>}
        </div>
    );
}