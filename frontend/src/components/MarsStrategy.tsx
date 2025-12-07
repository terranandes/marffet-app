import { useState } from 'react';
import {
    createColumnHelper,
    flexRender,
    getCoreRowModel,
    useReactTable,
    getSortedRowModel,
    type SortingState
} from '@tanstack/react-table';
import { ArrowUpDown, RefreshCw, ShieldCheck, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import axios from 'axios';

// Types
type Stock = {
    stock_code: string;
    stock_name: string;
    price: number;
    volatility_pct: number;
    cagr_pct: number;
    // grade: 'A' | 'B' | 'C'; // API doesn't return grade yet
}

const columnHelper = createColumnHelper<Stock>();

const columns = [
    columnHelper.accessor('stock_code', {
        header: 'Code',
        cell: info => <span className="font-mono font-bold text-slate-700">{info.getValue()}</span>,
    }),
    columnHelper.accessor('stock_name', {
        header: 'Name',
        cell: info => info.getValue(),
    }),
    columnHelper.accessor('price', {
        header: ({ column }) => {
            return (
                <button
                    className="flex items-center gap-1 hover:text-slate-900"
                    onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
                >
                    Price
                    <ArrowUpDown className="w-4 h-4" />
                </button>
            )
        },
        cell: info => `$${info.getValue().toFixed(2)}`,
    }),
    columnHelper.accessor('volatility_pct', {
        header: 'Volatility (%)',
        cell: info => {
            const val = info.getValue();
            return (
                <span className={cn(
                    "px-2 py-1 rounded-full text-xs font-semibold",
                    val < 15 ? "bg-green-100 text-green-700" :
                        val < 25 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
                )}>
                    {val ? val.toFixed(1) : 'N/A'}%
                </span>
            )
        },
    }),
    columnHelper.accessor('cagr_pct', {
        header: 'CAGR (%)',
        cell: info => {
            const val = info.getValue();
            return val ? `${val.toFixed(1)}%` : 'N/A';
        },
    }),
];

export default function MarsStrategy() {
    const [data, setData] = useState<Stock[]>([]);
    const [loading, setLoading] = useState(false);
    const [sorting, setSorting] = useState<SortingState>([]);
    const [error, setError] = useState('');

    const handleAnalyze = async () => {
        setLoading(true);
        setError('');
        try {
            // Demo Payload - In real app, inputs would come from user
            const payload = {
                stock_codes: ['2330', '2317', '2454', '2412', '0050', '2303', '2881', '2882'],
                start_year: 2023,
                end_year: 2024
            };

            const resp = await axios.post('http://localhost:8000/api/mars/analyze', payload);
            setData(resp.data.results);
        } catch (err) {
            console.error(err);
            setError('Failed to fetch analysis data. Ensure backend is running.');
        } finally {
            setLoading(false);
        }
    };

    const table = useReactTable({
        data,
        columns,
        state: { sorting },
        onSortingChange: setSorting,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
    });

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900">Mars Strategy Portfolio</h2>
                    <p className="text-slate-500 mt-1">Low volatility stocks selected by Gaussian filtering.</p>
                </div>
                <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    <span>{loading ? 'Analyzing...' : 'Refresh Analysis'}</span>
                </button>
            </header>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-sm font-medium text-slate-500">Portfolio Volatility</h3>
                    <p className="text-2xl font-bold text-slate-900 mt-2">
                        {data.length > 0 ? (data.reduce((acc, curr) => acc + curr.volatility_pct, 0) / data.length).toFixed(1) : '--'}%
                    </p>
                    <div className="flex items-center gap-2 mt-4 text-green-600 text-sm">
                        <ShieldCheck className="w-4 h-4" />
                        <span>Extremely Stable</span>
                    </div>
                </div>
            </div>

            {error && (
                <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm">
                    {error}
                </div>
            )}

            {/* Table */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-slate-50 border-b border-slate-200">
                        {table.getHeaderGroups().map(headerGroup => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map(header => (
                                    <th key={header.id} className="px-6 py-4 text-sm font-semibold text-slate-600">
                                        {header.isPlaceholder
                                            ? null
                                            : flexRender(
                                                header.column.columnDef.header,
                                                header.getContext()
                                            )}
                                    </th>
                                ))}
                            </tr>
                        ))}
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {table.getRowModel().rows.length > 0 ? (
                            table.getRowModel().rows.map(row => (
                                <tr key={row.id} className="hover:bg-slate-50 transition-colors">
                                    {row.getVisibleCells().map(cell => (
                                        <td key={cell.id} className="px-6 py-4 text-sm text-slate-600">
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan={columns.length} className="px-6 py-8 text-center text-slate-400">
                                    {loading ? 'Calculating metrics...' : 'No data available. Click "Refresh Analysis" to start.'}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
