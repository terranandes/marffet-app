import { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

export default function Visualization() {
    const [data, setData] = useState<any[]>([]);
    const [layout, setLayout] = useState<any>({});
    const [frames, setFrames] = useState<any[]>([]);

    // Generate Demo Data (Client-side for now)
    const generateRace = () => {
        // Should be moved to backend/plot_race.py logic later
        // Dummy Plotly Animation structure
        const years = ['2019', '2020', '2021', '2022', '2023'];
        const x1 = [10, 40, 60, 80, 100];
        const x2 = [20, 30, 50, 70, 90];

        // Base trace
        // const pad = {x: x1[0], y: 'TSMC', type: 'bar', orientation: 'h'};

        setData([
            { x: [x1[0]], y: ['TSMC'], type: 'bar', orientation: 'h', name: 'TSMC' },
            { x: [x2[0]], y: ['UMC'], type: 'bar', orientation: 'h', name: 'UMC' }
        ]);

        setLayout({
            title: 'Stock ROI Race (Demo)',
            xaxis: { title: 'ROI (%)', range: [0, 120] },
            yaxis: { title: 'Stock' },
            updatemenus: [{
                type: 'buttons',
                buttons: [{
                    label: 'Play',
                    method: 'animate',
                    args: [null, { frame: { duration: 500, redraw: true }, fromcurrent: true }]
                }]
            }]
        });

        const frs = years.map((yr, i) => ({
            name: yr,
            data: [
                { x: [x1[i]], y: ['TSMC'] },
                { x: [x2[i]], y: ['UMC'] }
            ]
        }));

        setFrames(frs);
    };

    useEffect(() => {
        generateRace();
    }, []);

    return (
        <div className="space-y-6 h-full">
            <header>
                <h2 className="text-3xl font-bold text-slate-900">Market Visualization</h2>
                <p className="text-slate-500 mt-1">Interactive analysis powered by Plotly.</p>
            </header>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 h-[600px]">
                {data.length > 0 && (
                    <Plot
                        data={data}
                        layout={layout}
                        frames={frames}
                        style={{ width: '100%', height: '100%' }}
                        useResizeHandler={true}
                    />
                )}
            </div>
        </div>
    );
}
