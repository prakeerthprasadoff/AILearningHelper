import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

const DEMO_EMAIL = "demo@myapp.com";
const DEMO_PASSWORD = "abcd";

function isAuthenticated() {
  return sessionStorage.getItem("student_auth") === "true";
}

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }

    if (email.trim().toLowerCase() === DEMO_EMAIL && password === DEMO_PASSWORD) {
      sessionStorage.setItem("student_auth", "true");
      sessionStorage.setItem("student_email", email.trim().toLowerCase());
      navigate("/dashboard");
      return;
    }

    setError("Invalid credentials. Please use the demo login details.");
  }

  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#26648E] via-[#4F8FC0] to-[#53D2DC] p-6 text-white">
      <div className="orb orb-one" />
      <div className="orb orb-two" />

      <section className="relative z-10 mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-5xl items-center justify-center gap-8">
        <div className="fade-in hidden max-w-md space-y-4 lg:block">
          <p className="inline-block rounded-full border border-[#FFE3B3]/60 bg-[#FFE3B3]/20 px-3 py-1 text-xs font-medium uppercase tracking-wide text-[#FFE3B3]">
            Student portal
          </p>
          <h1 className="text-4xl font-bold leading-tight text-[#FFF2D7]">
            Login to access your homework assistant.
          </h1>
          <p className="text-[#E8F7FB]">
            Frontend-only auth for now. Agentic homework support will be connected
            next.
          </p>
        </div>

        <div className="fade-in-up w-full max-w-md rounded-3xl border border-[#FFE3B3]/45 bg-[#26648E]/30 p-8 shadow-2xl backdrop-blur-xl transition-transform duration-300 hover:-translate-y-1">
          <h2 className="text-2xl font-semibold text-[#FFE3B3]">Sign in</h2>
          <p className="mt-2 text-sm text-[#D7EEF8]">
            Use the demo credentials to enter the dashboard.
          </p>

          <div className="mt-5 rounded-xl border border-[#FFE3B3]/55 bg-[#FFE3B3]/15 p-4 text-sm">
            <p className="font-semibold text-[#FFE3B3]">Demo credentials</p>
            <p className="mt-1 text-[#E8F7FB]">
              Email: <span className="font-medium text-white">{DEMO_EMAIL}</span>
            </p>
            <p className="text-[#E8F7FB]">
              Password: <span className="font-medium text-white">{DEMO_PASSWORD}</span>
            </p>
          </div>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-[#FFE3B3]">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 px-4 py-2.5 text-sm text-white placeholder:text-[#b9dfe9] transition-all duration-300 focus:-translate-y-0.5 focus:border-[#FFE3B3] focus:outline-none focus:ring-2 focus:ring-[#FFE3B3]/45"
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-[#FFE3B3]">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-xl border border-[#53D2DC]/35 bg-[#26648E]/55 px-4 py-2.5 text-sm text-white placeholder:text-[#b9dfe9] transition-all duration-300 focus:-translate-y-0.5 focus:border-[#FFE3B3] focus:outline-none focus:ring-2 focus:ring-[#FFE3B3]/45"
              />
            </div>

            {error ? (
              <p className="error-in rounded-lg border border-[#FFE3B3]/80 bg-[#FFE3B3]/90 px-3 py-2 text-sm text-[#26648E]">
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              className="w-full rounded-xl bg-[#FFE3B3] px-4 py-2.5 text-sm font-semibold text-[#1f4d6f] transition-all duration-300 hover:-translate-y-0.5 hover:bg-[#fff0cf] active:translate-y-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#FFE3B3]"
            >
              Sign in
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}

export default LoginPage;
