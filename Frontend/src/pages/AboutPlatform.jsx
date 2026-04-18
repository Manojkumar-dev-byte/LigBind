import { useNavigate } from "react-router-dom";

function AboutPlatform() {
  const navigate = useNavigate();

  return (
    <div className="detail-shell">
      <header className="detail-topbar">
        <button className="detail-back" onClick={() => navigate("/")}>Back to Home</button>
        <button className="detail-primary" onClick={() => navigate("/dashboard")}>Start Discovery</button>
      </header>

      <section className="detail-hero">
        <span className="detail-badge">About This Platform</span>
        <h1>LigBind: AI-Powered Drug Candidate Prioritization</h1>
        <p>
          LigBind is an end-to-end platform that transforms a biological target into a ranked,
          experiment-ready drug candidate list using protein-aware affinity prediction.
        </p>
      </section>

      <section className="detail-grid">
        <article className="detail-card">
          <h2>Platform Objective</h2>
          <p>
            The primary goal is to reduce lead discovery cycle time by ranking candidates before
            expensive downstream simulations and wet-lab validation.
          </p>
        </article>

        <article className="detail-card">
          <h2>Prediction Pipeline</h2>
          <ol>
            <li>Accept protein sequence or disease name.</li>
            <li>Resolve/construct target protein features.</li>
            <li>Generate molecular descriptors from candidate SMILES.</li>
            <li>Predict affinity via XGBoost regression.</li>
            <li>Sort candidates and surface top-ranked compounds.</li>
          </ol>
        </article>

        <article className="detail-card">
          <h2>Core Technology</h2>
          <ul>
            <li>Frontend: React + Vite</li>
            <li>Backend: FastAPI + MongoDB</li>
            <li>ML: XGBoost + scikit-learn</li>
            <li>Cheminformatics: RDKit</li>
            <li>Export: CSV for downstream analysis</li>
          </ul>
        </article>

        <article className="detail-card detail-card-wide">
          <h2>Deployment Readiness</h2>
          <ul>
            <li>Service separation between UI and inference API.</li>
            <li>Stateless HTTP prediction endpoints for scaling.</li>
            <li>Model artifacts loaded for low-latency scoring.</li>
            <li>Structured outputs for integration into screening pipelines.</li>
            <li>Database-backed storage for predictions and metadata.</li>
          </ul>
        </article>
      </section>
    </div>
  );
}

export default AboutPlatform;
