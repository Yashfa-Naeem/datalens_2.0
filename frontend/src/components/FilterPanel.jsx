export default function FilterPanel({ airlines, years, filters, onChange, onClear }) {
    return (
        <div className="filter-panel">
            <div className="filter-group">
                <label className="filter-label">Airline</label>
                <select className="filter-select" value={filters.airline}
                    onChange={(e) => onChange({ ...filters, airline: e.target.value })}>
                    <option value="">All Airlines</option>
                    {airlines.map((a) => <option key={a} value={a}>{a}</option>)}
                </select>
            </div>

            <div className="filter-group">
                <label className="filter-label">Year</label>
                <select className="filter-select" value={filters.year}
                    onChange={(e) => onChange({ ...filters, year: e.target.value })}>
                    <option value="">All Years</option>
                    {years.map((y) => <option key={y} value={y}>{y}</option>)}
                </select>
            </div>

            <button className="clear-btn" onClick={onClear}>✕ Clear Filters</button>
        </div>
    );
}