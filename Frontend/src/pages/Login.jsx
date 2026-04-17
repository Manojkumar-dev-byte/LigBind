import { useState } from "react";
import axios from "axios";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const loginUser = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please enter email and password");
      return;
    }

    try {
      setLoading(true);

      const res = await axios.post(
        "http://127.0.0.1:8000/auth/login",
        {
          email: email.trim(),
          password: password.trim(),
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Login Success:", res.data);

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("userEmail", email);

      alert("Login Successful");

      window.location.href = "/dashboard";
    } catch (error) {
      console.log("FULL ERROR:", error);

      const msg =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error.message ||
        "Login failed";

      alert("Login Failed: " + msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="logo-box">⚗</div>

        <h1>LigBind</h1>
        <p className="subtext">Login to continue</p>

        <form onSubmit={loginUser}>
          <label>Email</label>
          <input
            type="email"
            placeholder="you@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="bottom-text">
          New user? <a href="/register">Create account</a>
        </p>
      </div>
    </div>
  );
}

export default Login;