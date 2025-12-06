import { useState } from 'react';
import {
    createColumnHelper,
    flexRender,
    getCoreRowModel,
    useReactTable,
    getSortedRowModel,
    type SortingState
} from '@tanstack/react-table';
import { ArrowUpDown, RefreshCw, ShieldCheck } from 'lucide-react';
import { cn } from '../lib/utils';

// Types
type Stock = {
    code: string;
    name: string;
    price: number;
    volatility: number;
    cagr: number;
    grade: 'A' | 'B' | 'C';
}

const defaultData: Stock[] = [
    { code: '2330', name: 'TSMC', price: 580, volatility: 18.5, cagr: 15.2, grade: 'A' },
    { code: '2412', name: 'Chunghwa Telecom', price: 120, volatility: 8.2, cagr: 4.5, grade: 'A' },
    { code: '0050', name: 'Yuanta 50', price: 135, volatility: 14.1, cagr: 9.8, grade: 'A' },
    { code: '2303', name: 'UMC', price: 48, volatility: 25.4, cagr: 8.1, grade: 'B' },
    { code: '2317', name: 'Hon Hai', price: 105, volatility: 21.0, cagr: 6.5, grade: 'B' },
];

const columnHelper = createColumnHelper<Stock>();

const columns = [
    columnHelper.accessor('code', {
        header: 'Code',
        cell: info => <span className="font-mono font-bold text-slate-700">{info.getValue()}</span>,
    }),
    columnHelper.accessor('name', {
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
    columnHelper.accessor('volatility', {
        header: 'Volatility (%)',
        cell: info => {
            const val = info.getValue();
            return (
                <span className={cn(
                    "px-2 py-1 rounded-full text-xs font-semibold",
                    val < 15 ? "bg-green-100 text-green-700" :
                        val < 25 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
                )}>
                    {val.toFixed(1)}%
                </span>
            )
        },
    }),
    columnHelper.accessor('cagr', {
        header: 'CAGR (%)',
        cell: info => `${info.getValue().toFixed(1)}%`,
    }),
];

export default function MarsStrategy() {
    const [data] = useState(() => [...defaultData]);
    const [sorting, setSorting] = useState<SortingState>([]);

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
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors">
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh Analysis</span>
                </button>
            </header>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-sm font-medium text-slate-500">Portfolio Volatility</h3>
                    <p className="text-2xl font-bold text-slate-900 mt-2">12.4%</p>
                    <div className="flex items-center gap-2 mt-4 text-green-600 text-sm">
                        <ShieldCheck className="w-4 h-4" />
                        <span>Extremely Stable</span>
                    </div>
                </div>
            </div>

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
                        {table.getRowModel().rows.map(row => (
                            <tr key={row.id} className="hover:bg-slate-50 transition-colors">
                                {row.getVisibleCells().map(cell => (
                                    <td key={cell.id} className="px-6 py-4 text-sm text-slate-600">
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
