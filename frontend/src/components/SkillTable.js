function formatConfidence(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function SkillTable({ skills }) {
  return (
    <section className="dashboard-panel overflow-hidden p-6">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <p className="eyebrow">Predictions</p>
          <h3 className="panel-title mt-3 text-2xl">Ranked Skill Matches</h3>
        </div>
        <p className="text-sm text-slate-500">{skills.length} results</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {skills.map((skill, index) => (
          <article
            key={`${skill.name}-${skill.category}`}
            className="rounded-[24px] border border-slate-200 bg-white/80 p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">#{index + 1}</p>
                <h4 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">{skill.name}</h4>
              </div>
              <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
                {formatConfidence(skill.confidence)}
              </span>
            </div>

            <div className="mt-4">
              <span className="inline-flex rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-semibold text-orange-700">
                {skill.category}
              </span>
            </div>

            <div className="mt-5">
              <div className="mb-2 flex items-center justify-between text-sm text-slate-500">
                <span>Confidence</span>
                <span>{formatConfidence(skill.confidence)}</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#fb923c] via-[#ef4444] to-[#0f766e]"
                  style={{ width: `${Math.max(8, Math.round((skill.confidence || 0) * 100))}%` }}
                />
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default SkillTable;
