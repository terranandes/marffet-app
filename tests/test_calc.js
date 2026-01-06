const calculateWealthPath = (stockId, startYear, principal, annualContrib) => {
    // Mock History: 5% annual growth every year for 20 years
    // This roughly matches 2.6M from 1M+60k/yr
    const history = [];
    let cum = 1.0;
    for (let y = 2006; y <= 2026; y++) {
        cum = cum * 1.05; // 5% growth
        history.push({ year: y, id: stockId, roi: 5.0 }); // ROI is annual here? Or logic uses accum?
        // Logic in main.js: getCum = (1 + roi/100). 
        // Then annualFactor = cumCur / cumPrev.
        // So 'roi' in data should be CUMULATIVE for the logic `cumCur / cumPrev` to work as "Annual Change".
        // Wait, if data has 'roi' as ANNUAL. 
        // cumCur = 1 + 0.05 = 1.05.
        // cumPrev = 1 + 0.05 = 1.05.
        // annualFactor = 1.05 / 1.05 = 1.0. (0% growth).
        // THIS IS THE BUG!
    }

    // Let's test the hypothesis:
    // If main.js treats 'roi' as Cumulative Factor (1.x), but data provides Annual ROI (5%).

    // Mocking Data structure from main.js logic:
    // const getCum = (record) => record ? (1 + record.roi / 100) : 1.0;

    // If real data 'roi' is Annual Return (e.g. 5.0).
    // Year 2006: roi=5. cumCur=1.05.
    // Year 2005: roi=undef. cumPrev=1.0.
    // Factor = 1.05. (5% growth). Correct for year 1.

    // Year 2007: roi=5. cumCur=1.05.
    // Year 2006: roi=5. cumPrev=1.05.
    // Factor = 1.0. (0% growth).

    // SO, if raw data provides ANNUAL ROI, the logic `cumCur / cumPrev` cancels it out to 1.0 (flat).

    let wealth = principal;
    let cost = principal;
    const path = [];
    const currentYear = 2026;

    console.log(`Debug Start: Principal=${principal}, Contrib=${annualContrib}`);

    const rawRaceDataValue = history; // Mock

    for (let y = startYear; y <= currentYear; y++) {
        // Mocking the getCum logic from main.js
        const cur = rawRaceDataValue.find(h => h.year === y);
        const prev = rawRaceDataValue.find(h => h.year === y - 1);

        const getCum = (record) => record ? (1 + record.roi / 100) : 1.0;
        const cumCur = getCum(cur);
        const cumPrev = getCum(prev);

        let annualFactor = 1.0;
        if (y === 2006) {
            annualFactor = cumCur;
        } else {
            annualFactor = (cumPrev > 0) ? (cumCur / cumPrev) : 1.0;
        }

        const oldWealth = wealth;
        wealth = wealth * annualFactor;
        wealth += annualContrib;
        cost += annualContrib;

        const yearsElapsed = y - startYear + 1;
        let cagrPct = 0;
        if (yearsElapsed > 0 && principal > 0 && wealth > 0) {
            cagrPct = (Math.pow(wealth / principal, 1 / yearsElapsed) - 1) * 100;
        }

        console.log(`Year ${y}: Factor=${annualFactor.toFixed(4)}, Wealth=${wealth.toFixed(2)}, CAGR=${cagrPct.toFixed(2)}%`);
    }
};

// Run simulation
calculateWealthPath("TEST", 2006, 1000000, 60000);
