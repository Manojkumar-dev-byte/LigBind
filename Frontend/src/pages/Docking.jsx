import { useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import * as $3Dmol from "3dmol";

function Docking() {
  const viewerRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);
  const drug = params.get("drug") || "Selected Drug";
  const disease = params.get("disease") || "Target Disease";

  useEffect(() => {
    const viewer = $3Dmol.createViewer(viewerRef.current, {
      backgroundColor: "#0f172a",
    });

    viewer.addModel(
      `
ATOM      1  N   GLY A   1      -0.500   0.000   0.000
ATOM      2  CA  GLY A   1       0.500   0.000   0.000
ATOM      3  C   GLY A   1       1.200   1.100   0.000
ATOM      4  O   GLY A   1       1.900   1.600   0.000
ATOM      5  C1  LIG B   2       0.000   2.000   0.000
ATOM      6  C2  LIG B   2       1.000   2.600   0.000
END
`,
      "pdb"
    );

    viewer.setStyle({ chain: "A" }, { cartoon: { color: "spectrum" } });
    viewer.setStyle({ chain: "B" }, { stick: { color: "lime" } });
    viewer.zoomTo();
    viewer.render();
  }, []);

  return (
    <div className="dashboard-shell">
      <div className="dashboard-topbar">
        <div>
          <h1>LigBind Docking Lab</h1>
          <p>Protein-Ligand Visualization</p>
        </div>

        <button
          className="logout-btn"
          onClick={() => navigate("/dashboard")}
        >
          Back
        </button>
      </div>

      <div className="leaderboard-panel">
        <div className="panel-head">
          <h2>{drug}</h2>
          <span>{disease}</span>
        </div>

        <div ref={viewerRef} className="docking-viewer"></div>
      </div>
    </div>
  );
}

export default Docking;