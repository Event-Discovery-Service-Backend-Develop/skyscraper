import ConferenceDashboard from "./components/ConferenceDashboard";

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* ШАПКА САЙТА */}
      <nav className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 shadow-lg shadow-indigo-200">
              <span className="text-lg font-bold text-white">S</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold tracking-tight text-slate-900 leading-none">Skyscraper</span>
              <span className="text-[10px] font-semibold uppercase tracking-widest text-indigo-600">Event Discovery</span>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
              <a href="#" className="hover:text-indigo-600 transition-colors">Dashboard</a>
              <a href="http://localhost:3000" target="_blank" className="hover:text-indigo-600 transition-colors">Monitoring</a>
            </div>
            <a href="http://localhost:8000/admin" target="_blank" 
               className="rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800 transition-all shadow-md">
              Admin Portal
            </a>
          </div>
        </div>
      </nav>

      {/* ОСНОВНОЙ КОНТЕНТ */}
      <main className="flex-grow py-8">
        <ConferenceDashboard />
      </main>

      {/* ПОДВАЛ */}
      <footer className="border-t border-slate-200 bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <p className="text-sm text-slate-500">
              © 2026 Skyscraper Project. Specialized in IT Infrastructure & Data Science.
            </p>
            <div className="flex gap-6 text-xs font-medium text-slate-400 uppercase tracking-widest">
              <span>Cybersecurity</span>
              <span>Automation</span>
              <span>Analytics</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;