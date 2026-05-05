import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Search, Sparkles, Clock, MapPin, Trash2, RefreshCw, Shield, Zap, Database, ArrowUpRight, Github, LayoutGrid, Image as ImageIcon, CheckCircle2, Mic, MicOff, Edit3 } from 'lucide-react';
import { useReactMediaRecorder } from 'react-media-recorder-2';

interface Memory {
  id: string;
  content: string;
  metadata: any;
  base64_content?: string;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { type: 'spring', stiffness: 100 }
  }
};

function App() {
  const [content, setContent] = useState('');
  const [query, setQuery] = useState('');
  const [chatAnswer, setChatAnswer] = useState('');
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [encryptionKey, setEncryptionKey] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessSuccessMessage] = useState('Neural Fragment Synchronized');

  const getHeaders = () => {
    return encryptionKey ? { 'X-Encryption-Key': encryptionKey } : {};
  };

  const triggerSuccess = (msg?: string) => {
    setSuccessSuccessMessage(msg || 'Neural Fragment Synchronized');
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleVoiceUpload = async (blobUrl: string) => {
    setLoading(true);
    try {
      const blob = await fetch(blobUrl).then(r => r.blob());
      const formData = new FormData();
      const audioFile = new File([blob], "voice_memory.wav", { type: "audio/wav" });
      formData.append('file', audioFile);
      
      const response = await axios.post('/api/transcribe', formData, { 
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000 
      });
      
      if (response.data.status === 'success') {
        setContent(response.data.transcript);
        triggerSuccess('Voice Transcribed - Review and Commit');
      } else {
        alert('Transcription Error: ' + response.data.message);
      }
    } catch (err: any) {
      console.error("Transcription Failed:", err);
      alert('Voice Processing Failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const {
    status,
    startRecording,
    stopRecording,
  } = useReactMediaRecorder({ 
    audio: true,
    onStop: (blobUrl) => {
      if (blobUrl) handleVoiceUpload(blobUrl);
    }
  });

  const fetchMemories = async () => {
    try {
      const res = await axios.get('/api/memories', { headers: getHeaders() });
      setMemories(res.data);
    } catch (err) {
      console.error('Failed to fetch memories', err);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [encryptionKey]);

  const handleIngest = async () => {
    if (!content) return;
    setLoading(true);
    try {
      await axios.post('/api/ingest', 
        { content, metadata: { location: "Local Browser" } },
        { headers: getHeaders() }
      );
      setContent('');
      triggerSuccess('Memory Archived Successfully');
      fetchMemories();
    } catch (err) {
      console.error(err);
      alert('Encoding Failed');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post('/api/ingest/image', formData, { 
        headers: { ...getHeaders(), 'Content-Type': 'multipart/form-data' } 
      });
      triggerSuccess('Visual Memory Archived');
      fetchMemories();
    } catch (err) {
      console.error(err);
      alert('Visual Encoding Failed');
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
      const res = await axios.post('/api/chat', 
        { message: query },
        { headers: getHeaders() }
      );
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
    <div className="min-h-screen p-4 md:p-8 lg:p-12 overflow-x-hidden">
      <AnimatePresence>
        {showSuccess && (
          <motion.div 
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-8 left-1/2 -translate-x-1/2 z-50 bg-blue-600 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3 font-black uppercase text-[10px] tracking-widest"
          >
            <CheckCircle2 className="w-4 h-4" />
            {successMessage}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        className="max-w-7xl mx-auto space-y-8"
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        {/* Header Bento */}
        <motion.header className="grid grid-cols-1 md:grid-cols-12 gap-6" variants={itemVariants}>
          <div className="md:col-span-8 bento-card">
            <div className="bento-inner flex-row items-center justify-between">
              <div className="flex items-center gap-6">
                <motion.div 
                  className="bg-blue-600/20 p-4 rounded-3xl border border-blue-500/20"
                  whileHover={{ rotate: 15, scale: 1.1 }}
                >
                  <Brain className="w-8 h-8 text-blue-500" />
                </motion.div>
                <div>
                  <h1 className="text-3xl font-black tracking-tighter">MNEMOSYNE</h1>
                  <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-[0.2em]">Neural Core v0.5.0-REVIEW-LOOP</p>
                </div>
              </div>
              <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white/5 rounded-2xl border border-white/5">
                <Edit3 className="w-4 h-4 text-zinc-500" />
                <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Cognitive Review Active</span>
              </div>
            </div>
          </div>
          <div className="md:col-span-4 bento-card">
            <div className="bento-inner justify-center">
              <div className="flex items-center gap-4">
                <div className="flex flex-col flex-1">
                  <span className="text-[9px] text-zinc-500 font-black uppercase mb-1">Neural Lock</span>
                  <input 
                    type="password"
                    value={encryptionKey}
                    onChange={(e) => setEncryptionKey(e.target.value)}
                    placeholder="UNSECURED"
                    className="bg-transparent text-sm text-white focus:outline-none font-mono placeholder:text-red-500/30"
                  />
                </div>
                <motion.div 
                  className={`p-3 rounded-2xl ${encryptionKey ? 'bg-blue-500/10 text-blue-500' : 'bg-red-500/10 text-red-500'}`}
                  animate={{ scale: encryptionKey ? [1, 1.1, 1] : 1 }}
                  transition={{ repeat: encryptionKey ? Infinity : 0, duration: 2 }}
                >
                  <Shield className="w-5 h-5" />
                </motion.div>
              </div>
            </div>
          </div>
        </motion.header>

        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 auto-rows-[minmax(300px,auto)]">
          {/* Ingestion Tile */}
          <motion.section className="md:col-span-7 bento-card" variants={itemVariants}>
            <div className="bento-inner">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-500" />
                  <h2 className="text-xs font-black uppercase tracking-widest text-zinc-400">Ingestion</h2>
                </div>
                <span className="text-[9px] px-2 py-1 bg-white/5 rounded-lg text-zinc-600 font-bold uppercase tracking-tighter">
                  {status === 'recording' ? 'Listening...' : (loading ? 'Processing...' : 'Ready')}
                </span>
              </div>
              <textarea 
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Transcribe or type your thoughts..."
                className="flex-1 bg-transparent border-none focus:ring-0 text-2xl font-light leading-relaxed resize-none placeholder:text-zinc-800 text-white custom-scrollbar mb-6"
              />
              <div className="flex items-center justify-between">
                <div className="flex gap-4">
                  {/* Voice Record Button */}
                  <button 
                    onClick={status === 'recording' ? stopRecording : startRecording}
                    disabled={loading}
                    className={`p-3 rounded-2xl border transition-all duration-500 flex items-center justify-center ${status === 'recording' ? 'bg-red-500/20 border-red-500/50 text-red-500 animate-pulse' : (loading ? 'bg-white/5 border-white/5 text-zinc-800' : 'bg-white/5 border-white/5 text-zinc-600 hover:text-white')}`}
                  >
                    {status === 'recording' ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </button>

                  <label className={`p-3 rounded-2xl border transition-colors cursor-pointer flex items-center justify-center ${loading ? 'bg-white/5 border-white/5 text-zinc-800 pointer-events-none' : 'bg-white/5 border-white/5 text-zinc-600 hover:text-white'}`}>
                    <ImageIcon className="w-4 h-4" />
                    <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} disabled={loading} />
                  </label>
                  <div className="p-3 bg-white/5 rounded-2xl border border-white/5 text-zinc-600 hover:text-white transition-colors cursor-pointer">
                    <MapPin className="w-4 h-4" />
                  </div>
                </div>
                <motion.button 
                  onClick={handleIngest}
                  disabled={loading || !content}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="bg-blue-600 hover:bg-blue-500 disabled:opacity-20 text-white px-8 py-4 rounded-3xl font-black uppercase text-[10px] tracking-widest transition-all shadow-xl shadow-blue-900/20 flex items-center gap-2"
                >
                  {loading ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                      <RefreshCw className="w-4 h-4" />
                    </motion.div>
                  ) : (
                    <>Commit Memory <ArrowUpRight className="w-4 h-4" /></>
                  )}
                </motion.button>
              </div>
            </div>
          </motion.section>

          {/* AI/Retreival Tile */}
          <motion.section className="md:col-span-5 bento-card" variants={itemVariants}>
            <div className="bento-inner">
              <div className="flex items-center gap-2 mb-6">
                <Search className="w-4 h-4 text-purple-500" />
                <h2 className="text-xs font-black uppercase tracking-widest text-zinc-400">Synthesis</h2>
              </div>
              <div className="relative mb-6">
                <input 
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Query your archive..."
                  className="w-full bg-white/5 border border-white/5 rounded-2xl px-6 py-4 focus:outline-none focus:border-purple-500/50 transition-all text-white"
                />
                <button 
                  onClick={handleChat}
                  disabled={loading || !query}
                  className="absolute right-2 top-2 bottom-2 aspect-square bg-purple-600 hover:bg-purple-500 rounded-xl flex items-center justify-center transition-all disabled:opacity-20"
                >
                  {loading ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                      <RefreshCw className="w-4 h-4 text-white" />
                    </motion.div>
                  ) : (
                    <Search className="w-4 h-4 text-white" />
                  )}
                </button>
              </div>
              <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                {chatAnswer ? (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="space-y-4"
                  >
                    <div className="p-5 bg-purple-500/10 border border-purple-500/10 rounded-[1.5rem]">
                      <p className="text-zinc-300 text-sm leading-relaxed font-light italic">"{chatAnswer}"</p>
                    </div>
                    {sources.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {sources.map((s, i) => (
                          <span key={i} className="px-3 py-1 bg-white/5 border border-white/5 rounded-lg text-[9px] text-zinc-600 font-bold uppercase truncate max-w-[150px]">
                            {s === '[Visual Memory]' ? 'Visual Fragment' : `Fragment ${i + 1}`}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-zinc-800 space-y-4">
                    <div className="p-6 bg-white/[0.02] rounded-full">
                      <Zap className="w-8 h-8 opacity-10" />
                    </div>
                    <p className="text-[9px] font-black uppercase tracking-[0.2em] opacity-40 italic">Awaiting Request</p>
                  </div>
                )}
              </div>
            </div>
          </motion.section>

          {/* Stream Tile (Long) */}
          <motion.section className="md:col-span-12 lg:col-span-12 bento-card" variants={itemVariants}>
            <div className="bento-inner">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-zinc-500" />
                  <h2 className="text-xs font-black uppercase tracking-widest text-zinc-400">Neural Stream</h2>
                </div>
                <motion.button 
                  onClick={fetchMemories}
                  whileHover={{ rotate: 180 }}
                  transition={{ duration: 0.5 }}
                  className="p-3 bg-white/5 rounded-2xl border border-white/5 text-zinc-500 transition-all"
                >
                  <RefreshCw className="w-4 h-4" />
                </motion.button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 overflow-y-auto pr-2 custom-scrollbar">
                {memories.length > 0 ? (
                  memories.map((m) => (
                    <motion.div 
                      key={m.id} 
                      layout
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="group relative p-4 bg-white/[0.02] border border-white/5 rounded-3xl hover:bg-white/[0.04] hover:border-white/10 transition-all h-[240px] flex flex-col"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className={`w-2 h-2 rounded-full ${m.metadata.is_encrypted ? 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]' : 'bg-zinc-800'}`}></div>
                        <button 
                          onClick={() => handleDelete(m.id)}
                          className="opacity-0 group-hover:opacity-100 p-2 text-zinc-700 hover:text-red-500 transition-all"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      
                      {m.base64_content ? (
                        <div className="flex-1 mb-3 overflow-hidden rounded-2xl border border-white/5">
                          <img 
                            src={`data:image/png;base64,${m.base64_content}`} 
                            alt="Visual Memory" 
                            className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
                          />
                        </div>
                      ) : (
                        <p className="flex-1 text-sm text-zinc-400 font-light line-clamp-5 mb-3 group-hover:text-zinc-200 transition-colors">
                          {m.content}
                        </p>
                      )}

                      <div className="flex items-center justify-between mt-auto">
                        <span className="text-[9px] font-black uppercase text-zinc-700 tracking-widest">{m.metadata.is_image ? 'Visual' : (m.metadata.source === 'voice' ? 'Voice' : (m.metadata.category || 'Fragment'))}</span>
                        <span className="text-[9px] font-mono text-zinc-800">
                          {m.metadata.timestamp ? new Date(m.metadata.timestamp).toLocaleDateString() : 'Historical'}
                        </span>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="col-span-full py-20 text-center border-2 border-dashed border-white/5 rounded-[2.5rem]">
                    <p className="text-zinc-800 text-[10px] font-black uppercase tracking-[0.4em]">Neural Core Standby</p>
                  </div>
                )}
              </div>
            </div>
          </motion.section>
        </div>

        {/* Footer Bento */}
        <motion.footer className="grid grid-cols-1 md:grid-cols-3 gap-6" variants={itemVariants}>
          <div className="bento-card">
            <div className="bento-inner py-4 flex-row items-center gap-4">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
              <span className="text-[9px] font-black uppercase text-zinc-600 tracking-widest">Multi-Modal Sync Active</span>
            </div>
          </div>
          <div className="bento-card">
            <div className="bento-inner py-4 items-center">
              <span className="text-[9px] font-black uppercase text-zinc-800 tracking-[0.5em]">Mnemosyne &copy; 2026</span>
            </div>
          </div>
          <div className="bento-card">
            <div className="bento-inner py-4 flex-row items-center justify-center gap-8 text-[9px] font-black uppercase text-zinc-700 tracking-widest">
              <span className="hover:text-white transition-colors cursor-pointer">Terms</span>
              <span className="hover:text-white transition-colors cursor-pointer">Privacy</span>
              <Github className="w-4 h-4" />
            </div>
          </div>
        </motion.footer>
      </motion.div>
    </div>
  );
}

export default App;
