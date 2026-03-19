import { useState } from "react";
import CategoryChart from "../charts/CategoryChart";
import InputPanel from "../components/InputPanel";
import JsonPreview from "../components/JsonPreview";
import ResumeMatchPanel from "../components/ResumeMatchPanel";
import SkillTable from "../components/SkillTable";
import SummaryCards from "../components/SummaryCards";
import { fetchSampleDescription, matchResumeSkills, predictSkills } from "../services/api";

function buildCategoryCounts(skills) {
  return skills.reduce((accumulator, skill) => {
    const category = skill.category || "Uncategorized";
    accumulator[category] = (accumulator[category] || 0) + 1;
    return accumulator;
  }, {});
}

function HomePage() {
  const [text, setText] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [threshold, setThreshold] = useState("");
  const [topK, setTopK] = useState("12");
  const [minPredictions, setMinPredictions] = useState("5");
  const [showJson, setShowJson] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isMatching, setIsMatching] = useState(false);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

  async function handleSubmit() {
    if (!text.trim()) {
      setError("Job description text is empty. Paste text, upload a file, or load the sample.");
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      const payload = await predictSkills({
        text,
        threshold: threshold === "" ? undefined : Number(threshold),
        top_k: Number(topK),
        min_predictions: Number(minPredictions)
      });
      setResult(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleLoadSample() {
    setError("");
    setIsLoadingSample(true);

    try {
      const sample = await fetchSampleDescription();
      setText(sample);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoadingSample(false);
    }
  }

  async function handleMatch() {
    if (!text.trim()) {
      setError("Job description text is empty. Paste text, upload a file, or load the sample.");
      return;
    }

    if (!resumeText.trim()) {
      setError("Resume text is empty. Paste the candidate resume or upload a text file.");
      return;
    }

    setError("");
    setIsMatching(true);

    try {
      const payload = await matchResumeSkills({
        job_text: text,
        resume_text: resumeText,
        threshold: threshold === "" ? undefined : Number(threshold),
        top_k: Number(topK),
        min_predictions: Number(minPredictions)
      });
      setResult(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsMatching(false);
    }
  }

  function handleClear() {
    setText("");
    setResumeText("");
    setResult(null);
    setError("");
  }

  const skills = result?.predicted_skills || [];
  const categories = buildCategoryCounts(skills);
  const match = result?.match || null;

  return (
    <main className="min-h-screen bg-grid">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="relative overflow-hidden rounded-[36px] border border-white/60 bg-[linear-gradient(135deg,#0f172a_0%,#102a43_52%,#0f766e_100%)] px-6 py-8 text-white shadow-[0_28px_80px_rgba(15,23,42,0.24)] sm:px-8 lg:px-10">
          <div className="absolute inset-y-0 right-0 w-[36%] bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.18),transparent_48%)]" />
          <div className="relative grid gap-8 lg:grid-cols-[minmax(0,1fr)_260px]">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-orange-200">ML Skill Prediction</p>
              <h1 className="mt-4 max-w-3xl font-display text-4xl font-bold tracking-[-0.06em] text-white sm:text-5xl">
                Turn a job description into ranked skill predictions.
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-slate-200 sm:text-lg">
                Use the trained model to predict the most likely skills, categories, and confidence scores in one pass.
              </p>
            </div>
            <div className="grid gap-4 self-end">
              <div className="rounded-[28px] border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">Model</p>
                <p className="mt-3 text-2xl font-bold tracking-[-0.04em] text-white">Multi-label classifier</p>
              </div>
              <div className="rounded-[28px] border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-300">Output</p>
                <p className="mt-3 text-2xl font-bold tracking-[-0.04em] text-white">Skills + confidence</p>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[390px_minmax(0,1fr)] xl:grid-cols-[430px_minmax(0,1fr)]">
          <InputPanel
            text={text}
            resumeText={resumeText}
            threshold={threshold}
            topK={topK}
            minPredictions={minPredictions}
            showJson={showJson}
            isSubmitting={isSubmitting}
            isMatching={isMatching}
            isLoadingSample={isLoadingSample}
            onTextChange={setText}
            onResumeTextChange={setResumeText}
            onThresholdChange={setThreshold}
            onTopKChange={setTopK}
            onMinPredictionsChange={setMinPredictions}
            onShowJsonChange={setShowJson}
            onLoadSample={handleLoadSample}
            onSubmit={handleSubmit}
            onMatch={handleMatch}
            onClear={handleClear}
          />

          <div className="space-y-6">
            {error ? (
              <div className="dashboard-panel border border-rose-200 bg-rose-50 p-5 text-sm font-medium text-rose-700">
                {error}
              </div>
            ) : null}

            {result ? (
              <>
                <SummaryCards summary={result.summary} skills={skills} />

                {match ? <ResumeMatchPanel match={match} /> : null}

                <CategoryChart categories={categories} />

                <SkillTable skills={skills} />

                {showJson ? <JsonPreview data={result} /> : null}
              </>
            ) : (
              <div className="dashboard-panel flex min-h-[420px] items-center justify-center p-8">
                <div className="max-w-xl text-center">
                  <p className="eyebrow justify-center">Ready</p>
                  <h2 className="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-900">
                    Run the model to see ranked skill predictions.
                  </h2>
                  <p className="mt-4 text-base leading-7 text-slate-600">
                    The dashboard will show category distribution, confidence metrics, strongest predicted skills, and resume matching when you provide a candidate profile.
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default HomePage;
