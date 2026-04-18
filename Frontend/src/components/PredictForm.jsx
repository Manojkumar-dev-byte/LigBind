import { useState } from "react";

function PredictForm({
	proteinSequence,
	setProteinSequence,
	topN,
	setTopN,
	candidateSmiles,
	setCandidateSmiles,
	loading,
	onSubmit,
}) {
	const [inputMode, setInputMode] = useState("protein");
	const [diseaseInput, setDiseaseInput] = useState("");

	return (
		<div className="control-panel">
			<h2>Target Selection</h2>

			<div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
				<button
					onClick={() => setInputMode("protein")}
					style={{
						padding: "8px 12px",
						backgroundColor: inputMode === "protein" ? "#06b6d4" : "#374151",
						color: "white",
						border: "none",
						borderRadius: "4px",
						cursor: "pointer",
						fontSize: "14px",
					}}
				>
					Protein Sequence
				</button>
				<button
					onClick={() => setInputMode("disease")}
					style={{
						padding: "8px 12px",
						backgroundColor: inputMode === "disease" ? "#06b6d4" : "#374151",
						color: "white",
						border: "none",
						borderRadius: "4px",
						cursor: "pointer",
						fontSize: "14px",
					}}
				>
					Disease Name
				</button>
			</div>

			{inputMode === "protein" ? (
				<>
					<label>Protein Sequence</label>
					<textarea
						value={proteinSequence}
						placeholder="Paste the amino acid sequence here (e.g., MKTFFVAGVILLLAALA...)"
						onChange={(event) => setProteinSequence(event.target.value)}
						style={{ minHeight: "170px" }}
					/>
				</>
			) : (
				<>
					<label>Disease Name</label>
					<textarea
						value={diseaseInput}
						placeholder="Enter disease name (e.g., cancer, diabetes, alzheimer, heart disease, etc.)"
						onChange={(event) => setDiseaseInput(event.target.value)}
						style={{ minHeight: "170px" }}
					/>
					<p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "8px" }}>
						Common diseases: cancer, diabetes, heart disease, alzheimer, inflammation, etc.
					</p>
				</>
			)}

			<label>Top N Drugs</label>
			<input
				type="number"
				min="1"
				max="100"
				value={topN}
				onChange={(event) => setTopN(Number(event.target.value) || 10)}
			/>

			<label>Optional Custom SMILES</label>
			<textarea
				value={candidateSmiles}
				placeholder="Paste SMILES strings separated by commas. Leave blank to use the Davis drug library."
				onChange={(event) => setCandidateSmiles(event.target.value)}
				style={{ minHeight: "110px" }}
			/>

			<button
				className="primary-btn"
				onClick={() => {
					if (inputMode === "disease" && diseaseInput) {
						setProteinSequence("");
						onSubmit(diseaseInput, inputMode);
					} else if (inputMode === "protein" && proteinSequence) {
						onSubmit(proteinSequence, inputMode);
					}
				}}
				disabled={loading || (!proteinSequence && !diseaseInput)}
			>
				{loading ? "Ranking candidates..." : "Rank Drug Candidates"}
			</button>

			<p className="subtext" style={{ textAlign: "left", marginTop: "8px" }}>
				The backend ranks the full candidate set and returns the complete sorted list.
			</p>
		</div>
	);
}

export default PredictForm;
