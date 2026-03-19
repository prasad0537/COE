function JsonPreview({ data }) {
  return (
    <section className="dashboard-panel overflow-hidden">
      <div className="border-b border-slate-200 px-6 py-5">
        <p className="eyebrow">Debug</p>
        <h3 className="panel-title mt-3">Raw Response</h3>
      </div>
      <pre className="overflow-x-auto bg-[#0f172a] p-6 font-mono text-sm leading-7 text-slate-100">
        {JSON.stringify(data, null, 2)}
      </pre>
    </section>
  );
}

export default JsonPreview;
