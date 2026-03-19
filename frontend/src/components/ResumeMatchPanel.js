function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function SkillChipList({ title, skills, emptyLabel, chipClassName }) {
  return (
    <article className="rounded-[24px] border border-slate-200 bg-white/80 p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
      <div className="flex items-center justify-between gap-3">
        <h4 className="text-lg font-semibold tracking-[-0.03em] text-slate-900">{title}</h4>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{skills.length}</span>
      </div>

      {skills.length ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {skills.map((skill) => (
            <span key={skill} className={`rounded-full border px-3 py-1 text-sm font-semibold ${chipClassName}`}>
              {skill}
            </span>
          ))}
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-500">{emptyLabel}</p>
      )}
    </article>
  );
}

function ResumeMatchPanel({ match }) {
  if (!match) {
    return null;
  }

  const summaryCards = [
    {
      key: "percentage",
      label: "Match Percentage",
      value: formatPercent(match.match_percentage),
      accent: "from-[#ecfeff] to-white"
    },
    {
      key: "matched",
      label: "Matched Skills",
      value: match.matched_skill_count || 0,
      accent: "from-[#ecfdf5] to-white"
    },
    {
      key: "missing",
      label: "Missing Skills",
      value: match.missing_skill_count || 0,
      accent: "from-[#fff1f2] to-white"
    }
  ];

  return (
    <section className="dashboard-panel p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="eyebrow">Matching</p>
          <h3 className="panel-title mt-3 text-2xl">Resume Skill Matching</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Resume skills are predicted with the same pipeline, then compared with the current job skill predictions.
          </p>
        </div>

        <div className="rounded-[24px] border border-teal-100 bg-teal-50 px-5 py-4 text-right">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">Score</p>
          <p className="mt-2 font-display text-4xl font-bold tracking-[-0.05em] text-teal-900">
            {formatPercent(match.match_percentage)}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        {summaryCards.map((card) => (
          <article
            key={card.key}
            className={`rounded-[24px] border border-white/70 bg-gradient-to-br ${card.accent} p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]`}
          >
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">{card.label}</p>
            <p className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-slate-900">{card.value}</p>
          </article>
        ))}
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <SkillChipList
          title="Matched Skills"
          skills={match.matched_skills || []}
          emptyLabel="No matched skills found yet."
          chipClassName="border-emerald-200 bg-emerald-50 text-emerald-700"
        />
        <SkillChipList
          title="Missing Skills"
          skills={match.missing_skills || []}
          emptyLabel="No missing skills. The resume covers all predicted job skills."
          chipClassName="border-rose-200 bg-rose-50 text-rose-700"
        />
      </div>
    </section>
  );
}

export default ResumeMatchPanel;
