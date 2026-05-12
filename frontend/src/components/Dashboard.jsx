import ChatPanel from "./ChatPanel";
import ExecutiveSummary from "./ExecutiveSummary";
import { useEffect, useState } from "react";
import axios from "axios";
import {
    BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";
import FilterPanel from "./FilterPanel";

const COLORS = ["#38bdf8", "#818cf8", "#34d399", "#f87171", "#fbbf24", "#e879f9", "#fb923c", "#a3e635"];
const API = "http://localhost:8000/api";

export default function Dashboard({ datasetId, datasetName, onReset }) {
    const [profile, setProfile] = useState(null);
    const [charts, setCharts] = useState({});
    const [filters, setFilters] = useState({ airline: "", year: "" });
    const [loading, setLoading] = useState(true);

    // Load profile once
    useEffect(() => {
        axios.get(`${API}/profile/${datasetId}`).then(r => setProfile(r.data)).catch(console.error);
    }, [datasetId]);

    // Load chart data when filters change
    useEffect(() => {
        setLoading(true);
        const params = { dataset_id: datasetId, ...filters };
        Promise.all([
            axios.get(`${API}/aggregate`, { params: { ...params, groupby: "airline" } }),
            axios.get(`${API}/aggregate`, { params: { ...params, groupby: "month" } }),
            axios.get(`${API}/aggregate`, { params: { ...params, groupby: "cancellation" } }),
            axios.get(`${API}/aggregate`, { params: { ...params, groupby: "airport" } }),
        ]).then(([airline, month, cancel, airport]) => {
            setCharts({
                airline: airline.data,
                month: month.data,
                cancellation: cancel.data,
                airport: airport.data,
            });
        }).catch(console.error).finally(() => setLoading(false));
    }, [datasetId, filters]);

    const airlines = profile?.airlines || [];
    const years = profile?.years || [];

    return (
        <div>
            <div className="dashboard-header">
                <div>
                    <div className="dataset-title">📊 {datasetName}</div>
                    <div className="dataset-sub">
                        {profile ? `${profile.total_rows?.toLocaleString()} rows · ${profile.total_columns} columns` : "Loading profile..."}
                    </div>
                </div>
                <button className="reset-btn" onClick={onReset}>↑ Upload New File</button>
            </div>

            <FilterPanel
                airlines={airlines} years={years}
                filters={filters} onChange={setFilters}
                onClear={() => setFilters({ airline: "", year: "" })}
            />

            {loading ? (
                <div className="loading-chart">Loading charts...</div>
            ) : (
                <div className="charts-grid">

                    {/* Bar: Avg Delay by Airline */}
                    <div className="chart-card">
                        <div className="chart-title">Average Departure Delay by Airline (min)</div>
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={charts.airline?.slice(0, 10)}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} />
                                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
                                <Bar dataKey="avg_delay" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Line: Delays by Month */}
                    <div className="chart-card">
                        <div className="chart-title">Average Delay by Month</div>
                        <ResponsiveContainer width="100%" height={280}>
                            <LineChart data={charts.month}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} />
                                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
                                <Line type="monotone" dataKey="avg_delay" stroke="#818cf8" strokeWidth={2} dot={{ fill: "#818cf8" }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Pie: Cancellation Rate */}
                    <div className="chart-card">
                        <div className="chart-title">Flight Status Breakdown</div>
                        <ResponsiveContainer width="100%" height={280}>
                            <PieChart>
                                <Pie data={charts.cancellation} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                                    {charts.cancellation?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Bar: Top Airports by Delay */}
                    <div className="chart-card">
                        <div className="chart-title">Top 10 Airports by Avg Delay</div>
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={charts.airport?.slice(0, 10)} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} />
                                <YAxis dataKey="name" type="category" tick={{ fill: "#64748b", fontSize: 11 }} width={60} />
                                <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e293b" }} />
                                <Bar dataKey="avg_delay" fill="#34d399" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                </div>
            )}
        
        <ChatPanel datasetId={datasetId} />
        <ExecutiveSummary datasetId={datasetId} />
        </div>
    );
}
