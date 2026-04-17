import { useState } from "react";
import axios from "axios";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const registerUser = async (e) => {
    e.preventDefault();

    try {
      await axios.post(
        "http://127.0.0.1:8000/auth/register",
        {
          name,
          email,
          password,
        }
      );

      alert("Registration Successful");
      window.location.href = "/login";
    } catch (error) {
      alert(`Registration Failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="logo-box">⚗</div>

        <h1>Sign Up</h1>
        <p className="subtext">Create your account</p>

        <form onSubmit={registerUser}>
          <label>Full Name</label>
          <input
            type="text"
            placeholder="John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <label>Email</label>
          <input
            type="email"
            placeholder="you@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">Create Account</button>
        </form>

        <p className="bottom-text">
          Already have account? <a href="/login">Login</a>
        </p>
      </div>
    </div>
  );
}

export default Register;