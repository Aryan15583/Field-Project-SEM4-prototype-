import { Suspense, lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import { Mascot, Spinner } from "./components/ui";
import Daily from "./pages/Daily";
import Landing from "./pages/Landing";
import Leaderboard from "./pages/Leaderboard";
import Learn from "./pages/Learn";
import Lesson from "./pages/Lesson";
import Profile from "./pages/Profile";
import { TwoFactorSetup, TwoFactorVerify } from "./pages/TwoFactor";

// Heavier pages (charts, admin tools) load on demand.
const Stats = lazy(() => import("./pages/Stats"));
const Admin = lazy(() => import("./pages/Admin"));

function RequireAuth({ children, admin = false }) {
  const { status, user } = useAuth();
  if (status === "loading") return <Spinner />;
  if (status !== "authed") return <Navigate to="/" replace />;
  if (admin && user.role !== "admin") return <Navigate to="/learn" replace />;
  return children;
}

function PublicOnly({ children }) {
  const { status } = useAuth();
  if (status === "loading") return <Spinner />;
  return status === "authed" ? <Navigate to="/learn" replace /> : children;
}

function NotFound() {
  return (
    <div className="grid min-h-[60vh] place-items-center text-center">
      <div>
        <Mascot size={110} mood="sad" className="mx-auto" />
        <h1 className="mt-4 text-2xl font-black">404 - page not found</h1>
        <a href="/learn" className="btn-link">
          Back to learning
        </a>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PublicOnly><Landing /></PublicOnly>} />
      <Route path="/2fa/setup" element={<TwoFactorSetup />} />
      <Route path="/2fa/verify" element={<TwoFactorVerify />} />
      <Route path="/lesson/:id" element={<RequireAuth><Lesson /></RequireAuth>} />
      <Route element={<RequireAuth><Layout /></RequireAuth>}>
        <Route path="/learn" element={<Learn />} />
        <Route path="/daily" element={<Daily />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/stats" element={<Suspense fallback={<Spinner />}><Stats /></Suspense>} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/admin" element={<RequireAuth admin><Suspense fallback={<Spinner />}><Admin /></Suspense></RequireAuth>} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
