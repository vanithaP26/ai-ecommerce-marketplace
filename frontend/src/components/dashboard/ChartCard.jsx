import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

function ChartCard() {

  const data = [
    {
      month: "Jan",
      sales: 4000,
    },

    {
      month: "Feb",
      sales: 3000,
    },

    {
      month: "Mar",
      sales: 5000,
    },

    {
      month: "Apr",
      sales: 4500,
    },

    {
      month: "May",
      sales: 7000,
    },

    {
      month: "Jun",
      sales: 6000,
    },
  ];

  return (
    <div className="bg-white p-8 rounded-2xl shadow">

      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold">
            Sales Analytics
          </h2>

          <p className="text-gray-500 mt-1">
            Monthly revenue overview
          </p>
        </div>

        <button className="bg-black text-white px-5 py-2 rounded-xl">
          Export
        </button>
      </div>

      <ResponsiveContainer
        width="100%"
        height={350}
      >
        <LineChart data={data}>

          <CartesianGrid
            strokeDasharray="3 3"
          />

          <XAxis dataKey="month" />

          <YAxis />

          <Tooltip />

          <Line
            type="monotone"
            dataKey="sales"
            strokeWidth={4}
          />

        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ChartCard;