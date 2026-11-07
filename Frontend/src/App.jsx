import { useEffect, useMemo, useState } from "react";
import { Activity, ArrowRight, CheckCircle2, CloudSun, Database, FileImage, Leaf, Loader2, LogIn, RefreshCw, Sprout, UploadCloud, XCircle } from "lucide-react";
import { detectDisease, getHealth, getHistory, predictYield, recommendCrop } from "./api";

const cropDefaults = { N: 90, P: 42, K: 43, temperature: 20.88, humidity: 82, ph: 6.5, rainfall: 202.9 };
const yieldDefaults = { Area: "India", Item: "Rice, paddy", Year: 2024, average_rain_fall_mm_per_year: 1083, pesticides_tonnes: 500, avg_temp: 26.5 };
const farmerId = "demo-farmer-001";

function App() {
  const [active, setActive] = useState("overview");
  const [crop, setCrop] = useState(null);
  const [yieldResult, setYieldResult] = useState(null);
  const [disease, setDisease] = useState(null);
  const [history, setHistory] = useState([]);
  const [apiStatus, setApiStatus] = useState("checking");
  const [notice, setNotice] = useState(null);

  useEffect(() => {
    getHealth().then(() => setApiStatus("online")).catch(() => setApiStatus("offline"));
    refreshHistory();
  }, []);

  async function refreshHistory() {
    try {
      const data = await getHistory(farmerId);
      setHistory(data.items || []);
    } catch {
      setHistory([]);
    }
  }

  function showError(error) {
    setNotice({ type: "error", text: error.message || "Something went wrong. Check that the backend is running." });
  }

  async function runCrop(payload) {
    setNotice(null);
    try { setCrop({ loading: true }); const result = await recommendCrop(payload, farmerId); setCrop({ result }); await refreshHistory(); }
    catch (error) { setCrop({ error: error.message }); showError(error); }
  }

  async function runYield(payload) {
    setNotice(null);
    try { setYieldResult({ loading: true }); const result = await predictYield(payload, farmerId); setYieldResult({ result }); await refreshHistory(); }
    catch (error) { setYieldResult({ error: error.message }); showError(error); }
  }

  async function runDisease(file) {
    setNotice(null);
    if (!file) return;
    if (!file.type.match(/^image\/(jpeg|png|jpg)$/)) { const error = new Error("Please choose a JPG or PNG image."); setDisease({ error: error.message }); showError(error); return; }
    if (file.size > 10 * 1024 * 1024) { const error = new Error("Image must be smaller than 10 MB."); setDisease({ error: error.message }); showError(error); return; }
	try { setDisease({ loading: true, fileName: file.name, preview: URL.createObjectURL(file) }); const result = await detectDisease(file, farmerId); setDisease((current) => ({ ...current, loading: false, result, error: null })); await refreshHistory(); }
    catch (error) { setDisease((current) => ({ ...current, error: error.message })); showError(error); }
  }

  const sections = {
    overview: <Overview onNavigate={setActive} crop={crop} yieldResult={yieldResult} disease={disease} history={history} />,
    crop: <CropPanel onSubmit={runCrop} state={crop} />,
    yield: <YieldPanel onSubmit={runYield} state={yieldResult} />,
    disease: <DiseasePanel onSubmit={runDisease} state={disease} />,
    history: <HistoryPanel items={history} onRefresh={refreshHistory} />,
  };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><Sprout size={21} /></span><span><strong>AgriSense</strong><small>FIELD INTELLIGENCE</small></span></div>
      <nav>{[["overview", "Overview", Activity], ["crop", "Crop fit", Sprout], ["yield", "Yield forecast", CloudSun], ["disease", "Plant health", FileImage], ["history", "Query history", Database]].map(([id, label, Icon]) => <button key={id} className={active === id ? "nav-item active" : "nav-item"} onClick={() => setActive(id)}><Icon size={17} />{label}</button>)}</nav>
      <div className="sidebar-note"><span className={`status-dot ${apiStatus}`} />API {apiStatus === "online" ? "connected" : apiStatus === "offline" ? "offline" : "checking"}<p>Predictions are advisory. Verify decisions locally.</p></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><div className="eyebrow">WEEK 5 · FRONTEND + INTEGRATION</div><h1>Good morning, grower.</h1></div><div className="farmer-chip"><span className="avatar">S</span><span><b>Shibam</b><small>Demo farmer</small></span></div></header>
      {notice && <div className={notice.type === "error" ? "notice error" : "notice success"}><XCircle size={17} />{notice.text}<button onClick={() => setNotice(null)}>×</button></div>}
      <section className="hero"><div><span className="pill gold">AI-ASSISTED CROP MANAGEMENT</span><h2>Make your next field decision with more context.</h2><p>One workspace for crop fit, yield planning, plant health, and the history behind every query.</p><div className="hero-actions"><button className="button primary" onClick={() => setActive("crop")}>Run crop fit <ArrowRight size={16} /></button><button className="button ghost" onClick={() => setActive("disease")}>Analyze a leaf</button></div></div><div className="hero-orbit"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit-copy"><small>TODAY'S PRINCIPLE</small><strong>Measure twice.<br />Act clearly.</strong></div></div></section>
      {sections[active]}
    </main>
  </div>;
}

function Overview({ onNavigate, crop, yieldResult, disease, history }) {
  return <>
    <section className="metric-grid"><Metric icon={<Sprout />} label="Crop fit" value={crop?.result?.recommended_crop || "Ready"} detail={crop?.result ? `${Math.round(crop.result.confidence * 100)}% confidence` : "7 soil & weather inputs"} /><Metric icon={<CloudSun />} label="Yield forecast" value={yieldResult?.result ? `${yieldResult.result.predicted_yield_tonnes_per_ha} t/ha` : "Ready"} detail={yieldResult?.result ? "Model output" : "6 planning inputs"} /><Metric icon={<FileImage />} label="Plant health" value={disease?.result ? "Analyzed" : "Ready"} detail={disease?.result ? `${Math.round(disease.result.confidence * 100)}% confidence` : "JPG or PNG · max 10 MB"} /></section>
    <section className="section-heading"><div><div className="eyebrow">YOUR WORKSPACE</div><h2>Choose a workflow</h2></div><button className="text-button" onClick={() => onNavigate("history")}>View all history <ArrowRight size={15} /></button></section>
    <div className="workflow-grid"><WorkflowCard icon={<Sprout />} number="01" title="Find a suitable crop" text="Enter NPK, soil pH, rainfall, temperature, and humidity to get a ranked crop result." action="Open crop fit" onClick={() => onNavigate("crop")} /><WorkflowCard icon={<CloudSun />} number="02" title="Plan expected yield" text="Estimate yield from region, crop, year, rainfall, pesticides, and average temperature." action="Open yield forecast" onClick={() => onNavigate("yield")} /><WorkflowCard icon={<FileImage />} number="03" title="Screen plant health" text="Upload a clear leaf image and receive a disease prediction with confidence and treatment context." action="Upload leaf image" onClick={() => onNavigate("disease")} /></div>
    <section className="history-preview"><div className="section-heading"><div><div className="eyebrow">RECENT ACTIVITY</div><h2>Farmer query history</h2></div><span className="count-badge">{history.length} saved</span></div>{history.length ? <HistoryRows items={history.slice(0, 4)} /> : <EmptyState text="Your successful predictions will appear here." />}</section>
  </>;
}

function WorkflowCard({ icon, number, title, text, action, onClick }) { return <article className="workflow-card"><div className="card-icon">{icon}</div><span className="card-number">{number}</span><h3>{title}</h3><p>{text}</p><button className="text-button" onClick={onClick}>{action} <ArrowRight size={15} /></button></article>; }
function Metric({ icon, label, value, detail }) { return <div className="metric"><span className="metric-icon">{icon}</span><div><small>{label}</small><strong>{value}</strong><span>{detail}</span></div></div>; }

function FormCard({ title, eyebrow, description, children, onSubmit, submitLabel, loading }) { return <section className="panel form-panel"><div className="eyebrow">{eyebrow}</div><h2>{title}</h2><p className="panel-intro">{description}</p><form onSubmit={(event) => { event.preventDefault(); onSubmit(event); }}>{children}<button className="button primary full" disabled={loading}>{loading ? <><Loader2 className="spin" size={17} /> Working…</> : <>{submitLabel} <ArrowRight size={16} /></>}</button></form></section>; }
function NumberField({ label, name, value, onChange, min, max, step = "any" }) { return <label className="field"><span>{label}</span><input required type="number" name={name} value={value} min={min} max={max} step={step} onChange={(event) => onChange(event.target.value)} /><small>{min}–{max}</small></label>; }
function CropPanel({ onSubmit, state }) { const [form, setForm] = useState(cropDefaults); const update = (name, value) => setForm((current) => ({ ...current, [name]: Number(value) })); return <div className="split-layout"><FormCard eyebrow="01 · CROP FIT" title="Find a suitable crop" description="Use the same seven features expected by the trained crop classifier." onSubmit={() => onSubmit(form)} submitLabel="Generate recommendation" loading={state?.loading}><div className="field-grid">{[["N", "Nitrogen (N)", 0, 200], ["P", "Phosphorus (P)", 0, 200], ["K", "Potassium (K)", 0, 250], ["temperature", "Temperature (°C)", -10, 60], ["humidity", "Humidity (%)", 0, 100], ["ph", "Soil pH", 0, 14], ["rainfall", "Rainfall (mm)", 0, 500]].map(([name, label, min, max]) => <NumberField key={name} label={label} name={name} value={form[name]} min={min} max={max} onChange={(value) => update(name, value)} />)}</div></FormCard><ResultCard eyebrow="MODEL OUTPUT" title={state?.result ? state.result.recommended_crop : "Your crop fit appears here"} loading={state?.loading} error={state?.error}>{state?.result ? <><div className="result-highlight"><strong>{Math.round(state.result.confidence * 100)}%</strong><span>model confidence</span></div><h4>Top alternatives</h4><div className="rank-list">{state.result.top_3_alternatives.map((item, index) => <div key={item.crop}><span>0{index + 1}</span><b>{item.crop}</b><em>{Math.round(item.confidence * 100)}%</em></div>)}</div><p className="disclaimer">Benchmark prediction only. Confirm with local agronomic knowledge and field conditions.</p></> : <EmptyState text="Submit the form to see a ranked recommendation." />}</ResultCard></div>; }
function YieldPanel({ onSubmit, state }) { const [form, setForm] = useState(yieldDefaults); const update = (name, value) => setForm((current) => ({ ...current, [name]: ["Area", "Item"].includes(name) ? value : Number(value) })); return <div className="split-layout"><FormCard eyebrow="02 · YIELD FORECAST" title="Plan expected yield" description="Estimate output from the same features used by the trained regression pipeline." onSubmit={() => onSubmit(form)} submitLabel="Predict yield" loading={state?.loading}><div className="field-grid"><label className="field"><span>Area / region</span><input required value={form.Area} onChange={(event) => update("Area", event.target.value)} /><small>e.g. India</small></label><label className="field"><span>Crop item</span><input required value={form.Item} onChange={(event) => update("Item", event.target.value)} /><small>e.g. Rice, paddy</small></label><NumberField label="Year" name="Year" value={form.Year} min={1960} max={2030} step="1" onChange={(value) => update("Year", value)} /><NumberField label="Rainfall (mm/year)" name="average_rain_fall_mm_per_year" value={form.average_rain_fall_mm_per_year} min={0} max={10000} onChange={(value) => update("average_rain_fall_mm_per_year", value)} /><NumberField label="Pesticides (tonnes)" name="pesticides_tonnes" value={form.pesticides_tonnes} min={0} max={100000} onChange={(value) => update("pesticides_tonnes", value)} /><NumberField label="Average temperature" name="avg_temp" value={form.avg_temp} min={-30} max={50} onChange={(value) => update("avg_temp", value)} /></div></FormCard><ResultCard eyebrow="MODEL OUTPUT" title={state?.result ? `${state.result.predicted_yield_tonnes_per_ha} tonnes / ha` : "Your yield forecast appears here"} loading={state?.loading} error={state?.error}>{state?.result ? <><div className="yield-number">{state.result.predicted_yield_hg_per_ha.toLocaleString()} <span>hg / ha</span></div><p className="disclaimer">This estimate is a model output, not a guaranteed harvest. Weather, variety, soil, and farm practice can change the result.</p></> : <EmptyState text="Submit the form to see a yield estimate." />}</ResultCard></div>; }
function DiseasePanel({ onSubmit, state }) { return <div className="split-layout"><section className="panel form-panel"><div className="eyebrow">03 · PLANT HEALTH</div><h2>Screen a leaf image</h2><p className="panel-intro">Upload a clear JPG or PNG image. The file is sent directly to the FastAPI disease endpoint.</p><label className="dropzone"><UploadCloud size={30} /><strong>Choose a leaf image</strong><span>JPG or PNG · maximum 10 MB</span><input type="file" accept="image/jpeg,image/png" onChange={(event) => onSubmit(event.target.files?.[0])} /></label>{state?.preview && <div className="preview"><img src={state.preview} alt="Selected leaf preview" /><span>{state.fileName}</span></div>}{state?.error && <InlineError text={state.error} />}</section><ResultCard eyebrow="MODEL OUTPUT" title={state?.result ? state.result.predicted_disease.replaceAll("_", " ") : "Your plant health result appears here"} loading={state?.loading} error={state?.error}>{state?.result ? <><div className="result-highlight"><strong>{Math.round(state.result.confidence * 100)}%</strong><span>{state.result.low_confidence_warning ? "low confidence — inspect carefully" : "model confidence"}</span></div><p className="treatment"><b>Treatment suggestion</b>{state.result.treatment_suggestion}</p><p className="disclaimer">Educational image screening only. This is not an official diagnosis. Consult a local agriculture expert before treatment.</p></> : <EmptyState text="Choose an image to start analysis." />}</ResultCard></div>; }
function ResultCard({ eyebrow, title, children, loading, error }) { return <section className="panel result-panel"><div className="eyebrow">{eyebrow}</div><h2>{title}</h2>{error ? <InlineError text={error} /> : loading ? <div className="loading-box"><Loader2 className="spin" /><span>Calling the prediction API…</span></div> : children}</section>; }
function HistoryPanel({ items, onRefresh }) { return <section className="panel history-panel"><div className="section-heading"><div><div className="eyebrow">SAVED QUERIES</div><h2>Farmer query history</h2><p className="panel-intro">Successful prediction responses saved by the API for <b>{farmerId}</b>.</p></div><button className="button ghost" onClick={onRefresh}><RefreshCw size={16} /> Refresh</button></div>{items.length ? <HistoryRows items={items} /> : <EmptyState text="No saved queries yet. Run a prediction to create your first history record." />}</section>; }
function HistoryRows({ items }) { return <div className="history-list">{items.map((item) => <div className="history-row" key={item.id}><span className="history-icon">{item.query_type === "disease_detection" ? <FileImage size={17} /> : item.query_type === "yield_prediction" ? <CloudSun size={17} /> : <Sprout size={17} />}</span><div><b>{item.query_type.replaceAll("_", " ")}</b><small>{new Date(item.created_at).toLocaleString()}</small></div><strong>{item.response_payload.recommended_crop || item.response_payload.predicted_disease || `${item.response_payload.predicted_yield_tonnes_per_ha || "—"} t/ha`}</strong></div>)}</div>; }
function EmptyState({ text }) { return <div className="empty-state"><Leaf size={22} /><span>{text}</span></div>; }
function InlineError({ text }) { return <div className="inline-error"><XCircle size={17} />{text}</div>; }

export default App;
