import Link from "next/link";

const DashboardCard = ({
  title,
  description,
  href,
  color,
}: {
  title: string;
  description: string;
  href: string;
  color: string;
}) => (
  <Link
    href={href}
    className="group relative overflow-hidden rounded-2xl bg-zinc-900 border border-zinc-800 p-8 hover:border-zinc-700 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 block"
  >
    <div
      className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300 bg-gradient-to-br ${color}`}
    />
    <h3 className="text-xl font-bold mb-3 text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-zinc-400">
      {title}
    </h3>
    <p className="text-zinc-400 text-sm leading-relaxed">{description}</p>
  </Link>
);

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto py-10">
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-black mb-6 bg-gradient-to-b from-white to-zinc-600 bg-clip-text text-transparent tracking-tight">
          Welcome to Martian
        </h1>
        <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
          Your command center for low-volatility growth and arbitrage strategies.
          <br />
          <span className="text-purple-400 text-sm mt-2 block font-medium">
            Let's find some alpha today. 🚀
          </span>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Mars Strategy"
          description="Identify low-volatility, high-growth stocks using our proprietary Gaussian filtering algorithm. Target stable compounders."
          href="/mars"
          color="from-purple-600 to-pink-600"
        />
        <DashboardCard
          title="Visualization"
          description="Interactive Bar Chart Race visualizing stock performance over the last 15 years. See the winners emerge over time."
          href="/viz"
          color="from-cyan-500 to-blue-600"
        />
        <DashboardCard
          title="CB Arbitrage"
          description="Monitor Convertible Bond premiums and hedging opportunities in real-time."
          href="/cb"
          color="from-emerald-500 to-green-600"
        />
      </div>

      <div className="mt-20 border-t border-zinc-900 pt-10 text-center">
        <div className="inline-block p-4 rounded-full bg-zinc-900/50 border border-zinc-800 text-zinc-500 text-sm">
          🚀 System Status: <span className="text-green-500">Online</span> •
          Latest Crawl: Today 04:00 AM
        </div>
      </div>
    </div>
  );
}
