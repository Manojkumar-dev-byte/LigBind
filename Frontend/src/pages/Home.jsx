import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-shell">
      <header className="home-topbar">
        <div className="home-brand">LigBind</div>
        <div className="home-nav-actions">
          <button className="home-nav-btn" onClick={() => navigate("/about-platform")}>About This Platform</button>
          <button className="home-nav-btn" onClick={() => navigate("/how-to-use")}>How To Use</button>
        </div>
      </header>

      <section className="home-hero">
        <div className="home-badge">LigBind Platform</div>
        <h1>Accelerating Drug Discovery with Protein-Aware Ranking</h1>
        <p>
          LigBind predicts protein-drug binding affinity and ranks thousands of
          candidate molecules so researchers can focus on the most promising
          compounds first.
        </p>

        <div className="home-actions">
          <button className="home-cta" onClick={() => navigate("/dashboard")}>
            Start Discovery
          </button>
        </div>

        <div className="home-metrics">
          <div className="metric-card">
            <span>Model Type</span>
            <strong>XGBoost Regression Ranker</strong>
          </div>
          <div className="metric-card">
            <span>Pipeline Focus</span>
            <strong>Protein-Aware Drug Prioritization</strong>
          </div>
          <div className="metric-card">
            <span>Primary Output</span>
            <strong>Sorted Affinity Candidates + CSV</strong>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
