import ChatPanel from "./ChatPanel";
import ExecutiveSummary from "./ExecutiveSummary";
import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#38bdf8", "#818cf8", "#34d399", "#f87171", "#fbbf24", "#e879f9"];
const API = "http://localhost:8000/api";

export default function Dashboard({ datasetId, datasetName, onReset }) {
    const [profile, setProfile] = useState(null);
    const [charts, setCharts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get(API + "/profile/" + datasetId).then(r => {
            setProfile(r.data);
            const catCols = r.data.categorical_cols || [];
            const cols = catCols.slice(0, 4);
            Promise.all(cols.map(col =>
                axios.get(API + "/aggregate", { params: { dataset_id: datasetId, groupby: col } })
                    .then(res => ({ col, data: res.data }))
                    .catch(() => null)
            )).then(results => { setCharts(results.filter(Boolean)); setLoading(false); });
        }).catch(console.error);
    }, [datasetId]);

    return (
        <div>
            <div className="dashboard-header">
                <div>
                    <div className="dataset-title">DataLens - {datasetName}</div>
                    <div className="dataset-sub">{profile ? profile.row_count + " rows, " + profile.column_count + " columns" : "Loading..."}</div>
                </div>
                <button className="reset-btn" onClick={onReset}>Upload New File</button>
            </div>
            {loading ? <div className="loading-chart">Loading charts...</div> : (
                <div className="charts-grid">
                    {charts.map(({ col, data }, i) => (
                        <div className="chart-card" key={col}>
                            <div className="chart-title">{col} Distribution</div>
                            <ResponsiveContainer width="100%" height={280}>
                                {i % 2 === 0 ? (
                                    <BarChart data={data.slice(0, 10)}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                        <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} />
                                        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                                        <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
                                        <Bar dataKey="value" fill={COLORS[i % COLORS.length]} radius={[4,4,0,0]} />
                                    </BarChart>
                                ) : (
                                    <PieChart>
                                        <Pie data={data.slice(0, 8)} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                                            {data.slice(0,8).map((_, j) => <Cell key={j} fill={COLORS[j % COLORS.length]} />)}
                                        </Pie>
                                        <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
                                        <Legend />
                                    </PieChart>
                                )}
                            </ResponsiveContainer>
                        </div>
                    ))}
                </div>
            )}
            <ChatPanel datasetId={datasetId} />
            <ExecutiveSummary datasetId={datasetId} />
        </div>
    );
}
