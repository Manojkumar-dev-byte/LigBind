import { useNavigate } from "react-router-dom";

function HowToUse() {
  const navigate = useNavigate();

  return (
    <div className="detail-shell">
      <header className="detail-topbar">
        <button className="detail-back" onClick={() => navigate("/")}>Back to Home</button>
        <button className="detail-primary" onClick={() => navigate("/dashboard")}>Open Dashboard</button>
      </header>

      <section className="detail-hero">
        <span className="detail-badge">How To Use</span>
        <h1>Operational Guide: From Target Input to Ranked Output</h1>
        <p>
          Follow this workflow to run predictions efficiently and export ranked candidates for
          external analysis.
        </p>
      </section>

      <section className="detail-grid">
        <article className="detail-card">
          <h2>Step 1: Select Input Mode</h2>
          <ul>
            <li>Protein Sequence mode for direct target input.</li>
            <li>Disease Name mode for mapped protein resolution.</li>
          </ul>
        </article>

        <article className="detail-card">
          <h2>Step 2: Configure Ranking Scope</h2>
          <ul>
            <li>Set Top-N to control shortlist depth.</li>
            <li>Optionally supply custom SMILES candidates.</li>
            <li>Leave custom list empty to use full library.</li>
          </ul>
        </article>

        <article className="detail-card">
          <h2>Step 3: Run Discovery</h2>
          <ul>
            <li>Click Rank Drug Candidates.</li>
            <li>Review top affinities and candidate ordering.</li>
            <li>Use ranking output to prioritize validation candidates.</li>
          </ul>
        </article>

        <article className="detail-card detail-card-wide">
          <h2>Step 4: Export and Integrate</h2>
          <ul>
            <li>Use Export CSV for the complete ranked table.</li>
            <li>Share output with medicinal chemistry teams.</li>
            <li>Use scores as a triage layer before high-cost experiments.</li>
          </ul>
        </article>
      </section>
    </div>
  );
}

export default HowToUse;
