
import { useEffect, useState } from "react";
import {
  fetchFiles,
  fetchFileEntries,
  uploadFile,
  deleteFile,
  type LogFile,
  type LogEntry,
} from "./api";
import "./App.css";

function App() {
  const [activeNav, setActiveNav] = useState("Overview");

  const [files, setFiles] = useState<LogFile[]>([]);
  const [selectedFileId, setSelectedFileId] = useState("");

  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [entriesLoading, setEntriesLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [deletingFileId, setDeletingFileId] = useState<number | null>(null);
  async function loadFiles() {
    try {
      setApiError("");
      const result = await fetchFiles();
      setFiles(result);

      setSelectedFileId((current) => {
        if (current && result.some((file) => String(file.id) === current)) {
          return current;
        }

        return result.length ? String(result[0].id) : "";
      });
    } catch (error) {
      setApiError(
        error instanceof Error ? error.message : "Could not load files."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadFiles();
  }, []);

  useEffect(() => {
    if (!selectedFileId) {
      setEntries([]);
      return;
    }

    let cancelled = false;

    async function loadEntries() {
      setEntriesLoading(true);
      setApiError("");

      try {
        const result = await fetchFileEntries(Number(selectedFileId));

        if (!cancelled) {
          setEntries(result.entries);
        }
      } catch (error) {
        if (!cancelled) {
          setEntries([]);
          setApiError(
            error instanceof Error
              ? error.message
              : "Could not load log entries."
          );
        }
      } finally {
        if (!cancelled) {
          setEntriesLoading(false);
        }
      }
    }

    void loadEntries();

    return () => {
      cancelled = true;
    };
  }, [selectedFileId]);

  const totalLines = files.reduce(
    (sum, file) => sum + file.total_lines,
    0
  );

  const parsedLines = files.reduce(
    (sum, file) => sum + file.parsed_lines,
    0
  );

  const failedLines = files.reduce(
    (sum, file) => sum + file.failed_lines,
    0
  );

  const stats = [
    { label: "Uploaded files", value: String(files.length), color: "blue" },
    { label: "Total lines", value: String(totalLines), color: "purple" },
    { label: "Parsed lines", value: String(parsedLines), color: "blue" },
    { label: "Parse failures", value: String(failedLines), color: "yellow" },
  ];
  
const severityLevels = [
  "DEBUG",
  "INFO",
  "WARNING",
  "ERROR",
  "CRITICAL",
];

const severityCounts = severityLevels.map((level) => ({
  level,
  count: entries.filter((entry) => entry.level === level).length,
}));

const maxSeverityCount = Math.max(
  1,
  ...severityCounts.map((item) => item.count)
);

const sourceCounts = Object.entries(
  entries.reduce<Record<string, number>>((counts, entry) => {
    const source = entry.source || "Unknown";
    counts[source] = (counts[source] || 0) + 1;
    return counts;
  }, {})
)
  .map(([source, count]) => ({ source, count }))
  .sort((a, b) => b.count - a.count)
  .slice(0, 5);

const errorCount = entries.filter(
  (entry) => entry.level === "ERROR" || entry.level === "CRITICAL"
).length;

const errorRate =
  entries.length > 0
    ? ((errorCount / entries.length) * 100).toFixed(1)
    : "0.0";

const selectedFile = files.find(
  (file) => String(file.id) === selectedFileId
);

const selectedParsedRate =
  selectedFile && selectedFile.total_lines > 0
    ? (
        (selectedFile.parsed_lines / selectedFile.total_lines) *
        100
      ).toFixed(1)
    : "0.0";

  const visibleEntries = entries.filter((entry) => {
    const matchesLevel = filter === "ALL" || entry.level === filter;
    const query = search.trim().toLowerCase();

    const searchableText =
      `${entry.source ?? ""} ${entry.message} ${entry.level} ${entry.line_number}`;

    return matchesLevel && searchableText.toLowerCase().includes(query);
  });

async function handleDelete(file: LogFile) {
  const confirmed = window.confirm(
    `Delete "${file.filename}"?\n\nThis permanently removes the uploaded file and its parsed log entries.`
  );

  if (!confirmed) return;

  setDeletingFileId(file.id);
  setApiError("");

  try {
    await deleteFile(file.id);
    await loadFiles();
  } catch (error) {
    setApiError(
      error instanceof Error ? error.message : "Could not delete file."
    );
  } finally {
    setDeletingFileId(null);
  }
}

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const input = event.currentTarget;
    const file = input.files?.[0];

    if (!file) return;

    setUploading(true);
    setApiError("");

    try {
      const result = await uploadFile(file);
      await loadFiles();

      if (result.file?.id) {
        setSelectedFileId(String(result.file.id));
      }
    } catch (error) {
      setApiError(
        error instanceof Error ? error.message : "Upload failed."
      );
    } finally {
      setUploading(false);
      input.value = "";
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">L</div>
          <div>
            <strong>LogLens</strong>
            <span>LOG INTELLIGENCE</span>
          </div>
        </div>

        <p className="nav-heading">WORKSPACE</p>

        {["Overview", "Log Explorer", "Uploaded Files", "Analytics"].map(
          (item) => (
            <button
              key={item}
              className={`nav-item ${activeNav === item ? "active" : ""}`}
              onClick={() => setActiveNav(item)}
            >
              <span className="nav-dot" />
              {item}
            </button>
          )
        )}

        <div className="sidebar-bottom">
          <span className="status-dot" />
          Flask API connected
          <small>Flask · PostgreSQL</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <span className="breadcrumb">Workspace / {activeNav}</span>
          <span className="environment">
            <span className="status-dot" />
            LOCAL ENVIRONMENT
          </span>
        </header>

        <section className="page-heading">
          <div>
            <p className="eyebrow">OBSERVABILITY WORKSPACE</p>
            <h1>{activeNav}</h1>
            <p className="subtitle">
              Explore and investigate your application logs.
            </p>
          </div>

          <label className="upload-button">
            <span>＋</span>
            {uploading ? "Uploading..." : "Select log file"}
            <input
              type="file"
              accept=".log,.txt"
              disabled={uploading}
              onChange={handleUpload}
            />
          </label>
        </section>

        {loading && (
          <p className="subtitle page-message">Loading files from Flask...</p>
        )}

        {apiError && (
          <div role="alert" className="api-error">
            {apiError}
            <button
              className="retry-button"
              onClick={() => void loadFiles()}
            >
              Refresh files
            </button>
          </div>
        )}

        <section className="stats-grid">
          {stats.map((stat) => (
            <article className="stat-card" key={stat.label}>
              <div className="stat-top">
                <span>{stat.label}</span>
                <span className={`stat-indicator ${stat.color}`} />
              </div>
              <strong>{stat.value}</strong>
              <small>{loading ? "Loading..." : "From PostgreSQL"}</small>
            </article>
          ))}
        </section>
          
{activeNav === "Analytics" && (
  <>
    <section className="analytics-summary">
      <article className="analytics-card">
        <span>Parsed entries</span>
        <strong>{entries.length}</strong>
        <small>Selected file</small>
      </article>

      <article className="analytics-card">
        <span>Error rate</span>
        <strong>{errorRate}%</strong>
        <small>ERROR + CRITICAL entries</small>
      </article>

      <article className="analytics-card">
        <span>Parse success</span>
        <strong>{selectedParsedRate}%</strong>
        <small>Lines successfully parsed</small>
      </article>

      <article className="analytics-card">
        <span>Failed lines</span>
        <strong>{selectedFile?.failed_lines ?? 0}</strong>
        <small>Selected file</small>
      </article>
    </section>

    <section className="analytics-grid">
      <article className="panel analytics-panel">
        <div className="panel-heading">
          <div>
            <h2>Severity distribution</h2>
            <p>Parsed entries by log level</p>
          </div>
        </div>

        <div className="chart-content">
          {severityCounts.map(({ level, count }) => (
            <div className="bar-row" key={level}>
              <span className={`chart-level ${level.toLowerCase()}`}>
                {level}
              </span>

              <div className="bar-track">
                <div
                  className={`bar-fill ${level.toLowerCase()}`}
                  style={{
                    width: `${(count / maxSeverityCount) * 100}%`,
                  }}
                />
              </div>

              <strong>{count}</strong>
            </div>
          ))}

          {entries.length === 0 && (
            <p className="empty-state">No parsed entries to analyze.</p>
          )}
        </div>
      </article>

      <article className="panel analytics-panel">
        <div className="panel-heading">
          <div>
            <h2>Top log sources</h2>
            <p>Services with the most entries</p>
          </div>
        </div>

        <div className="source-list">
          {sourceCounts.map(({ source, count }) => (
            <div className="source-row" key={source}>
              <span className="source-cell">{source}</span>
              <strong>{count}</strong>
            </div>
          ))}

          {sourceCounts.length === 0 && (
            <p className="empty-state">No sources available.</p>
          )}
        </div>
      </article>
    </section>

    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Parsing overview</h2>
          <p>Processing results across all uploaded files</p>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>FILE</th>
              <th>TOTAL LINES</th>
              <th>PARSED</th>
              <th>FAILED</th>
              <th>SUCCESS RATE</th>
            </tr>
          </thead>

          <tbody>
            {files.map((file) => {
              const successRate =
                file.total_lines > 0
                  ? ((file.parsed_lines / file.total_lines) * 100).toFixed(1)
                  : "0.0";

              return (
                <tr key={file.id}>
                  <td className="source-cell">{file.filename}</td>
                  <td>{file.total_lines}</td>
                  <td>{file.parsed_lines}</td>
                  <td>{file.failed_lines}</td>
                  <td>{successRate}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  </>
)}
      {activeNav !== "Analytics" && (
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Log Explorer</h2>
              <p>
                {entriesLoading
                  ? "Loading parsed entries..."
                  : `${visibleEntries.length} matching entries · ${
                      entries.length
                    } total parsed`}
              </p>
            </div>
            <span className="live-label">
              <span className="status-dot" />
              LIVE API DATA
            </span>
          </div>

          <div className="table-controls">
            <select
              aria-label="Select uploaded file"
              value={selectedFileId}
              onChange={(event) => setSelectedFileId(event.target.value)}
            >
              {files.length === 0 && <option value="">No files available</option>}
              {files.map((file) => (
                <option key={file.id} value={String(file.id)}>
                  {file.filename} (ID {file.id})
                </option>
              ))}
            </select>

            <input
              className="search-input"
              placeholder="Search messages, sources, levels..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />

            <select
              aria-label="Filter by severity"
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
            >
              {["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].map(
                (level) => (
                  <option key={level} value={level}>
                    {level === "ALL" ? "All levels" : level}
                  </option>
                )
              )}
            </select>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>LINE</th>
                  <th>TIME</th>
                  <th>LEVEL</th>
                  <th>SOURCE</th>
                  <th>MESSAGE</th>
                </tr>
              </thead>

              <tbody>
                {visibleEntries.map((entry) => (
                  <tr key={entry.id}>
                    <td className="time-cell">{entry.line_number}</td>
                    <td className="time-cell">
                      {entry.timestamp
                        ? new Date(entry.timestamp).toLocaleTimeString()
                        : "—"}
                    </td>
                    <td>
                      <span
                        className={`level-badge ${entry.level.toLowerCase()}`}
                      >
                        {entry.level}
                      </span>
                    </td>
                    <td className="source-cell">
                      {entry.source ?? "—"}
                    </td>
                    <td>{entry.message}</td>
                  </tr>
                ))}

                {!entriesLoading && visibleEntries.length === 0 && (
                  <tr>
                    <td colSpan={5} className="empty-state">
                      {entries.length === 0
                        ? "No parsed entries in this file."
                        : "No entries match your search or severity filter."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <footer className="panel-footer">
            <span>
              Showing {visibleEntries.length} of {entries.length} parsed entries
            </span>
            <span>
              LogLens <span className="version">v0.1.0</span>
            </span>
          </footer>
        </section>
)}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Uploaded files</h2>
              <p>Files retrieved from your Flask API</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>FILE</th>
                  <th>TOTAL LINES</th>
                  <th>PARSED</th>
                  <th>FAILED</th>
                  <th>UPLOADED AT</th>
                  <th>ACTION</th>
                </tr>
              </thead>

              <tbody>
            
{files.map((file) => (
  <tr key={file.id}>
    <td className="source-cell">{file.filename}</td>
    <td>{file.total_lines}</td>
    <td>{file.parsed_lines}</td>
    <td>{file.failed_lines}</td>
    <td>{new Date(file.uploaded_at).toLocaleString()}</td>
    <td>
      <button
        className="delete-button"
        disabled={deletingFileId !== null}
        onClick={() => void handleDelete(file)}
      >
        {deletingFileId === file.id ? "Deleting..." : "Delete"}
      </button>
    </td>
  </tr>
))}

{!loading && files.length === 0 && (
  <tr>
    <td colSpan={6} className="empty-state">
      No files uploaded yet. Select a log file to get started.
    </td>
  </tr>
)}

              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
