import { useEffect, useState } from "react";

import PredictForm from "../components/PredictForm";
import ResultCard from "../components/ResultCard";
import { downloadRankingsCsv, rankProteinTarget } from "../services/api";

function Dashboard() {
  const [proteinSequence, setProteinSequence] = useState("");
  const [topN, setTopN] = useState(10);
  const [candidateSmiles, setCandidateSmiles] = useState("");
  const [rankings, setRankings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scale, setScale] = useState(1);

  const comparisonRows = rankings.slice(0, Math.min(5, rankings.length));
  const comparisonAffinities = comparisonRows.map((item) => item.predicted_affinity);
  const comparisonBest = comparisonAffinities.length ? Math.min(...comparisonAffinities) : 0;
  const comparisonWorst = comparisonAffinities.length ? Math.max(...comparisonAffinities) : 0;
  const comparisonRange = Math.max(comparisonWorst - comparisonBest, 0);

  const pieData = (() => {
    const values = rankings.slice(0, Math.min(topN, rankings.length)).map((item) => item.predicted_affinity);
    if (!values.length) {
      return { best: 0, middle: 0, lower: 0 };
    }

    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue;
    if (range === 0) {
      return { best: values.length, middle: 0, lower: 0 };
    }

    const edge1 = minValue + range / 3;
    const edge2 = minValue + (2 * range) / 3;
    let best = 0;
    let middle = 0;
    let lower = 0;

    values.forEach((value) => {
      if (value <= edge1) {
        best += 1;
      } else if (value <= edge2) {
        middle += 1;
      } else {
        lower += 1;
      }
    });

    return { best, middle, lower };
  })();

  const pieTotal = pieData.best + pieData.middle + pieData.lower;
  const pieBestPct = pieTotal ? (pieData.best / pieTotal) * 100 : 0;
  const pieMiddlePct = pieTotal ? (pieData.middle / pieTotal) * 100 : 0;
  const pieLowerPct = pieTotal ? (pieData.lower / pieTotal) * 100 : 0;

  useEffect(() => {
    const updateScale = () => {
      const width = window.innerWidth;

      if (width >= 1800) setScale(0.88);
      else if (width >= 1600) setScale(0.92);
      else if (width >= 1450) setScale(0.96);
      else if (width >= 1300) setScale(1);
      else if (width >= 1150) setScale(0.95);
      else setScale(0.9);
    };

    updateScale();
    window.addEventListener("resize", updateScale);
    return () => window.removeEventListener("resize", updateScale);
  }, []);

  const buildPayload = (inputValue, inputMode) => {
    const smilesList = candidateSmiles
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    const payload = {
      top_n: topN,
    };

    if (inputMode === "disease") {
      payload.disease_name = inputValue.trim();
    } else {
      payload.protein_sequence = inputValue.trim();
    }

    if (smilesList.length > 0) {
      payload.candidate_smiles = smilesList;
    }

    return payload;
  };

  const predictRankings = async (inputValue, inputMode) => {
    if (!inputValue || !inputValue.trim()) {
      alert(`Enter a ${inputMode === "disease" ? "disease name" : "protein sequence"}`);
      return;
    }

    try {
      setLoading(true);
      const response = await rankProteinTarget(buildPayload(inputValue, inputMode));
      setRankings(response.rankings || []);
      setSummary(response);
    } catch (error) {
      const message = error?.response?.data?.detail || "Failed to fetch results";
      alert(message);
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = async () => {
    if (!summary && !proteinSequence.trim()) {
      alert("First run ranking, then export CSV");
      return;
    }

    try {
      setLoading(true);
      const payload = {
        top_n: topN,
      };
      if (summary?.protein_sequence) {
        payload.protein_sequence = summary.protein_sequence;
      } else if (proteinSequence.trim()) {
        payload.protein_sequence = proteinSequence.trim();
      }
      const smilesList = candidateSmiles
        .split(",")
        .map((item) => item.trim())
        .filter((item) => item.length > 0);
      if (smilesList.length > 0) {
        payload.candidate_smiles = smilesList;
      }
      
      const blob = await downloadRankingsCsv(payload);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ligbind_rankings.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      const message = error?.response?.data?.detail || "CSV export failed";
      alert(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="dashboard-shell"
      style={{
        width: "100%",
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        padding: "14px",
        boxSizing: "border-box",
        overflowX: "hidden",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "1700px",
          transform: `scale(${scale})`,
          transformOrigin: "top center",
        }}
      >
        <div className="dashboard-topbar">
          <div>
            <h1>LigBind Discovery</h1>
            <p>Protein-sequence driven drug ranking and export</p>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "390px 1fr",
            gap: "18px",
            alignItems: "start",
          }}
        >
          <div className="left-column-stack">
            <PredictForm
              proteinSequence={proteinSequence}
              setProteinSequence={setProteinSequence}
              topN={topN}
              setTopN={setTopN}
              candidateSmiles={candidateSmiles}
              setCandidateSmiles={setCandidateSmiles}
              loading={loading}
              onSubmit={predictRankings}
            />

            <div className="left-analytics-card">
              <h3>Quick Comparison</h3>
              {!comparisonRows.length ? (
                <p className="subtext" style={{ textAlign: "left", marginBottom: 0 }}>
                  Run ranking to see bar and pie comparison.
                </p>
              ) : (
                <>
                  <div>
                    {comparisonRows.map((item) => {
                      const widthPct = comparisonRange === 0
                        ? 100
                        : ((comparisonWorst - item.predicted_affinity) / comparisonRange) * 100;

                      return (
                        <div key={`left-cmp-${item.rank}`} className="left-cmp-row">
                          <div className="left-cmp-head">
                            <span>#{item.rank} {item.drug_name || `Drug ${item.drug_index}`}</span>
                            <strong>{item.predicted_affinity.toFixed(4)}</strong>
                          </div>
                          <div className="bar-wrap">
                            <div className="bar-fill" style={{ width: `${Math.max(8, Math.min(100, widthPct))}%` }}></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="left-pie-layout">
                    <div
                      className="left-pie"
                      style={{
                        background: `conic-gradient(#00c896 0% ${pieBestPct}%, #00e5ff ${pieBestPct}% ${pieBestPct + pieMiddlePct}%, #334155 ${pieBestPct + pieMiddlePct}% 100%)`,
                      }}
                    ></div>
                    <div className="left-pie-legend">
                      <div><span className="dot best"></span>Best tier: {pieData.best}</div>
                      <div><span className="dot mid"></span>Middle tier: {pieData.middle}</div>
                      <div><span className="dot low"></span>Lower tier: {pieData.lower}</div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          <ResultCard
            rankings={rankings}
            topN={topN}
            onDownloadCsv={exportCsv}
          />
        </div>

        {summary && (
          <div style={{ marginTop: "18px", color: "#94a3b8" }}>
            Top affinity: <strong style={{ color: "white" }}>{summary.rankings?.[0]?.predicted_affinity?.toFixed(4)}</strong>
            {summary.rankings?.length ? ` | Total candidates ranked: ${summary.rankings.length}` : ""}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
