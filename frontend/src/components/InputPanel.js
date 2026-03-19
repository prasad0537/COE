function InputPanel({
  text,
  resumeText,
  jobFileName,
  resumeFileName,
  threshold,
  topK,
  minPredictions,
  showJson,
  isSubmitting,
  isMatching,
  isLoadingSample,
  isUploadingJob,
  isUploadingResume,
  onTextChange,
  onResumeTextChange,
  onThresholdChange,
  onTopKChange,
  onMinPredictionsChange,
  onShowJsonChange,
  onImportJobFile,
  onImportResumeFile,
  onLoadSample,
  onSubmit,
  onMatch,
  onClear
}) {
  async function handleFileImport(event, onImport) {
    const [file] = event.target.files || [];
    if (!file) {
      return;
    }

    onImport(file);
    event.target.value = "";
  }

  return (
    <aside className="dashboard-panel h-fit p-6 lg:sticky lg:top-6">
      <div className="mb-6">
        <p className="eyebrow">Input</p>
        <h2 className="panel-title mt-3 text-2xl">Job + Resume</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Paste text or upload TXT, PDF, or DOCX files for the job description and candidate resume.
        </p>
      </div>

      <div className="space-y-5">
        <div>
          <label className="field-label" htmlFor="job-description">
            Job Description
          </label>
          <textarea
            id="job-description"
            className="field-input min-h-[360px] resize-y"
            placeholder="Paste a job description here or upload a TXT, PDF, or DOCX file..."
            value={text}
            onChange={(event) => onTextChange(event.target.value)}
          />
          {jobFileName ? <p className="mt-2 text-xs font-medium text-slate-500">Loaded from: {jobFileName}</p> : null}
        </div>

        <div>
          <label className="field-label" htmlFor="candidate-resume">
            Candidate Resume
          </label>
          <textarea
            id="candidate-resume"
            className="field-input min-h-[260px] resize-y"
            placeholder="Paste a candidate resume here or upload a TXT, PDF, or DOCX file..."
            value={resumeText}
            onChange={(event) => onResumeTextChange(event.target.value)}
          />
          {resumeFileName ? <p className="mt-2 text-xs font-medium text-slate-500">Loaded from: {resumeFileName}</p> : null}
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="field-label" htmlFor="threshold">
              Threshold
            </label>
            <input
              id="threshold"
              className="field-input"
              type="number"
              min="0"
              max="1"
              step="0.01"
              placeholder="Model default"
              value={threshold}
              onChange={(event) => onThresholdChange(event.target.value)}
            />
          </div>

          <div>
            <label className="field-label" htmlFor="top-k">
              Top K
            </label>
            <input
              id="top-k"
              className="field-input"
              type="number"
              min="1"
              max="50"
              step="1"
              value={topK}
              onChange={(event) => onTopKChange(event.target.value)}
            />
          </div>

          <div>
            <label className="field-label" htmlFor="min-predictions">
              Minimum Results
            </label>
            <input
              id="min-predictions"
              className="field-input"
              type="number"
              min="1"
              max="20"
              step="1"
              value={minPredictions}
              onChange={(event) => onMinPredictionsChange(event.target.value)}
            />
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <button
            type="button"
            className="action-button bg-gradient-to-r from-[#f97316] via-[#ef4444] to-[#dc2626] text-white shadow-lg shadow-orange-500/20 hover:-translate-y-0.5"
            onClick={onSubmit}
            disabled={isSubmitting || isMatching}
          >
            {isSubmitting ? "Predicting..." : "Predict Skills"}
          </button>
          <button
            type="button"
            className="action-button bg-gradient-to-r from-[#0f766e] to-[#155e75] text-white shadow-lg shadow-teal-500/20 hover:-translate-y-0.5"
            onClick={onMatch}
            disabled={isSubmitting || isMatching}
          >
            {isMatching ? "Matching..." : "Match Resume"}
          </button>
          <button
            type="button"
            className="action-button border border-slate-300 bg-white text-ink hover:border-slate-400 hover:bg-slate-50"
            onClick={onLoadSample}
            disabled={isLoadingSample}
          >
            {isLoadingSample ? "Loading..." : "Use Sample"}
          </button>
          <button
            type="button"
            className="action-button border border-slate-300 bg-white text-ink hover:border-slate-400 hover:bg-slate-50"
            onClick={onClear}
          >
            Clear
          </button>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <label className="action-button cursor-pointer border border-dashed border-slate-300 bg-slate-50 text-ink hover:border-slate-400 hover:bg-white">
            {isUploadingJob ? "Uploading Job File..." : "Upload Job TXT / PDF / DOCX"}
            <input
              className="hidden"
              type="file"
              accept=".txt,.pdf,.docx,.doc"
              disabled={isUploadingJob || isUploadingResume}
              onChange={(event) => handleFileImport(event, onImportJobFile)}
            />
          </label>

          <label className="action-button cursor-pointer border border-dashed border-slate-300 bg-slate-50 text-ink hover:border-slate-400 hover:bg-white">
            {isUploadingResume ? "Uploading Resume File..." : "Upload Resume TXT / PDF / DOCX"}
            <input
              className="hidden"
              type="file"
              accept=".txt,.pdf,.docx,.doc"
              disabled={isUploadingJob || isUploadingResume}
              onChange={(event) => handleFileImport(event, onImportResumeFile)}
            />
          </label>
        </div>

        <p className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs font-medium leading-5 text-slate-500">
          Supports TXT, PDF, and DOCX uploads up to 10 MB. If you have an older Word `.doc` file, convert it to
          `.docx` or PDF first.
        </p>

        <label className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3">
          <input
            type="checkbox"
            checked={showJson}
            onChange={(event) => onShowJsonChange(event.target.checked)}
          />
          <span className="text-sm font-medium text-slate-700">Show raw JSON</span>
        </label>
      </div>
    </aside>
  );
}

export default InputPanel;
