import React from "react";
import ReactDOM from "react-dom/client";
import {
  AppBar,
  Box,
  Card,
  CardContent,
  Chip,
  Container,
  CssBaseline,
  Grid,
  Stack,
  ThemeProvider,
  Toolbar,
  Typography,
  createTheme,
} from "@mui/material";

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
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          background:
            "radial-gradient(circle at top left, rgba(15,118,110,0.18), transparent 30%), linear-gradient(180deg, #f7f3ea 0%, #efe4d0 100%)",
        }}
      >
        <AppBar position="static" color="transparent" elevation={0}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              maestro
            </Typography>
            <Chip label="Local Dashboard" color="primary" />
          </Toolbar>
        </AppBar>
        <Container sx={{ py: 6 }}>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h3" gutterBottom>
                Multi-agent delivery with deterministic control.
              </Typography>
              <Typography variant="body1" sx={{ maxWidth: 760 }}>
                Visualize run state, policy gates, tickets, and artifacts while the Python engine
                orchestrates role-specific agents through validated structured payloads.
              </Typography>
            </Box>
            <Grid container spacing={2}>
              {cards.map((card) => (
                <Grid size={{ xs: 12, md: 6 }} key={card.title}>
                  <Card sx={{ minHeight: 180, boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }}>
                    <CardContent>
                      <Typography variant="overline">{card.title}</Typography>
                      <Typography variant="h4" sx={{ mt: 1, mb: 2 }}>
                        {card.value}
                      </Typography>
                      <Typography variant="body2">{card.subtitle}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Stack>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
