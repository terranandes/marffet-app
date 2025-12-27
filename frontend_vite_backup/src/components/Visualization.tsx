import { useState } from 'react';
import Plot from 'react-plotly.js';
import { Play, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function Visualization() {
    const [data, setData] = useState<any[]>([]);
    const [layout, setLayout] = useState<any>({});
    const [frames, setFrames] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const loadRace = async () => {
        setLoading(true);
        setError('');
        try {
            // Payload: Request smart candidates
            const payload = {
                stock_codes: ['MARS_TOP50'],
                start_year: 2006,
                end_year: 2025
            };
            const resp = await axios.post('/api/data/race', payload, {
                timeout: 300000 // 5 minutes
            });

            // Plotly JSON from backend has { data: [], layout: {}, frames: [] }
            setData(resp.data.data);
            setLayout(resp.data.layout);
            setFrames(resp.data.frames);

        } catch (err) {
            console.error(err);
            setError('Failed to load visualization. Ensure backend is running.');
        } finally {
            setLoading(false);
        }
    };

    // Load once automatically or via button? Let's use button for control
    // useEffect(() => { loadRace(); }, []);

    return (
        <div className="space-y-6 h-full flex flex-col">
            <header className="flex items-center justify-between shrink-0">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900">Market Visualization</h2>
                    <p className="text-slate-500 mt-1">Dynamic Bar Chart Race (Cumulative ROI).</p>
                </div>
                <button
                    onClick={loadRace}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    <span>{loading ? 'Generating...' : 'Start Race'}</span>
                </button>
            </header>

            {error && (
                <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm shrink-0">
                    {error}
                </div>
            )}

            <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex-1 min-h-[500px] relative">
                {data.length > 0 ? (
                    <Plot
                        data={data}
                        layout={{ ...layout, autosize: true }}
                        frames={frames}
                        style={{ width: '100%', height: '100%' }}
                        useResizeHandler={true}
                        config={{ responsive: true }}
                    />
                ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-slate-400">
                        {loading ? 'Fetching data & generating animation lines...' : 'Click "Start Race" to begin visualization.'}
                    </div>
                )}
            </div>
        </div>
    );
}
