import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

function CategoryChart({ categories }) {
  const data = Object.entries(categories || {})
    .map(([name, value]) => ({
      name,
      value
    }))
    .sort((left, right) => right.value - left.value);

  return (
    <section className="dashboard-panel p-6">
      <div className="mb-6">
        <p className="eyebrow">Breakdown</p>
        <h3 className="panel-title mt-3 text-2xl">Category Distribution</h3>
      </div>
      <div className="h-[320px]">
        {data.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 6, right: 30, left: 8, bottom: 6 }}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: "#64748b" }} />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#334155", fontSize: 12 }}
              />
              <Tooltip
                cursor={{ fill: "rgba(15, 23, 42, 0.04)" }}
                contentStyle={{
                  borderRadius: 16,
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 20px 40px rgba(15, 23, 42, 0.12)"
                }}
              />
              <Bar dataKey="value" fill="#0f766e" radius={[0, 12, 12, 0]} barSize={24}>
                <LabelList dataKey="value" position="right" fill="#0f172a" fontSize={12} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center rounded-[24px] border border-dashed border-slate-300 bg-slate-50 text-sm text-slate-500">
            No data
          </div>
        )}
      </div>
    </section>
  );
}

export default CategoryChart;
