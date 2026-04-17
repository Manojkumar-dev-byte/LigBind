import { useState, useEffect } from "react";
import axios from "axios";

function Dashboard() {
  const [disease, setDisease] = useState("");
  const [drugs, setDrugs] = useState("");
  const [results, setResults] = useState([]);
  const [manualResults, setManualResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Auto scale for normal 100% browser zoom
  const [scale, setScale] = useState(1);

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

  const predictTop10 = async () => {
    if (!disease.trim()) return alert("Enter disease name");

    try {
      setLoading(true);
      const res = await axios.get(
        `http://127.0.0.1:8000/predict/top10/${disease}`
      );
      setResults(res.data.top_drugs);
    } catch {
      alert("Failed to fetch results");
    } finally {
      setLoading(false);
    }
  };

  const predictAffinity = async () => {
    if (!disease.trim()) return alert("Enter disease");
    if (!drugs.trim()) return alert("Enter drugs");

    try {
      setLoading(true);

      const drugList = drugs
        .split(",")
        .map((d) => d.trim())
        .filter((d) => d !== "");

      const res = await axios.post(
        "http://127.0.0.1:8000/predict/",
        { disease, drugs: drugList }
      );

      setManualResults(res.data.rankings);
    } catch {
      alert("Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const runDocking = (drug) => {
    window.location.href = `/docking?drug=${drug}&disease=${disease}`;
  };

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  const top3 = results.slice(0, 3);

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
      {/* FIT TO 100% SCREEN */}
      <div
        style={{
          width: "100%",
          maxWidth: "1700px",
          transform: `scale(${scale})`,
          transformOrigin: "top center",
        }}
      >
        {/* TOPBAR */}
        <div className="dashboard-topbar">
          <div>
            <h1>LigBind Discovery</h1>
            <p>AI Powered Drug Candidate Ranking Platform</p>
          </div>

          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>

        {/* MAIN */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "390px 1fr",
            gap: "18px",
            alignItems: "start",
          }}
        >
          {/* LEFT */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "16px",
            }}
          >
            <div className="control-panel">
              <h2>Target Selection</h2>

              <label>Disease Name</label>
              <input
                type="text"
                value={disease}
                placeholder="Lung Cancer / Diabetes"
                onChange={(e) => setDisease(e.target.value)}
              />

              <label>Drug Names (Optional)</label>
              <textarea
                value={drugs}
                placeholder="Gefitinib, Erlotinib"
                onChange={(e) => setDrugs(e.target.value)}
                style={{ minHeight: "95px" }}
              />

              <button
                className="primary-btn"
                onClick={predictTop10}
                style={{ marginBottom: "10px" }}
              >
                {loading ? "Analyzing..." : "View Top 10 Drugs"}
              </button>

              <button
                className="secondary-btn"
                onClick={predictAffinity}
              >
                Predict Affinity Score
              </button>
            </div>

            {manualResults.length > 0 && (
              <div className="leaderboard-panel">
                <div className="panel-head">
                  <h2>User Input Drug Ranking</h2>
                  <span>{manualResults.length} Results</span>
                </div>

                {manualResults.map((item, index) => (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "50px 1fr 70px 105px",
                      gap: "8px",
                      alignItems: "center",
                      padding: "12px 0",
                      borderBottom:
                        "1px solid rgba(255,255,255,0.06)",
                    }}
                    key={index}
                  >
                    <span className="rank">#{index + 1}</span>

                    <div className="drug-cell">
                      <strong>{item.drug}</strong>
                      <small>User Candidate</small>
                    </div>

                    <span>{item.score}</span>

                    <button
                      className="dock-btn"
                      style={{
                        fontSize: "11px",
                        padding: "8px",
                        width: "100%",
                      }}
                      onClick={() => runDocking(item.drug)}
                    >
                      Docking
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* RIGHT */}
          <div className="leaderboard-panel">
            <div className="panel-head">
              <h2>Top 10 Recommended Drugs</h2>
              <span>{results.length} Results</span>
            </div>

            <div className="table-head">
              <span>Rank</span>
              <span>Drug Candidate</span>
              <span>Affinity</span>
              <span>Binding %</span>
              <span>Action</span>
            </div>

            {results.map((item, index) => {
              const percent = Math.max(100 - index * 2, 82);

              return (
                <div className="result-row" key={index}>
                  <span className="rank">#{index + 1}</span>

                  <div className="drug-cell">
                    <strong>{item.drug}</strong>
                    <small>AI Suggested Candidate</small>
                  </div>

                  <span>{item.score}</span>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      minWidth: "150px",
                    }}
                  >
                    <div
                      style={{
                        width: "100px",
                        height: "8px",
                        borderRadius: "20px",
                        background: "#1c2433",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${percent}%`,
                          height: "100%",
                          background:
                            "linear-gradient(90deg,#3b82f6,#06b6d4)",
                        }}
                      />
                    </div>

                    <small
                      style={{
                        color: "#00e5ff",
                        fontWeight: "600",
                      }}
                    >
                      {percent}%
                    </small>
                  </div>

                  <button
                    className="dock-btn"
                    onClick={() => runDocking(item.drug)}
                  >
                    Docking
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* TOP PICKS */}
        {top3.length > 0 && (
          <div
            className="top-picks"
            style={{
              marginTop: "20px",
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(240px,1fr))",
              gap: "14px",
            }}
          >
            {top3.map((item, index) => (
              <div className="pick-card" key={index}>
                <p>
                  {index === 0
                    ? "🥇 Champion"
                    : index === 1
                    ? "🥈 Runner Up"
                    : "🥉 Third Best"}
                </p>

                <h3>{item.drug}</h3>
                <h2>{item.score}</h2>

                <button
                  className="dock-btn"
                  onClick={() => runDocking(item.drug)}
                >
                  Docking
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;