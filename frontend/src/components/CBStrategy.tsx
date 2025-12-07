import { useState } from 'react';
import { Calculator, TrendingUp, Info } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';
import axios from 'axios';



export default function CBStrategy() {
    const [cbPrice, setCbPrice] = useState(105.0);
    const [stockPrice, setStockPrice] = useState(100.0);
    const [convPrice, setConvPrice] = useState(95.0);

    const [result, setResult] = useState<{
        premium_rate: number;
        signal: string;
        action: string;
        detail: string;
        color: string;
    } | null>(null);

    const handleCalculate = async () => {
        try {
            const resp = await axios.post('http://localhost:8000/api/cb/evaluate', {
                cb_price: cbPrice,
                stock_price: stockPrice,
                conversion_price: convPrice
            });
            setResult(resp.data);
        } catch (err) {
            console.error("API Error", err);
        }
    };

    // Initial calculation on component mount
    useState(() => {
        handleCalculate();
    });


    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <header>
                <h2 className="text-3xl font-bold text-slate-900">CB Arbitrage Calculator</h2>
                <p className="text-slate-500 mt-1">Convertible Bond real-time signal evaluator (Powered by FastAPI).</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Input Form */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 space-y-6">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-blue-600" />
                        Market Data
                    </h3>

                    <div className="space-y-4">
                        <InputGroup label="CB Market Price" value={cbPrice} onChange={(v) => { setCbPrice(v); handleCalculate(); }} unit="$" />
                        <InputGroup label="Stock Market Price" value={stockPrice} onChange={(v) => { setStockPrice(v); handleCalculate(); }} unit="$" />
                        <InputGroup label="Conversion Price" value={convPrice} onChange={(v) => { setConvPrice(v); handleCalculate(); }} unit="$" />
                    </div>

                    <div className="pt-4 border-t border-slate-100">
                        <div className="flex justify-between text-sm">
                            <button
                                onClick={handleCalculate}
                                className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                            >
                                Analyze via API
                            </button>
                        </div>
                        {result && (
                            <div className="flex justify-between text-sm mt-4">
                                <span className="text-slate-500">Premium Rate (I2)</span>
                                <span className={cn("font-mono font-bold", result.premium_rate < 0 ? "text-red-600" : "text-green-600")}>
                                    {result.premium_rate.toFixed(2)}%
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Signal Card */}
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={result.signal}
                        className={cn(
                            "rounded-xl p-8 flex flex-col justify-between text-white shadow-xl transition-colors duration-500",
                            // Map API color names to Tailwind classes if needed, or use inline styles if API sends hex.
                            // API sends: 'red', 'orange', 'green', 'blue', 'purple', 'slate-900'
                            // We need to map them or trust they match tailwind standard colors? 
                            // The API sends simple names (e.g. 'orange'). Tailwind needs 'bg-orange-500'.
                            `bg-${result.color === 'slate-900' ? 'slate-900' : result.color + '-500'}`
                        )}
                    >
                        <div>
                            <div className="flex items-center gap-2 text-white/80 uppercase text-xs font-bold tracking-wider mb-2">
                                Signal
                            </div>
                            <h2 className="text-5xl font-extrabold tracking-tight">{result.signal}</h2>
                            <p className="text-xl mt-2 font-medium opacity-90">{result.action}</p>
                        </div>

                        <div className="mt-8 pt-6 border-t border-white/20">
                            <div className="flex items-start gap-3">
                                <Info className="w-5 h-5 mt-0.5 opacity-80" />
                                <p className="text-sm leading-relaxed opacity-90">
                                    {result.detail}
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}
            </div>

            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 flex gap-3 text-blue-800 text-sm">
                <TrendingUp className="w-5 h-5 shrink-0" />
                <p>
                    <strong>Pro Tip:</strong> When Premium Rate is negative, it's a "Free Lunch" (Arbitrage).
                    When &gt; 30%, the bond behaves purely like an overvalued stock.
                </p>
            </div>
        </div>
    );
}

function InputGroup({ label, value, onChange, unit }: {
    label: string,
    value: number,
    onChange: (v: number) => void,
    unit: string
}) {
    return (
        <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
            <div className="relative">
                <input
                    type="number"
                    value={value}
                    onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all font-mono text-slate-900"
                />
                <span className="absolute right-3 top-2 text-slate-400 text-sm">{unit}</span>
            </div>
        </div>
    )
}
