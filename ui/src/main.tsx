import React, { useEffect, useMemo, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  Alert,
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  CssBaseline,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  Stack,
  TextField,
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
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700 },
  },
  shape: { borderRadius: 18 },
});

const apiBase = import.meta.env.VITE_MAESTRO_API_URL ?? "http://127.0.0.1:8765";

type RunRow = {
  run_id: string;
  status: string;
  current_state: string;
  current_ticket_id?: string | null;
};

type SchedulerRow = {
  run_id: string;
  state: string;
};

type RunEvent = {
  state: string;
  detail: string;
};

type DiffApprovalRequest = {
  ticket_id: string;
  status: string;
};

type RunState = {
  run_id: string;
  status: string;
  current_state: string;
  current_ticket_id?: string | null;
  events: RunEvent[];
  diff_approval_request?: DiffApprovalRequest | null;
  approval_request?: { ticket_id: string; status: string } | null;
  artifacts: { artifacts: { name: string; path: string; kind: string }[]; evidence_bundles: { name: string; path: string; kind: string }[] };
};

type DoctorResult = {
  repo_path: string;
  policy: string;
  repo_type: string;
  support_tier: string;
  readiness_score: number;
  blockers: string[];
  recommendations: string[];
};

function App() {
  const [repoPath, setRepoPath] = useState("/Users/javiersierra/dev/maestro/examples/hello_world_cli_game");
  const [briefPath, setBriefPath] = useState("/Users/javiersierra/dev/maestro/examples/hello_world_cli_game_brief.md");
  const [configPath, setConfigPath] = useState("/Users/javiersierra/dev/maestro/examples/maestro.example.yaml");
  const [doctor, setDoctor] = useState<DoctorResult | null>(null);
  const [runs, setRuns] = useState<RunRow[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>("");
  const [runState, setRunState] = useState<RunState | null>(null);
  const [schedulerRows, setSchedulerRows] = useState<SchedulerRow[]>([]);
  const [actionComment, setActionComment] = useState("");
  const [message, setMessage] = useState<string>("");

  const selectedTicketId = runState?.diff_approval_request?.ticket_id ?? runState?.current_ticket_id ?? "";

  async function fetchDoctor() {
    const params = new URLSearchParams({ repo_path: repoPath, config_path: configPath });
    const response = await fetch(`${apiBase}/api/doctor?${params.toString()}`);
    setDoctor(await response.json());
  }

  async function fetchRuns() {
    const params = new URLSearchParams({ repo_path: repoPath });
    const response = await fetch(`${apiBase}/api/runs?${params.toString()}`);
    const payload = (await response.json()) as RunRow[];
    setRuns(payload);
    if (!selectedRunId && payload.length > 0) {
      setSelectedRunId(payload[0].run_id);
    }
  }

  async function fetchRun(runId: string) {
    const params = new URLSearchParams({ repo_path: repoPath });
    const response = await fetch(`${apiBase}/api/runs/${runId}?${params.toString()}`);
    setRunState(await response.json());
  }

  async function fetchScheduler() {
    const response = await fetch(`${apiBase}/api/scheduler`);
    setSchedulerRows((await response.json()) as SchedulerRow[]);
  }

  async function startPlan() {
    const response = await fetch(`${apiBase}/api/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_path: repoPath, brief_path: briefPath, config_path: configPath }),
    });
    const payload = (await response.json()) as { run_id: string };
    setSelectedRunId(payload.run_id);
    setMessage(`Started run ${payload.run_id}`);
    await fetchRuns();
  }

  async function runAction(action: "approve" | "reject" | "rerun") {
    if (!selectedRunId || !selectedTicketId) {
      return;
    }
    const response = await fetch(`${apiBase}/api/runs/${selectedRunId}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_path: repoPath, ticket_id: selectedTicketId, comment: actionComment }),
    });
    const payload = (await response.json()) as RunState;
    setRunState(payload);
    setMessage(`${action} applied to ${selectedTicketId}`);
  }

  async function cancelRun() {
    if (!selectedRunId) {
      return;
    }
    const response = await fetch(`${apiBase}/api/runs/${selectedRunId}/cancel`, {
      method: "POST",
    });
    const payload = (await response.json()) as { cancelled: boolean };
    setMessage(payload.cancelled ? `Cancelled ${selectedRunId}` : `Unable to cancel ${selectedRunId}`);
    await fetchScheduler();
  }

  useEffect(() => {
    void fetchDoctor();
    void fetchRuns();
    void fetchScheduler();
  }, [repoPath, configPath]);

  useEffect(() => {
    if (!selectedRunId) {
      return;
    }
    void fetchRun(selectedRunId);
    const interval = window.setInterval(() => {
      void fetchRun(selectedRunId);
      void fetchRuns();
      void fetchScheduler();
    }, 2000);
    return () => window.clearInterval(interval);
  }, [selectedRunId, repoPath]);

  const artifactCount = useMemo(
    () => (runState ? runState.artifacts.artifacts.length + runState.artifacts.evidence_bundles.length : 0),
    [runState],
  );

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
              maestro operator console
            </Typography>
            <Chip label="UI-first run control" color="primary" />
          </Toolbar>
        </AppBar>
        <Container sx={{ py: 4 }}>
          <Stack spacing={3}>
            {message ? <Alert severity="info">{message}</Alert> : null}
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 5 }}>
                <Card sx={{ boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }}>
                  <CardContent>
                    <Typography variant="h4" gutterBottom>
                      Start a run
                    </Typography>
                    <Stack spacing={2}>
                      <TextField label="Repo path" value={repoPath} onChange={(event) => setRepoPath(event.target.value)} fullWidth />
                      <TextField label="Brief path" value={briefPath} onChange={(event) => setBriefPath(event.target.value)} fullWidth />
                      <TextField label="Config path" value={configPath} onChange={(event) => setConfigPath(event.target.value)} fullWidth />
                      <Stack direction="row" spacing={1}>
                        <Button variant="contained" onClick={() => void startPlan()}>
                          Start plan
                        </Button>
                        <Button variant="outlined" onClick={() => void fetchDoctor()}>
                          Refresh doctor
                        </Button>
                      </Stack>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, md: 7 }}>
                <Card sx={{ boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }}>
                  <CardContent>
                    <Typography variant="h4" gutterBottom>
                      Repo readiness
                    </Typography>
                    {doctor ? (
                      <Stack spacing={1}>
                        <Stack direction="row" spacing={1}>
                          <Chip label={doctor.repo_type} />
                          <Chip label={doctor.support_tier} color="secondary" />
                          <Chip label={`score ${doctor.readiness_score}`} />
                        </Stack>
                        <Typography variant="body2">Policy: {doctor.policy}</Typography>
                        <Typography variant="subtitle2">Blockers</Typography>
                        <List dense>
                          {doctor.blockers.length === 0 ? <ListItem><ListItemText primary="None" /></ListItem> : doctor.blockers.map((item) => <ListItem key={item}><ListItemText primary={item} /></ListItem>)}
                        </List>
                        <Typography variant="subtitle2">Recommendations</Typography>
                        <List dense>
                          {doctor.recommendations.map((item) => <ListItem key={item}><ListItemText primary={item} /></ListItem>)}
                        </List>
                      </Stack>
                    ) : null}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 4 }}>
                <Card sx={{ minHeight: 520, boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }}>
                  <CardContent>
                    <Typography variant="h4" gutterBottom>
                      Runs
                    </Typography>
                    <List dense>
                      {runs.map((run) => (
                        <ListItem
                          key={run.run_id}
                          component="button"
                          onClick={() => setSelectedRunId(run.run_id)}
                          sx={{
                            borderRadius: 2,
                            mb: 1,
                            bgcolor: selectedRunId === run.run_id ? "rgba(15,118,110,0.08)" : "transparent",
                          }}
                        >
                          <ListItemText primary={run.run_id} secondary={`${run.status} · ${run.current_state}`} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, md: 8 }}>
                <Card sx={{ minHeight: 520, boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }}>
                  <CardContent>
                    <Typography variant="h4" gutterBottom>
                      Run detail
                    </Typography>
                    {runState ? (
                      <Stack spacing={2}>
                        <Stack direction="row" spacing={1}>
                          <Chip label={runState.status} color="primary" />
                          <Chip label={runState.current_state} />
                          <Chip label={`${artifactCount} artifacts`} />
                          <Button size="small" onClick={() => void cancelRun()}>
                            Cancel run
                          </Button>
                        </Stack>
                        {runState.diff_approval_request ? (
                          <Alert severity="warning">
                            Diff approval required for {runState.diff_approval_request.ticket_id}
                          </Alert>
                        ) : null}
                        {runState.diff_approval_request ? (
                          <Stack spacing={1}>
                            <TextField
                              label="Approval comment"
                              value={actionComment}
                              onChange={(event) => setActionComment(event.target.value)}
                              fullWidth
                            />
                            <Stack direction="row" spacing={1}>
                              <Button variant="contained" onClick={() => void runAction("approve")}>
                                Approve
                              </Button>
                              <Button variant="outlined" color="secondary" onClick={() => void runAction("reject")}>
                                Reject
                              </Button>
                              <Button variant="outlined" onClick={() => void runAction("rerun")}>
                                Rerun
                              </Button>
                            </Stack>
                          </Stack>
                        ) : null}
                        <Divider />
                        <Typography variant="subtitle1">Events</Typography>
                        <List dense sx={{ maxHeight: 220, overflow: "auto" }}>
                          {runState.events.map((event, index) => (
                            <ListItem key={`${event.state}-${index}`}>
                              <ListItemText primary={event.state} secondary={event.detail} />
                            </ListItem>
                          ))}
                        </List>
                        <Divider />
                        <Typography variant="subtitle1">Artifacts</Typography>
                        <List dense sx={{ maxHeight: 220, overflow: "auto" }}>
                          {[...runState.artifacts.artifacts, ...runState.artifacts.evidence_bundles].map((artifact) => (
                            <ListItem key={artifact.path}>
                              <ListItemText primary={artifact.name} secondary={artifact.path} />
                            </ListItem>
                          ))}
                        </List>
                      </Stack>
                    ) : (
                      <Typography variant="body2">Select a run to inspect its state.</Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            <Card sx={{ boxShadow: "0 16px 40px rgba(49,35,19,0.08)" }}>
              <CardContent>
                <Typography variant="h4" gutterBottom>
                  Scheduler
                </Typography>
                <List dense>
                  {schedulerRows.map((row) => (
                    <ListItem key={row.run_id}>
                      <ListItemText primary={row.run_id} secondary={row.state} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
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
