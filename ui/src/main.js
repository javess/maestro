import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import ReactDOM from "react-dom/client";
import { AppBar, Box, Card, CardContent, Chip, Container, CssBaseline, Grid, Stack, ThemeProvider, Toolbar, Typography, createTheme, } from "@mui/material";
const theme = createTheme({
    palette: {
        mode: "light",
        primary: { main: "#0f766e" },
        secondary: { main: "#9a3412" },
        background: { default: "#f7f3ea", paper: "#fffdf8" },
    },
    typography: {
        fontFamily: '"IBM Plex Sans", "Helvetica", sans-serif',
        h4: { fontWeight: 700 },
    },
    shape: {
        borderRadius: 18,
    },
});
const cards = [
    { title: "Orchestrator", value: "Deterministic", subtitle: "State machine, retries, policy gates" },
    { title: "Providers", value: "Pluggable", subtitle: "OpenAI, Gemini, Claude, FakeProvider" },
    { title: "Repo Adapters", value: "Repo-Agnostic", subtitle: "Python, Node, Go, Rust, Java, monorepo" },
    { title: "Evals", value: "Deterministic", subtitle: "Scenario-driven runs and JSON reports" },
];
function App() {
    return (_jsxs(ThemeProvider, { theme: theme, children: [_jsx(CssBaseline, {}), _jsxs(Box, { sx: {
                    minHeight: "100vh",
                    background: "radial-gradient(circle at top left, rgba(15,118,110,0.18), transparent 30%), linear-gradient(180deg, #f7f3ea 0%, #efe4d0 100%)",
                }, children: [_jsx(AppBar, { position: "static", color: "transparent", elevation: 0, children: _jsxs(Toolbar, { children: [_jsx(Typography, { variant: "h6", sx: { flexGrow: 1 }, children: "maestro" }), _jsx(Chip, { label: "Local Dashboard", color: "primary" })] }) }), _jsx(Container, { sx: { py: 6 }, children: _jsxs(Stack, { spacing: 3, children: [_jsxs(Box, { children: [_jsx(Typography, { variant: "h3", gutterBottom: true, children: "Multi-agent delivery with deterministic control." }), _jsx(Typography, { variant: "body1", sx: { maxWidth: 760 }, children: "Visualize run state, policy gates, tickets, and artifacts while the Python engine orchestrates role-specific agents through validated structured payloads." })] }), _jsx(Grid, { container: true, spacing: 2, children: cards.map((card) => (_jsx(Grid, { size: { xs: 12, md: 6 }, children: _jsx(Card, { sx: { minHeight: 180, boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }, children: _jsxs(CardContent, { children: [_jsx(Typography, { variant: "overline", children: card.title }), _jsx(Typography, { variant: "h4", sx: { mt: 1, mb: 2 }, children: card.value }), _jsx(Typography, { variant: "body2", children: card.subtitle })] }) }) }, card.title))) })] }) })] })] }));
}
ReactDOM.createRoot(document.getElementById("root")).render(_jsx(React.StrictMode, { children: _jsx(App, {}) }));
