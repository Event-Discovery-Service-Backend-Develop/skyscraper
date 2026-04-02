import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { CalendarDays, MapPin, Search, Tag } from "lucide-react";

const API_BASE_URL = import.meta?.env?.VITE_API_BASE_URL || "";

const TAG_STYLES = {
  AI: "bg-blue-100 text-blue-700 border-blue-200/80",
  Security: "bg-rose-100 text-rose-700 border-rose-200/80",
  Physics: "bg-violet-100 text-violet-700 border-violet-200/80",
  "Data Science": "bg-emerald-100 text-emerald-700 border-emerald-200/80",
  "Software Engineering": "bg-indigo-100 text-indigo-700 border-indigo-200/80",
  default: "bg-slate-100 text-slate-700 border-slate-200/80",
};

const STATUS_OPTIONS = [
  { value: "", label: "All" },
  { value: "true", label: "Processed" },
  { value: "false", label: "Raw" },
];

function getTagClass(tag) {
  return TAG_STYLES[tag] || TAG_STYLES.default;
}

function parseKeywords(value) {
  if (!value) return [];
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function getDaysToDeadline(deadline) {
  if (!deadline) return null;
  const oneDay = 24 * 60 * 60 * 1000;
  const diff = new Date(deadline).setHours(0, 0, 0, 0) - new Date().setHours(0, 0, 0, 0);
  return Math.floor(diff / oneDay);
}

function SearchBar({ value, onChange }) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search by conference title, location, or tags..."
        className="w-full rounded-xl border border-slate-200/70 bg-white/70 py-2.5 pl-10 pr-4 text-sm text-slate-800 shadow-sm backdrop-blur-sm outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-200/70"
      />
    </div>
  );
}

function FilterSidebar({
  tags,
  selectedTag,
  selectedYear,
  selectedStatus,
  yearOptions,
  onTagChange,
  onYearChange,
  onStatusChange,
}) {
  return (
    <aside className="rounded-2xl border border-slate-200/60 bg-white/65 p-4 shadow-sm backdrop-blur-md">
      <h2 className="text-sm font-semibold text-slate-900">Filters</h2>

      <div className="mt-4 space-y-5">
        <section>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Category</p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onTagChange("")}
              className={`rounded-lg border px-3 py-1.5 text-xs transition ${
                selectedTag
                  ? "border-slate-200 bg-white text-slate-600 hover:border-indigo-200"
                  : "border-indigo-200 bg-indigo-50 text-indigo-700"
              }`}
            >
              All
            </button>
            {tags.map((tag) => (
              <button
                key={tag}
                onClick={() => onTagChange(tag)}
                className={`rounded-lg border px-3 py-1.5 text-xs transition ${
                  selectedTag === tag
                    ? "border-indigo-200 bg-indigo-50 text-indigo-700"
                    : "border-slate-200 bg-white text-slate-600 hover:border-indigo-200"
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </section>

        <section>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Year</p>
          <select
            value={selectedYear}
            onChange={(e) => onYearChange(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-indigo-400"
          >
            <option value="">All years</option>
            {yearOptions.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </section>

        <section>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Processing Status</p>
          <div className="space-y-2">
            {STATUS_OPTIONS.map((option) => (
              <label key={option.value || "all"} className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
                <input
                  type="radio"
                  name="processed"
                  value={option.value}
                  checked={selectedStatus === option.value}
                  onChange={(e) => onStatusChange(e.target.value)}
                  className="h-4 w-4 border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                {option.label}
              </label>
            ))}
          </div>
        </section>
      </div>
    </aside>
  );
}

function ConferenceCard({ conference }) {
  const tags = parseKeywords(conference.keywords);
  const days = getDaysToDeadline(conference.deadline);
  const urgent = typeof days === "number" && days >= 0 && days < 7;

  return (
    <motion.article
      whileHover={{ y: -4, boxShadow: "0 14px 34px rgba(15, 23, 42, 0.10)" }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="rounded-2xl border border-slate-200/60 bg-white/70 p-5 shadow-sm backdrop-blur-md"
    >
      <div className="flex items-start justify-between gap-4">
        <h3 className="line-clamp-2 text-base font-semibold text-slate-900">{conference.title || "Untitled conference"}</h3>
        <span
          className={`shrink-0 rounded-full px-2 py-1 text-[11px] font-medium ${
            conference.is_processed ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
          }`}
        >
          {conference.is_processed ? "Processed" : "Raw"}
        </span>
      </div>

      <div className="mt-4 space-y-2 text-sm text-slate-600">
        <p className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-slate-400" />
          {conference.location || "Location is not specified"}
        </p>
        <p className="flex items-center gap-2">
          <CalendarDays className="h-4 w-4 text-slate-400" />
          Event: {conference.event_date || "TBD"}
        </p>
        <p className="flex items-center gap-2">
          <Tag className="h-4 w-4 text-slate-400" />
          ID: {conference.wikicfp_id}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {tags.length === 0 ? (
          <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-500">No tags yet</span>
        ) : (
          tags.map((tag) => (
            <span key={tag} className={`rounded-md border px-2 py-1 text-xs font-medium ${getTagClass(tag)}`}>
              {tag}
            </span>
          ))
        )}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-slate-200/70 pt-3">
        <p className="text-xs text-slate-500">Deadline: {conference.deadline || "Not available"}</p>
        {urgent && (
          <span className="inline-flex items-center gap-2 text-xs font-medium text-rose-600">
            <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-rose-500" />
            {days === 0 ? "Today" : `${days} days left`}
          </span>
        )}
      </div>
    </motion.article>
  );
}

function ConferenceSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border border-slate-200/60 bg-white/70 p-5">
      <div className="h-4 w-3/4 rounded bg-slate-200" />
      <div className="mt-4 h-3 w-full rounded bg-slate-200" />
      <div className="mt-2 h-3 w-5/6 rounded bg-slate-200" />
      <div className="mt-4 flex gap-2">
        <div className="h-6 w-16 rounded bg-slate-200" />
        <div className="h-6 w-20 rounded bg-slate-200" />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white/60 p-10 text-center backdrop-blur-sm">
      <h3 className="text-lg font-semibold text-slate-900">No conferences found</h3>
      <p className="mt-2 text-sm text-slate-500">Try changing search text or relaxing one of the filters.</p>
    </div>
  );
}

export default function ConferenceDashboard() {
  const [conferences, setConferences] = useState([]);
  const [count, setCount] = useState(0);
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);

  const [search, setSearch] = useState("");
  const [selectedTag, setSelectedTag] = useState("");
  const [selectedYear, setSelectedYear] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const knownTags = useMemo(
    () => ["AI", "Security", "Physics", "Data Science", "Software Engineering"],
    []
  );

  const yearOptions = useMemo(() => {
    const now = new Date().getFullYear();
    return Array.from({ length: 10 }, (_, i) => String(now - i));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchConferences();
    }, 320);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, selectedTag, selectedYear, selectedStatus, page]);

  async function fetchConferences() {
    try {
      setLoading(true);
      setError("");

      const params = {
        page,
        ordering: "-event_date",
      };
      if (search) params.search = search;
      if (selectedTag) params.tag = selectedTag;
      if (selectedYear) params.year = selectedYear;
      if (selectedStatus) params.processed = selectedStatus;

      const response = await axios.get(`${API_BASE_URL}/api/conferences/`, { params });
      setConferences(response.data?.results || []);
      setCount(response.data?.count || 0);
      setNextUrl(response.data?.next || null);
      setPrevUrl(response.data?.previous || null);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load conferences");
      setConferences([]);
      setCount(0);
      setNextUrl(null);
      setPrevUrl(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 font-sans text-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-8 lg:px-6">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 md:text-3xl">Event Discovery Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">Track calls for papers, deadlines, and trending research domains.</p>
        </header>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
          <div className="lg:col-span-3">
            <FilterSidebar
              tags={knownTags}
              selectedTag={selectedTag}
              selectedYear={selectedYear}
              selectedStatus={selectedStatus}
              yearOptions={yearOptions}
              onTagChange={(value) => {
                setSelectedTag(value);
                setPage(1);
              }}
              onYearChange={(value) => {
                setSelectedYear(value);
                setPage(1);
              }}
              onStatusChange={(value) => {
                setSelectedStatus(value);
                setPage(1);
              }}
            />
          </div>

          <section className="space-y-4 lg:col-span-9">
            <SearchBar
              value={search}
              onChange={(value) => {
                setSearch(value);
                setPage(1);
              }}
            />

            <div className="flex items-center justify-between text-sm text-slate-500">
              <span>{count.toLocaleString()} conferences found</span>
              <span>Page {page}</span>
            </div>

            {error ? (
              <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
            ) : null}

            {loading ? (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, idx) => (
                  <ConferenceSkeleton key={idx} />
                ))}
              </div>
            ) : conferences.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {conferences.map((conference) => (
                  <ConferenceCard key={conference.id} conference={conference} />
                ))}
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                disabled={!prevUrl || loading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Previous
              </button>
              <button
                disabled={!nextUrl || loading}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
