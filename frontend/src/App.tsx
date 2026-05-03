import { useState, useEffect } from 'react';
import axios from 'axios';
import { Brain, Send, Search, Sparkles, Clock, MapPin, Trash2, RefreshCw } from 'lucide-react';

interface Memory {
  id: string;
  content: string;
  metadata: any;
}

function App() {
  const [content, setContent] = useState('');
  const [query, setQuery] = useState('');
  const [chatAnswer, setChatAnswer] = useState('');
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [memories, setMemories] = useState<Memory[]>([]);

  const fetchMemories = async () => {
    try {
      const res = await axios.get('/api/memories');
      setMemories(res.data);
    } catch (err) {
      console.error('Failed to fetch memories', err);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  const handleIngest = async () => {
    if (!content) return;
    setLoading(true);
    try {
      await axios.post('/api/ingest', { content, metadata: { location: "Local Browser" } });
      setContent('');
      fetchMemories();
    } catch (err) {
      console.error(err);
      alert('Encoding Failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Forget this memory?')) return;
    try {
      await axios.delete(`/api/memories/${id}`);
      fetchMemories();
    } catch (err) {
      console.error('Delete failed', err);
    }
  };

  const handleChat = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const res = await axios.post('/api/chat', { message: query });
      setChatAnswer(res.data.answer);
      setSources(res.data.sources || []);
    } catch (err) {
      console.error(err);
      setChatAnswer('Error connecting to the brain.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-mnemo-bg text-mnemo-text p-6 md:p-12 font-sans">
      <header className="max-w-4xl mx-auto mb-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-mnemo-primary/20 rounded-2xl">
            <Brain className="w-8 h-8 text-mnemo-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tighter text-white">MNEMOSYNE</h1>
            <p className="text-zinc-500 text-sm uppercase tracking-widest font-medium">Cognitive Archiving System</p>
          </div>
        </div>
        <div className="hidden md:block">
          <div className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-full flex items-center gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-widest">Neural Link Active</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {/* Ingestion Section */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 mb-2 text-zinc-400">
              <Sparkles className="w-4 h-4" />
              <h2 className="text-xs font-bold uppercase tracking-widest">Ingest Memory</h2>
            </div>
            <div className="bg-mnemo-card border border-zinc-800 p-6 rounded-3xl shadow-2xl">
              <textarea 
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="What are you thinking about right now?"
                className="w-full h-40 bg-transparent border-none focus:ring-0 text-lg resize-none placeholder:text-zinc-700 text-white"
              />
              <div className="flex justify-between items-center mt-4">
                <div className="flex gap-4 text-zinc-600">
                  <MapPin className="w-4 h-4" />
                  <Clock className="w-4 h-4" />
                </div>
                <button 
                  onClick={handleIngest}
                  disabled={loading}
                  className="bg-mnemo-primary hover:bg-blue-600 disabled:opacity-50 text-white px-6 py-2 rounded-full font-medium transition-all flex items-center gap-2"
                >
                  {loading ? 'Encoding...' : 'Store Memory'}
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </section>

          {/* Query Section */}
          <section className="space-y-6">
            <div className="flex items-center gap-2 mb-2 text-zinc-400">
              <Search className="w-4 h-4" />
              <h2 className="text-xs font-bold uppercase tracking-widest">Retrieve & Synthesize</h2>
            </div>
            <div className="bg-mnemo-card border border-zinc-800 p-6 rounded-3xl shadow-2xl flex flex-col h-[280px]">
              <div className="flex gap-3 mb-4">
                <input 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Ask your digital twin..."
                  className="flex-1 bg-zinc-900 border border-zinc-800 rounded-full px-5 py-2 focus:outline-none focus:border-mnemo-primary transition-colors text-white"
                />
                <button 
                  onClick={handleChat}
                  className="p-2 bg-mnemo-secondary rounded-full hover:scale-110 transition-transform"
                >
                  <Search className="w-5 h-5 text-white" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                {chatAnswer ? (
                  <div className="space-y-4">
                    <p className="text-zinc-300 leading-relaxed italic">"{chatAnswer}"</p>
                    {sources.length > 0 && (
                      <div className="pt-4 border-t border-zinc-800">
                        <p className="text-[10px] uppercase text-zinc-600 font-bold mb-2">Based on memories:</p>
                        <ul className="space-y-1">
                          {sources.map((s, i) => (
                            <li key={i} className="text-[11px] text-zinc-500 truncate">• {s}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-zinc-700">
                    <Brain className="w-12 h-12 mb-2 opacity-10" />
                    <p className="text-xs italic">Waiting for query...</p>
                  </div>
                )}
              </div>
            </div>
          </section>
        </div>

        {/* Memory Stream Section */}
        <section className="space-y-6">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-zinc-400">
              <Clock className="w-4 h-4" />
              <h2 className="text-xs font-bold uppercase tracking-widest">Memory Stream</h2>
            </div>
            <button 
              onClick={fetchMemories}
              className="text-zinc-600 hover:text-mnemo-primary transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {memories.length > 0 ? (
              memories.map((m) => (
                <div key={m.id} className="group bg-mnemo-card/50 border border-zinc-800/50 p-4 rounded-2xl hover:border-zinc-700 transition-all">
                  <div className="flex justify-between items-start gap-4">
                    <p className="text-sm text-zinc-400 leading-relaxed line-clamp-2">{m.content}</p>
                    <button 
                      onClick={() => handleDelete(m.id)}
                      className="opacity-0 group-hover:opacity-100 p-2 text-zinc-600 hover:text-red-500 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="mt-3 flex items-center gap-3">
                    <span className="text-[10px] px-2 py-0.5 bg-zinc-900 border border-zinc-800 rounded text-zinc-500 uppercase font-bold tracking-tighter">
                      {m.metadata.category || 'Fragment'}
                    </span>
                    <span className="text-[9px] text-zinc-700 font-mono">
                      {m.metadata.timestamp ? new Date(m.metadata.timestamp).toLocaleDateString() : 'Historical'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-2 text-center py-12 border border-dashed border-zinc-800 rounded-3xl">
                <p className="text-zinc-700 text-xs italic uppercase tracking-widest">No memories indexed in the archive yet.</p>
              </div>
            )}
          </div>
        </section>
      </main>

      <footer className="max-w-4xl mx-auto mt-20 pb-12 pt-8 border-t border-zinc-900 text-center text-zinc-600 text-[10px] tracking-widest uppercase font-medium">
        Encrypted | Local-First | Eternal Preservation
      </footer>
    </div>
  );
}

export default App;

export default App;
