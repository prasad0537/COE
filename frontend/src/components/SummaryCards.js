function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function SummaryCards({ summary, skills }) {
  const averageConfidence =
    skills.length > 0 ? skills.reduce((total, skill) => total + (skill.confidence || 0), 0) / skills.length : 0;

  const cardDefinitions = [
    {
      key: "total",
      label: "Predicted Skills",
      value: summary?.total_predicted_skills || skills.length || 0,
      accent: "from-[#fff3e8] to-white"
    },
    {
      key: "top",
      label: "Top Category",
      value: summary?.top_category || "N/A",
      accent: "from-[#e6f7f5] to-white"
    },
    {
      key: "threshold",
      label: "Threshold",
      value: summary?.threshold ?? "N/A",
      accent: "from-[#edf2ff] to-white"
    },
    {
      key: "average",
      label: "Average Confidence",
      value: formatPercent(averageConfidence),
      accent: "from-[#fff0f3] to-white"
    }
  ];

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cardDefinitions.map((card) => (
        <article
          key={card.key}
          className={`rounded-[28px] border border-white/70 bg-gradient-to-br ${card.accent} p-5 shadow-[0_20px_50px_rgba(15,23,42,0.08)]`}
        >
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">{card.label}</p>
          <p className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-slate-900">
            {card.value}
          </p>
        </article>
      ))}
    </section>
  );
}

export default SummaryCards;
