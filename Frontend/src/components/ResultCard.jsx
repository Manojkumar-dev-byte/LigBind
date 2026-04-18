function ResultCard({ rankings, topN, onDownloadCsv }) {
	if (!rankings || rankings.length === 0) {
		return (
			<div className="leaderboard-panel">
				<div className="panel-head">
					<h2>Ranked Drug Candidates</h2>
					<span>Waiting for a protein sequence</span>
				</div>
				<p className="subtext" style={{ textAlign: "left" }}>
					Run the model to see the ranked drug list and export it as CSV.
				</p>
			</div>
		);
	}

	const topResults = rankings.slice(0, topN);
	const comparisonLimit = Math.min(topResults.length, 10);
	const comparisonData = topResults.slice(0, comparisonLimit);
	const affinityValues = comparisonData.map((item) => item.predicted_affinity);
	const bestAffinity = Math.min(...affinityValues);
	const worstAffinity = Math.max(...affinityValues);
	const affinityRange = Math.max(worstAffinity - bestAffinity, 0);

	return (
		<div className="leaderboard-panel">
			<div className="panel-head">
				<h2>Ranked Drug Candidates</h2>
				<div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
					<span>{rankings.length} candidates</span>
					<button className="dock-btn" onClick={onDownloadCsv} style={{ width: "auto", marginTop: 0 }}>
						Export CSV
					</button>
				</div>
			</div>

			<div className="manual-box" style={{ marginTop: 0 }}>
				<h3>Top {topN} Drugs</h3>
				{topResults.map((item) => (
					<div className="manual-card" key={item.rank}>
						<div style={{ display: "flex", justifyContent: "space-between", gap: "12px" }}>
							<div>
								<div className="score-label">Rank #{item.rank}</div>
								<div style={{ marginTop: "8px", wordBreak: "break-word" }}>
									<strong>{item.drug_name || `Drug ${item.drug_index}`}</strong>
									<div style={{ color: "#94a3b8", fontSize: "12px", marginTop: "4px" }}>
										{item.smiles}
									</div>
								</div>
							</div>
							<div style={{ textAlign: "right" }}>
								<div className="score-value">{item.predicted_affinity.toFixed(4)}</div>
								<div style={{ color: "#94a3b8", fontSize: "12px" }}>Predicted affinity</div>
							</div>
						</div>


					</div>
				))}
			</div>

			<div className="manual-box" style={{ marginTop: "18px" }}>
				<h3>Affinity Comparison (Top {comparisonLimit})</h3>
				{comparisonData.map((item) => {
					const barPercent = affinityRange === 0
						? 100
						: ((worstAffinity - item.predicted_affinity) / affinityRange) * 100;

					return (
						<div key={`cmp-${item.rank}`} style={{ marginBottom: "12px" }}>
							<div style={{ display: "flex", justifyContent: "space-between", gap: "10px", marginBottom: "6px" }}>
								<span style={{ color: "#cbd5e1", fontSize: "13px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
									#{item.rank} {item.drug_name || `Drug ${item.drug_index}`}
								</span>
								<span style={{ color: "#00e5ff", fontSize: "13px", fontWeight: 700 }}>
									{item.predicted_affinity.toFixed(4)}
								</span>
							</div>
							<div className="bar-wrap">
								<div className="bar-fill" style={{ width: `${Math.max(8, Math.min(100, barPercent))}%` }}></div>
							</div>
						</div>
					);
				})}
			</div>

			<div style={{ marginTop: "18px", maxHeight: "560px", overflowY: "auto" }}>
				<div className="table-head" style={{ position: "sticky", top: 0, background: "#111827", zIndex: 1 }}>
					<span>Rank</span>
					<span>Drug</span>
					<span>Affinity</span>
					<span>SMILES</span>
				</div>

				{rankings.map((item) => (
					<div className="result-row" key={item.rank} style={{ gridTemplateColumns: "80px 120px 120px 1fr" }}>
						<span className="rank">#{item.rank}</span>
						<span>{item.drug_name || `Drug ${item.drug_index}`}</span>
						<span>{item.predicted_affinity.toFixed(4)}</span>
						<span style={{ wordBreak: "break-word", color: "#94a3b8" }}>{item.smiles}</span>
					</div>
				))}
			</div>
		</div>
	);
}

export default ResultCard;
