import { test, expect } from '@playwright/test';
const fs = require('fs');

test('Check Group 2 Targets', async ({ page, context }) => {
    // Inject auth state from existing storage if any, or just login
    // Actually, I can use the existing global auth state if the playwight suite uses one.
    // Let's just monitor console output.
    page.on('console', msg => {
        console.log(`[Browser Console ${msg.type()}]`, msg.text());
    });
    page.on('pageerror', err => {
        console.log(`[Browser Uncaught Error]`, err.message);
    });
    page.on('requestfailed', request => {
        console.log(`[Browser Request Failed]`, request.url(), request.failure().errorText);
    });
    
    // We navigate to /portfolio. We'll be "guest" unless we hook up login.
    // If we're guest, we still get groups. Does Guest Group 2 load?!
    await page.goto('http://localhost:3000/portfolio');
    await page.waitForTimeout(1000);
    
    // Wait for group loading
    await page.waitForSelector('button >> text="Bond"'); // Group 2
    
    // Click it
    const group2Btn = page.getByRole('button', { name: "Bond" });
    if(await group2Btn.count() > 0) {
        console.log("Clicking Group 2...");
        await group2Btn.first().click();
        await page.waitForTimeout(2000);
        
        // Wait and see if there are any errors or if targets length > 0
        const html = await page.innerHTML('body');
        if(html.includes('No assets in this group yet')) {
            console.log("Empty assets message found!");
        } else {
            console.log("Assets rendered!");
        }
    } else {
        console.log("Group 2 button not found!");
    }
});
