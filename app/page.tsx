"use client";
import { useState } from "react";
import useSWR from "swr";
import { fetcher, startAnalysis } from "@/lib/api";
import AnalysisResult from "@/components/AnalysisResult";
import { Loader2, Search } from "lucide-react";

export default function ESGTracker() {
  const [url, setUrl] = useState("");
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  // Auto-polling: If we have a job ID, check status every 3 seconds
  const { data, error } = useSWR(
    activeJobId ? `http://localhost:8000/status/${activeJobId}` : null,
    fetcher,
    { refreshInterval: 3000 }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await startAnalysis(url);
    setActiveJobId(result.job_id);
  };

  const isProcessing = data?.status === "pending" || data?.status === "processing";

  return (
    <main className="max-w-3xl mx-auto py-12 px-4">
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Autonomous ESG Tracker</h1>
        <p className="text-slate-500 mt-2">Audit supply chain ethics using real-time AI analysis.</p>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 text-slate-400" size={18} />
          <input
            type="url"
            placeholder="Paste news article URL..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        </div>
        <button 
          disabled={isProcessing}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {isProcessing ? <Loader2 className="animate-spin" /> : "Analyze"}
        </button>
      </form>

      {/* State Transitions */}
      {isProcessing && (
        <div className="text-center p-12 border-2 border-dashed rounded-xl">
          <Loader2 className="animate-spin mx-auto text-indigo-500 mb-4" size={32} />
          <p className="text-slate-600 font-medium">AI is reading the article and identifying entities...</p>
        </div>
      )}

      {data?.status === "completed" && <AnalysisResult data={data.result} />}
      
      {error && <p className="text-red-500">Failed to connect to backend engine.</p>}
    </main>
  );
}